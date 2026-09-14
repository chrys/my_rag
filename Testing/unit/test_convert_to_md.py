"""
Unit tests for scripts/convert_to_md.py
"""

import io
from pathlib import Path
import pytest

from scripts.convert_to_md import (
    detect_csv_qa_columns,
    format_csv_as_qa,
    format_csv_as_table,
    parse_csv_file,
    parse_source_file,
    collect_source_files,
    generate_compiled_markdown,
)


def test_detect_csv_qa_columns():
    headers = ["Category", "Question", "Answer", "Notes", "Extra"]
    cat, q, a, n = detect_csv_qa_columns(headers)
    assert cat == "Category"
    assert q == "Question"
    assert a == "Answer"
    assert n == "Notes"


def test_detect_csv_qa_columns_synonyms():
    headers = ["topic", "q", "a", "context"]
    cat, q, a, n = detect_csv_qa_columns(headers)
    assert cat == "topic"
    assert q == "q"
    assert a == "a"
    assert n == "context"


def test_detect_csv_non_qa():
    headers = ["id", "name", "price", "stock"]
    cat, q, a, n = detect_csv_qa_columns(headers)
    assert q is None
    assert a is None


def test_parse_csv_qa_with_categories(tmp_path: Path):
    csv_content = """category,question,answer,notes
Billing,How do I pay?,You can pay via credit card.,Invoices generated monthly.
Billing,Can I get a refund?,Yes within 14 days.,Contact support.
Security,How to reset password?,Go to Settings > Security.,Link expires in 1 hour.
"""
    csv_file = tmp_path / "faq.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    doc = parse_csv_file(csv_file, tmp_path, csv_mode="auto")
    assert doc.source_type == "csv"
    assert "Faq" in doc.title
    assert "## Category: Billing" in doc.body
    assert "## Category: Security" in doc.body
    assert "### How do I pay?" in doc.body
    assert "**Answer:** You can pay via credit card." in doc.body
    assert "**Notes:** Invoices generated monthly." in doc.body
    assert "### How to reset password?" in doc.body
    assert len(doc.sections) >= 5


def test_parse_csv_table_mode(tmp_path: Path):
    csv_content = """id,product,price
1,Widget,19.99
2,Gadget,29.99
"""
    csv_file = tmp_path / "products.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    doc = parse_csv_file(csv_file, tmp_path, csv_mode="auto")
    assert doc.source_type == "csv"
    assert "| id | product | price |" in doc.body
    assert "| 1 | Widget | 19.99 |" in doc.body
    assert "| 2 | Gadget | 29.99 |" in doc.body


def test_parse_csv_utf8_bom(tmp_path: Path):
    # Excel exports often start with UTF-8 BOM \ufeff
    csv_content = "\ufeffcategory,question,answer,notes\nGeneral,What is this?,A test.,None\n"
    csv_file = tmp_path / "bom_faq.csv"
    csv_file.write_bytes(csv_content.encode("utf-8"))

    doc = parse_csv_file(csv_file, tmp_path, csv_mode="auto")
    assert "## Category: General" in doc.body
    assert "### What is this?" in doc.body
    assert "**Answer:** A test." in doc.body


def test_collect_source_files(tmp_path: Path):
    (tmp_path / "note1.md").write_text("# Note 1", encoding="utf-8")
    (tmp_path / "sheet.csv").write_text("a,b\n1,2", encoding="utf-8")
    (tmp_path / "ignore.tmp").write_text("tmp", encoding="utf-8")

    files = collect_source_files(tmp_path, recursive=True)
    names = {f.name for f in files}
    assert "note1.md" in names
    assert "sheet.csv" in names
    assert "ignore.tmp" not in names
