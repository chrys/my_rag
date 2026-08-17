#!/usr/bin/env python3
"""
convert_to_md.py - Markdown Consolidation and LLM Context Preparation Tool.

Aggregates multiple Markdown files from a directory into a structured,
well-organized Markdown file ready to be fed into LLM prompts or context windows.
Extracts file paths, note titles, metadata/frontmatter, and section outlines.

Usage:
    python scripts/convert_to_md.py /path/to/markdown/notes -o compiled_context.md
    python scripts/convert_to_md.py ./Design --exclude "archive,*.tmp" -o design_notes.md
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple


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


@dataclass
class SectionInfo:
    """Represents a Markdown heading section."""
    level: int
    title: str


@dataclass
class MarkdownDoc:
    """Represents a parsed Markdown document with extracted metadata."""
    file_path: Path
    relative_path: str
    title: str
    frontmatter: Optional[str] = None
    sections: List[SectionInfo] = field(default_factory=list)
    body: str = ""
    word_count: int = 0
    size_bytes: int = 0


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
    )


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


def collect_markdown_files(
    input_path: Path,
    recursive: bool = True,
    exclude_patterns: Optional[List[str]] = None,
) -> List[Path]:
    """
    Finds all .md files in the given input path.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    files: List[Path] = []
    if input_path.is_file():
        if input_path.suffix.lower() == ".md":
            files.append(input_path)
        return files

    if not input_path.is_dir():
        return files

    pattern = "**/*.md" if recursive else "*.md"
    for p in input_path.glob(pattern):
        if p.is_file() and not should_exclude(p, exclude_patterns, input_path):
            files.append(p)

    return files


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
    lines.append("This document contains consolidated Markdown notes organized with clear file metadata, note titles, and structural section outlines for LLM ingestion.")
    lines.append("")

    # Table of Contents
    if include_toc and total_docs > 0:
        lines.append("---")
        lines.append("## Table of Contents")
        lines.append("")
        lines.append("| Index | Note Title | File Path | Sections Count | Words |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for idx, doc in enumerate(docs, 1):
            sections_count = len(doc.sections)
            sanitized_title = doc.title.replace("|", "\\|")
            sanitized_path = doc.relative_path.replace("|", "\\|")
            anchor = f"#doc-{idx}-{re.sub(r'[^a-zA-Z0-9_-]', '-', doc.title.lower()).strip('-')}"
            lines.append(f"| {idx} | [{sanitized_title}]({anchor}) | `{sanitized_path}` | {sections_count} | {doc.word_count:,} |")
        lines.append("")

    lines.append("---")
    lines.append("## Documents Content")
    lines.append("")

    # Document Content Sections
    for idx, doc in enumerate(docs, 1):
        anchor_id = f"doc-{idx}-{re.sub(r'[^a-zA-Z0-9_-]', '-', doc.title.lower()).strip('-')}"
        lines.append(f"<document index=\"{idx}\" path=\"{doc.relative_path}\" title=\"{doc.title}\">")
        lines.append(f"<a id=\"{anchor_id}\"></a>")
        lines.append(f"### Document {idx}: {doc.title}")
        lines.append("")
        lines.append(f"- **Filename:** `{doc.file_path.name}`")
        lines.append(f"- **Relative Path:** `{doc.relative_path}`")
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
            lines.append("#### Note Frontmatter Metadata")
            lines.append("```yaml")
            lines.append(doc.frontmatter)
            lines.append("```")

        lines.append("")
        lines.append("#### Note Content")
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
        description="Consolidate Markdown files from a directory into a structured, LLM-ready context document.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Local path containing Markdown (.md) files or a specific .md file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="compiled_llm_context.md",
        help="Output Markdown file path (or '-' for stdout).",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Recursively scan subdirectories for Markdown files.",
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

    raw_files = collect_markdown_files(
        input_path=input_path,
        recursive=args.recursive,
        exclude_patterns=exclude_patterns,
    )

    if not raw_files:
        print(f"No Markdown (.md) files found in '{input_path}'.", file=sys.stderr)
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
    docs = [parse_markdown_file(f, base_dir) for f in raw_files]

    if args.dry_run:
        print(f"Found {len(docs)} Markdown file(s) under '{input_path}':")
        for idx, doc in enumerate(docs, 1):
            print(f"  [{idx}] {doc.relative_path} (Title: '{doc.title}', {len(doc.sections)} sections, {doc.word_count:,} words)")
        return 0

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
            f"Successfully compiled {len(docs)} Markdown file(s) into '{output_file}' "
            f"({sum(d.word_count for d in docs):,} words, {len(compiled_text.encode('utf-8')) / 1024:.2f} KB)."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
