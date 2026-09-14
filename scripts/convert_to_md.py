#!/usr/bin/env python3
"""
convert_to_md.py - Markdown & CSV Consolidation and LLM Context Preparation Tool.

Aggregates Markdown (.md) and Spreadsheet (.csv) files from a directory or single file
into structured, well-organized Markdown ready for LLM prompts, context windows,
or RAG document stores.

For CSV files, it automatically recognizes Q&A / FAQ spreadsheets
(columns: category, question, answer, notes) and structures them into semantic,
chunk-friendly Markdown sections. Generic tabular CSVs are converted to clean
Markdown tables.

Usage:
    # Convert a Q&A spreadsheet to a clean Markdown file for RAG ingestion:
    python scripts/convert_to_md.py faq.csv -o faq.md --raw

    # Consolidate a directory of notes and CSVs into an LLM context document:
    python scripts/convert_to_md.py /path/to/docs -o compiled_context.md

    # Dry-run inspection:
    python scripts/convert_to_md.py ./data --dry-run
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import io
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_EXCLUDES = [
    ".git",
    ".github",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".obsidian",
    ".trash",
    ".DS_Store",
]

SUPPORTED_EXTENSIONS = {".md", ".csv"}


@dataclass
class SectionInfo:
    """Represents a Markdown heading section."""
    level: int
    title: str


@dataclass
class MarkdownDoc:
    """Represents a parsed Markdown or CSV-derived document with extracted metadata."""
    file_path: Path
    relative_path: str
    title: str
    frontmatter: Optional[str] = None
    sections: List[SectionInfo] = field(default_factory=list)
    body: str = ""
    word_count: int = 0
    size_bytes: int = 0
    source_type: str = "markdown"


def parse_frontmatter(content: str) -> Tuple[Optional[str], str]:
    """
    Extracts YAML frontmatter (between triple dashes `---`) from markdown content.

    Returns:
        Tuple of (frontmatter_string_or_None, remaining_body_content)
    """
    frontmatter_pattern = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
    match = frontmatter_pattern.match(content)
    if match:
        frontmatter = match.group(1).strip()
        body = content[match.end():]
        return frontmatter, body
    return None, content


def extract_title_from_frontmatter(frontmatter: Optional[str]) -> Optional[str]:
    """Attempts to extract a 'title:' field from YAML frontmatter string."""
    if not frontmatter:
        return None
    for line in frontmatter.splitlines():
        match = re.match(r"^title\s*:\s*[\"']?(.*?)[\"']?\s*$", line, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            if val:
                return val
    return None


def extract_sections_and_title(body: str, fallback_title: str) -> Tuple[str, List[SectionInfo]]:
    """
    Extracts all heading sections (# H1, ## H2, etc.) and determines note title.

    Returns:
        Tuple of (title, list_of_sections)
    """
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    sections: List[SectionInfo] = []
    first_h1_title: Optional[str] = None

    # Track code block state to avoid matching # comments in code blocks
    in_code_block = False
    for line in body.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("```"):
            in_code_block = not in_code_block
            continue

        if not in_code_block:
            match = heading_pattern.match(line)
            if match:
                level = len(match.group(1))
                sec_title = match.group(2).strip()
                # Remove inline markdown link syntax e.g. [text](url) -> text
                clean_sec_title = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", sec_title)
                sections.append(SectionInfo(level=level, title=clean_sec_title))
                if level == 1 and first_h1_title is None:
                    first_h1_title = clean_sec_title

    resolved_title = first_h1_title or fallback_title
    return resolved_title, sections


def parse_markdown_file(file_path: Path, base_dir: Path) -> MarkdownDoc:
    """
    Reads and parses a single markdown file into a MarkdownDoc.
    """
    try:
        relative_path = str(file_path.relative_to(base_dir))
    except ValueError:
        relative_path = file_path.name

    fallback_title = file_path.stem.replace("-", " ").replace("_", " ").title()

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        content = f"[Error reading file {file_path.name}: {e}]"

    size_bytes = len(content.encode("utf-8"))
    word_count = len(content.split())

    frontmatter, body = parse_frontmatter(content)
    fm_title = extract_title_from_frontmatter(frontmatter)

    extracted_title, sections = extract_sections_and_title(body, fallback_title)
    final_title = fm_title if fm_title else extracted_title

    return MarkdownDoc(
        file_path=file_path,
        relative_path=relative_path,
        title=final_title,
        frontmatter=frontmatter,
        sections=sections,
        body=content.strip(),
        word_count=word_count,
        size_bytes=size_bytes,
        source_type="markdown",
    )


def read_file_text_with_fallback(file_path: Path) -> str:
    """Reads file text attempting utf-8-sig (for BOM handling), utf-8, and latin-1."""
    try:
        return file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="latin-1", errors="replace")


def detect_csv_qa_columns(fieldnames: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Identifies column names for category, question, answer, notes (case-insensitive,
    supports compound headers like 'Question / Topic', 'Answer & Details', 'Key Highlights / Notes').
    """
    category_col = None
    question_col = None
    answer_col = None
    notes_col = None

    for col in fieldnames:
        clean = col.strip().lower()
        tokens = set(re.split(r"[^a-z0-9]+", clean))

        if not question_col and (
            clean in {"question", "questions", "q", "prompt", "query"}
            or any(t in tokens for t in ["question", "questions", "prompt", "query"])
        ):
            question_col = col
        elif not answer_col and (
            clean in {"answer", "answers", "a", "response", "completion"}
            or any(t in tokens for t in ["answer", "answers", "response", "completion"])
        ):
            answer_col = col
        elif not category_col and (
            clean in {"category", "categories", "topic", "topics", "section", "group"}
            or any(t in tokens for t in ["category", "categories", "section"])
        ):
            category_col = col
        elif not notes_col and (
            clean in {"notes", "note", "context", "comment", "comments", "details", "highlights"}
            or any(t in tokens for t in ["notes", "note", "highlights", "context", "details"])
        ):
            notes_col = col

    return category_col, question_col, answer_col, notes_col


def format_csv_as_qa(
    rows: List[Dict[str, str]],
    fieldnames: List[str],
    category_col: Optional[str],
    question_col: str,
    answer_col: str,
    notes_col: Optional[str],
    doc_title: str,
) -> str:
    """
    Formats rows as structured, semantic Q&A Markdown cards grouped by category.
    """
    md_lines: List[str] = []
    other_cols = [
        c for c in fieldnames
        if c not in {category_col, question_col, answer_col, notes_col}
    ]

    # Group by category if available, preserving initial appearance order
    grouped: Dict[str, List[Dict[str, str]]] = {}
    for r in rows:
        cat_val = r.get(category_col, "").strip() if category_col else ""
        if not cat_val:
            cat_val = "General" if category_col else ""
        grouped.setdefault(cat_val, []).append(r)

    if category_col:
        md_lines.append(f"# {doc_title} Knowledge Base")
        md_lines.append("")
        for cat_name, cat_rows in grouped.items():
            md_lines.append(f"## Category: {cat_name}")
            md_lines.append("")
            for row in cat_rows:
                q_text = row.get(question_col, "").strip()
                a_text = row.get(answer_col, "").strip()
                n_text = row.get(notes_col, "").strip() if notes_col else ""

                if not q_text and not a_text:
                    continue

                md_lines.append(f"### {q_text or '[Untitled Question]'}")
                md_lines.append(f"**Answer:** {a_text or '*(No answer provided)*'}")
                if n_text and n_text.lower() != "nan":
                    md_lines.append(f"**Notes:** {n_text}")

                for oc in other_cols:
                    val = row.get(oc, "").strip()
                    if val and val.lower() != "nan":
                        md_lines.append(f"- **{oc.strip().title()}:** {val}")

                md_lines.append("")
                md_lines.append("---")
                md_lines.append("")
    else:
        md_lines.append(f"# {doc_title}")
        md_lines.append("")
        for row in rows:
            q_text = row.get(question_col, "").strip()
            a_text = row.get(answer_col, "").strip()
            n_text = row.get(notes_col, "").strip() if notes_col else ""

            if not q_text and not a_text:
                continue

            md_lines.append(f"## {q_text or '[Untitled Question]'}")
            md_lines.append(f"**Answer:** {a_text or '*(No answer provided)*'}")
            if n_text and n_text.lower() != "nan":
                md_lines.append(f"**Notes:** {n_text}")

            for oc in other_cols:
                val = row.get(oc, "").strip()
                if val and val.lower() != "nan":
                    md_lines.append(f"- **{oc.strip().title()}:** {val}")

            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")

    return "\n".join(md_lines).strip()


def format_csv_as_table(
    rows: List[Dict[str, str]],
    fieldnames: List[str],
    doc_title: str,
) -> str:
    """
    Formats rows as a clean Markdown table.
    """
    lines: List[str] = [f"# {doc_title}", ""]

    if not fieldnames or not rows:
        lines.append("_Empty dataset._")
        return "\n".join(lines)

    # Sanitize header
    headers = [c.replace("|", "\\|").replace("\n", " ") for c in fieldnames]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join([":---"] * len(headers)) + " |")

    for row in rows:
        cell_vals = [
            str(row.get(col, "")).replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>").strip()
            for col in fieldnames
        ]
        lines.append("| " + " | ".join(cell_vals) + " |")

    return "\n".join(lines).strip()


def parse_csv_file(file_path: Path, base_dir: Path, csv_mode: str = "auto") -> MarkdownDoc:
    """
    Reads a CSV spreadsheet and converts it into a structured MarkdownDoc.
    Supports auto Q&A detection (category, question, answer, notes) or table mode.
    """
    try:
        relative_path = str(file_path.relative_to(base_dir))
    except ValueError:
        relative_path = file_path.name

    fallback_title = file_path.stem.replace("-", " ").replace("_", " ").title()

    raw_text = read_file_text_with_fallback(file_path)
    size_bytes = len(raw_text.encode("utf-8"))

    # Parse with csv.reader / DictReader
    rows: List[Dict[str, str]] = []
    fieldnames: List[str] = []

    try:
        csv_file = io.StringIO(raw_text)
        reader = csv.DictReader(csv_file)
        if reader.fieldnames:
            fieldnames = [c.strip() for c in reader.fieldnames if c and c.strip()]
            for r in reader:
                # Store non-empty rows
                cleaned_row = {k.strip(): (v.strip() if v else "") for k, v in r.items() if k}
                if any(cleaned_row.values()):
                    rows.append(cleaned_row)
    except Exception as exc:
        err_body = f"# Error Parsing CSV\n\nFailed to parse `{file_path.name}`: {exc}"
        return MarkdownDoc(
            file_path=file_path,
            relative_path=relative_path,
            title=fallback_title,
            body=err_body,
            word_count=len(err_body.split()),
            size_bytes=size_bytes,
            source_type="csv",
        )

    cat_col, q_col, a_col, n_col = detect_csv_qa_columns(fieldnames)
    is_qa_candidate = (q_col is not None and a_col is not None)

    use_qa = (csv_mode == "qa") or (csv_mode == "auto" and is_qa_candidate)

    if use_qa and is_qa_candidate:
        body = format_csv_as_qa(
            rows=rows,
            fieldnames=fieldnames,
            category_col=cat_col,
            question_col=q_col,
            answer_col=a_col,
            notes_col=n_col,
            doc_title=fallback_title,
        )
        resolved_format = "qa"
    else:
        body = format_csv_as_table(
            rows=rows,
            fieldnames=fieldnames,
            doc_title=fallback_title,
        )
        resolved_format = "table"

    extracted_title, sections = extract_sections_and_title(body, fallback_title)
    word_count = len(body.split())

    # Build informative frontmatter metadata
    frontmatter_lines = [
        f"source_file: \"{file_path.name}\"",
        "source_type: \"csv\"",
        f"format: \"{resolved_format}\"",
        f"total_rows: {len(rows)}",
        "columns:",
    ]
    for col in fieldnames:
        frontmatter_lines.append(f"  - \"{col}\"")
    frontmatter = "\n".join(frontmatter_lines)

    return MarkdownDoc(
        file_path=file_path,
        relative_path=relative_path,
        title=extracted_title,
        frontmatter=frontmatter,
        sections=sections,
        body=body,
        word_count=word_count,
        size_bytes=size_bytes,
        source_type="csv",
    )


def parse_source_file(file_path: Path, base_dir: Path, csv_mode: str = "auto") -> MarkdownDoc:
    """Dispatches parsing based on file extension (.md or .csv)."""
    ext = file_path.suffix.lower()
    if ext == ".csv":
        return parse_csv_file(file_path, base_dir, csv_mode=csv_mode)
    return parse_markdown_file(file_path, base_dir)


def should_exclude(path: Path, exclude_patterns: List[str], base_dir: Path) -> bool:
    """
    Checks if a path matches any exclude patterns or default directory excludes.
    """
    try:
        rel_parts = path.relative_to(base_dir).parts
    except ValueError:
        rel_parts = path.parts

    # Check part-based folder exclusions
    for part in rel_parts:
        if part in DEFAULT_EXCLUDES:
            return True
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(part, pattern):
                return True

    # Check filename and full relative path
    rel_path_str = str(path.relative_to(base_dir)) if path.is_relative_to(base_dir) else str(path)
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(rel_path_str, pattern):
            return True

    return False


def collect_source_files(
    input_path: Path,
    recursive: bool = True,
    exclude_patterns: Optional[List[str]] = None,
    allowed_extensions: Optional[set[str]] = None,
) -> List[Path]:
    """
    Finds all supported files (.md, .csv) in the given input path.
    """
    if exclude_patterns is None:
        exclude_patterns = []
    if allowed_extensions is None:
        allowed_extensions = SUPPORTED_EXTENSIONS

    files: List[Path] = []
    if input_path.is_file():
        if input_path.suffix.lower() in allowed_extensions:
            files.append(input_path)
        return files

    if not input_path.is_dir():
        return files

    pattern = "**/*" if recursive else "*"
    for p in input_path.glob(pattern):
        if p.is_file() and p.suffix.lower() in allowed_extensions:
            if not should_exclude(p, exclude_patterns, input_path):
                files.append(p)

    return files


# Backward-compatibility alias
collect_markdown_files = collect_source_files


def generate_compiled_markdown(
    docs: List[MarkdownDoc],
    source_path: Path,
    include_toc: bool = True,
) -> str:
    """
    Generates a structured, unified markdown document from parsed documents.
    """
    total_docs = len(docs)
    total_words = sum(d.word_count for d in docs)
    total_bytes = sum(d.size_bytes for d in docs)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines: List[str] = []

    # LLM Context Header
    lines.append("# Compiled Markdown Knowledge Base")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(f"> **Generated at**: {timestamp}  ")
    lines.append(f"> **Source Root**: `{source_path.resolve()}`  ")
    lines.append(f"> **Total Documents**: {total_docs}  ")
    lines.append(f"> **Total Word Count**: {total_words:,} words  ")
    lines.append(f"> **Total Size**: {total_bytes / 1024:.2f} KB")
    lines.append("")
    lines.append("This document contains consolidated knowledge files organized with clear file metadata, note titles, and structural section outlines for LLM ingestion.")
    lines.append("")

    # Table of Contents
    if include_toc and total_docs > 0:
        lines.append("---")
        lines.append("## Table of Contents")
        lines.append("")
        lines.append("| Index | Note Title | Type | File Path | Sections | Words |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for idx, doc in enumerate(docs, 1):
            sections_count = len(doc.sections)
            sanitized_title = doc.title.replace("|", "\\|")
            sanitized_path = doc.relative_path.replace("|", "\\|")
            anchor = f"#doc-{idx}-{re.sub(r'[^a-zA-Z0-9_-]', '-', doc.title.lower()).strip('-')}"
            lines.append(f"| {idx} | [{sanitized_title}]({anchor}) | `{doc.source_type.upper()}` | `{sanitized_path}` | {sections_count} | {doc.word_count:,} |")
        lines.append("")

    lines.append("---")
    lines.append("## Documents Content")
    lines.append("")

    # Document Content Sections
    for idx, doc in enumerate(docs, 1):
        anchor_id = f"doc-{idx}-{re.sub(r'[^a-zA-Z0-9_-]', '-', doc.title.lower()).strip('-')}"
        lines.append(f"<document index=\"{idx}\" path=\"{doc.relative_path}\" title=\"{doc.title}\" type=\"{doc.source_type}\">")
        lines.append(f"<a id=\"{anchor_id}\"></a>")
        lines.append(f"### Document {idx}: {doc.title}")
        lines.append("")
        lines.append(f"- **Filename:** `{doc.file_path.name}`")
        lines.append(f"- **Relative Path:** `{doc.relative_path}`")
        lines.append(f"- **Source Type:** `{doc.source_type.upper()}`")
        lines.append(f"- **Word Count:** {doc.word_count:,}")
        lines.append(f"- **Size:** {doc.size_bytes:,} bytes")

        # Section hierarchy
        if doc.sections:
            lines.append("- **Sections Outline:**")
            for sec in doc.sections:
                indent = "  " * max(0, sec.level - 1)
                lines.append(f"  {indent}- {'#' * sec.level} {sec.title}")
        else:
            lines.append("- **Sections Outline:** _No explicit headings found_")

        if doc.frontmatter:
            lines.append("")
            lines.append("#### File Metadata")
            lines.append("```yaml")
            lines.append(doc.frontmatter)
            lines.append("```")

        lines.append("")
        lines.append("#### Content")
        lines.append("")
        lines.append(doc.body)
        lines.append("")
        lines.append("</document>")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consolidate Markdown (.md) and Spreadsheet (.csv) files into a structured, LLM-ready context document or clean RAG markdown.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Local path containing .md or .csv files, or a specific file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="compiled_llm_context.md",
        help="Output Markdown file path (or '-' for stdout).",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Output clean converted markdown body directly without compiled bundle headers, metadata, or <document> wrappers. Recommended when converting a single CSV/file for document store upload.",
    )
    parser.add_argument(
        "--csv-mode",
        choices=["auto", "qa", "table"],
        default="auto",
        help="Formatting mode for CSV files: 'auto' (detect Q&A columns), 'qa' (force Q&A cards), or 'table' (markdown table).",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Recursively scan subdirectories for files.",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        default="",
        help="Comma-separated patterns/directories to exclude (e.g. 'archive/*,temp_*.md').",
    )
    parser.add_argument(
        "--sort",
        choices=["path", "name", "size", "mtime"],
        default="path",
        help="Sort order for collected documents.",
    )
    parser.add_argument(
        "--toc",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include a Table of Contents summary table at the top.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run to inspect matched files without writing output.",
    )

    args = parser.parse_args()

    input_path = Path(args.input_path).expanduser().resolve()
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist.", file=sys.stderr)
        return 1

    exclude_patterns = [p.strip() for p in args.exclude.split(",") if p.strip()]

    raw_files = collect_source_files(
        input_path=input_path,
        recursive=args.recursive,
        exclude_patterns=exclude_patterns,
    )

    if not raw_files:
        print(f"No supported files (.md, .csv) found in '{input_path}'.", file=sys.stderr)
        return 0

    base_dir = input_path if input_path.is_dir() else input_path.parent

    # Sort files based on user preference
    if args.sort == "path":
        raw_files.sort(key=lambda p: str(p))
    elif args.sort == "name":
        raw_files.sort(key=lambda p: p.name.lower())
    elif args.sort == "size":
        raw_files.sort(key=lambda p: p.stat().st_size if p.exists() else 0, reverse=True)
    elif args.sort == "mtime":
        raw_files.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)

    # Parse documents
    docs = [parse_source_file(f, base_dir, csv_mode=args.csv_mode) for f in raw_files]

    if args.dry_run:
        print(f"Found {len(docs)} file(s) under '{input_path}':")
        for idx, doc in enumerate(docs, 1):
            print(f"  [{idx}] {doc.relative_path} (Type: {doc.source_type.upper()}, Title: '{doc.title}', {len(doc.sections)} sections, {doc.word_count:,} words)")
        return 0

    if args.raw:
        # Output clean body directly (concatenated with separator if multiple)
        compiled_text = "\n\n---\n\n".join(d.body for d in docs)
    else:
        compiled_text = generate_compiled_markdown(
            docs=docs,
            source_path=input_path,
            include_toc=args.toc,
        )

    if args.output == "-":
        sys.stdout.write(compiled_text)
    else:
        output_file = Path(args.output).expanduser().resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(compiled_text, encoding="utf-8")
        print(
            f"Successfully converted {len(docs)} file(s) into '{output_file}' "
            f"({sum(d.word_count for d in docs):,} words, {len(compiled_text.encode('utf-8')) / 1024:.2f} KB)."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
