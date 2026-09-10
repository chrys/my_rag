"""
Unit tests for web crawler services (URL sanitization, boundary checking, sitemap parsing).
"""

import pytest
import httpx
from unittest.mock import MagicMock
from src.apps.documents.web_crawler_services import (
    sanitize_url,
    is_within_boundary,
    parse_sitemap,
)


class TestWebCrawlerSanitization:
    """Tests for URL sanitization and normalization."""

    def test_sanitize_url_strips_fragments(self):
        raw = "https://docs.example.com/guides/intro#section-1"
        assert sanitize_url(raw) == "https://docs.example.com/guides/intro"

    def test_sanitize_url_strips_tracking_params(self):
        raw = "https://docs.example.com/guides/?utm_source=twitter&utm_medium=cpc&fbclid=12345&id=42"
        sanitized = sanitize_url(raw)
        assert "utm_source" not in sanitized
        assert "utm_medium" not in sanitized
        assert "fbclid" not in sanitized
        assert "id=42" in sanitized

    def test_sanitize_url_normalizes_trailing_slash(self):
        assert sanitize_url("https://docs.example.com") == "https://docs.example.com/"
        assert sanitize_url("https://docs.example.com/api") == "https://docs.example.com/api"

    def test_sanitize_url_rejects_non_http(self):
        assert sanitize_url("mailto:test@example.com") is None
        assert sanitize_url("javascript:void(0)") is None
        assert sanitize_url("tel:+123456789") is None


class TestWebCrawlerBoundary:
    """Tests for domain and subpath boundary checking."""

    def test_subpath_only_boundary(self):
        base = "https://example.com/docs/"
        assert is_within_boundary("https://example.com/docs/intro", base, subpath_only=True) is True
        assert is_within_boundary("https://example.com/docs/api/v1", base, subpath_only=True) is True
        assert is_within_boundary("https://example.com/blog/article", base, subpath_only=True) is False
        assert is_within_boundary("https://other.com/docs/intro", base, subpath_only=True) is False

    def test_entire_domain_boundary(self):
        base = "https://example.com/docs/"
        assert is_within_boundary("https://example.com/blog/article", base, subpath_only=False) is True
        assert is_within_boundary("https://other.com/docs/", base, subpath_only=False) is False


class TestWebCrawlerSitemapParser:
    """Tests for sitemap.xml parsing."""

    def test_parse_standard_sitemap(self):
        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/docs/intro</loc>
                <lastmod>2026-08-01T12:00:00Z</lastmod>
            </url>
            <url>
                <loc>https://example.com/docs/api</loc>
                <lastmod>2026-08-02T15:00:00Z</lastmod>
            </url>
            <url>
                <loc>https://example.com/blog/ignore-me</loc>
                <lastmod>2026-08-03T10:00:00Z</lastmod>
            </url>
        </urlset>"""

        def handler(request: httpx.Request):
            return httpx.Response(200, text=sitemap_xml, headers={"Content-Type": "application/xml"})

        client = httpx.Client(transport=httpx.MockTransport(handler))
        results = parse_sitemap(
            "https://example.com/sitemap.xml",
            base_url="https://example.com/docs/",
            subpath_only=True,
            client=client
        )

        assert len(results) == 2
        urls = [r["url"] for r in results]
        assert "https://example.com/docs/intro" in urls
        assert "https://example.com/docs/api" in urls
        assert "https://example.com/blog/ignore-me" not in urls
        assert results[0]["lastmod"] == "2026-08-01T12:00:00Z"

    def test_parse_sitemap_index_nested(self):
        index_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>https://example.com/sitemap-docs.xml</loc>
            </sitemap>
        </sitemapindex>"""

        child_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/docs/nested-page</loc>
                <lastmod>2026-08-05T00:00:00Z</lastmod>
            </url>
        </urlset>"""

        def handler(request: httpx.Request):
            if "sitemap-docs.xml" in str(request.url):
                return httpx.Response(200, text=child_xml, headers={"Content-Type": "application/xml"})
            return httpx.Response(200, text=index_xml, headers={"Content-Type": "application/xml"})

        client = httpx.Client(transport=httpx.MockTransport(handler))
        results = parse_sitemap(
            "https://example.com/sitemap.xml",
            base_url="https://example.com/docs/",
            subpath_only=True,
            client=client
        )

        assert len(results) == 1
        assert results[0]["url"] == "https://example.com/docs/nested-page"
        assert results[0]["lastmod"] == "2026-08-05T00:00:00Z"


class TestWebCrawlerRobots:
    """Tests for robots.txt parsing and compliance."""

    def test_robots_txt_disallow(self):
        from src.apps.documents.web_crawler_services import check_robots_txt

        robots_text = """User-agent: *
Disallow: /docs/private/
Disallow: /admin/
"""
        def handler(request: httpx.Request):
            return httpx.Response(200, text=robots_text)

        client = httpx.Client(transport=httpx.MockTransport(handler))
        assert check_robots_txt("https://example.com/docs/", "https://example.com/docs/intro", client=client) is True
        assert check_robots_txt("https://example.com/docs/", "https://example.com/docs/private/secret", client=client) is False


class TestWebCrawlerSpider:
    """Tests for bounded BFS link crawler."""

    def test_bfs_crawl_discovers_links_within_subpath(self):
        from src.apps.documents.web_crawler_services import crawl_site_bfs

        html_root = """<html><body>
            <a href="/docs/page1">Page 1</a>
            <a href="/docs/page2">Page 2</a>
            <a href="/blog/ignored">Blog</a>
            <a href="/docs/asset.pdf">PDF File</a>
            <a href="https://other.com/ext">External</a>
        </body></html>"""

        html_page1 = """<html><body>
            <a href="/docs/page3">Page 3</a>
        </body></html>"""

        html_page2 = """<html><body>Empty</body></html>"""
        html_page3 = """<html><body>Leaf</body></html>"""

        def handler(request: httpx.Request):
            url_str = str(request.url)
            if url_str.endswith("/docs/page1"):
                return httpx.Response(200, text=html_page1, headers={"Content-Type": "text/html"})
            elif url_str.endswith("/docs/page2"):
                return httpx.Response(200, text=html_page2, headers={"Content-Type": "text/html"})
            elif url_str.endswith("/docs/page3"):
                return httpx.Response(200, text=html_page3, headers={"Content-Type": "text/html"})
            elif "robots.txt" in url_str:
                return httpx.Response(404)
            return httpx.Response(200, text=html_root, headers={"Content-Type": "text/html"})

        client = httpx.Client(transport=httpx.MockTransport(handler))
        pages = crawl_site_bfs(
            root_url="https://example.com/docs/",
            max_depth=2,
            max_pages=10,
            subpath_only=True,
            client=client
        )

        urls = [p["url"] for p in pages]
        assert "https://example.com/docs/" in urls
        assert "https://example.com/docs/page1" in urls
        assert "https://example.com/docs/page2" in urls
        assert "https://example.com/docs/page3" in urls
        assert not any("asset.pdf" in u for u in urls)
        assert not any("blog" in u for u in urls)
        assert not any("other.com" in u for u in urls)


class TestWebCrawlerExtraction:
    """Tests for Trafilatura Markdown extraction."""

    def test_extract_clean_markdown_strips_boilerplate(self):
        from src.apps.documents.web_crawler_services import extract_clean_markdown

        raw_html = """<!DOCTYPE html>
        <html>
        <head><title>Test Guide</title></head>
        <body>
            <header><nav><a href="/">Home</a><a href="/login">Login</a></nav></header>
            <main>
                <article>
                    <h1>Getting Started with Django</h1>
                    <p>Django is a high-level Python web framework that encourages rapid development and clean design.</p>
                    <p>Built by experienced developers, it takes care of much of the hassle of web development.</p>
                </article>
            </main>
            <footer><p>&copy; 2026 Example Corp. All rights reserved. Cookie policy.</p></footer>
        </body>
        </html>"""

        md = extract_clean_markdown(raw_html)
        assert md is not None
        assert "Getting Started with Django" in md
        assert "Django is a high-level Python web framework" in md
        assert "Cookie policy" not in md
        assert "Login" not in md

    def test_extract_clean_markdown_rejects_empty(self):
        from src.apps.documents.web_crawler_services import extract_clean_markdown

        assert extract_clean_markdown("") is None
        assert extract_clean_markdown("   ") is None
        assert extract_clean_markdown("<html><body><p>Short</p></body></html>") is None


@pytest.mark.django_db
class TestWebCrawlerIndexing:
    """Tests for vector ingestion and WebPage state updates."""

    def test_process_web_page_indexing_success(self, monkeypatch):
        from src.apps.projects.models import Project
        from src.apps.documents.models import WebSource, WebPage
        from src.apps.documents.web_crawler_services import process_web_page_indexing

        project = Project.objects.create(
            project_id="web_indexing_test_01",
            display_name="Web Indexing Test",
            storage_type="postgres",
        )
        source = WebSource.objects.create(
            project=project,
            root_url="https://example.com/docs/",
            allowed_domain="example.com",
        )
        page = WebPage.objects.create(
            web_source=source,
            url="https://example.com/docs/page1",
            title="Page 1",
            status="PENDING",
        )

        sample_html = """<!DOCTYPE html>
        <html><body><article>
        <h1>Article Header</h1>
        <p>This is a long enough article content to test valid extraction and vector ingestion into the project store.</p>
        </article></body></html>"""

        mock_index_doc = MagicMock()
        monkeypatch.setattr(
            "src.apps.documents.services.LlamaIndexIngestionPipeline.index_document",
            mock_index_doc,
        )

        success = process_web_page_indexing(
            web_page=page,
            project_id=project.project_id,
            raw_html=sample_html
        )

        assert success is True
        page.refresh_from_db()
        assert page.status == "INDEXED"
        assert len(page.content_hash) == 64
        assert page.last_indexed_at is not None
        assert mock_index_doc.called


@pytest.mark.django_db
class TestWebLifecycle:
    """Tests for run_web_lifecycle (discover, sync, index_new, full)."""

    def test_run_web_lifecycle_discover(self, monkeypatch):
        from src.apps.projects.models import Project
        from src.apps.documents.models import WebSource, WebPage
        from src.apps.documents.web_crawler_services import run_web_lifecycle

        project = Project.objects.create(
            project_id="lifecycle_proj_01",
            display_name="Lifecycle Proj 1",
            storage_type="postgres",
        )
        source = WebSource.objects.create(
            project=project,
            root_url="https://example.com/docs/",
            allowed_domain="example.com",
            subpath_only=True,
            max_pages=10,
        )

        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/docs/page-a</loc></url>
            <url><loc>https://example.com/docs/page-b</loc></url>
        </urlset>"""

        def handler(request: httpx.Request):
            if "sitemap.xml" in str(request.url):
                return httpx.Response(200, text=sitemap_xml, headers={"Content-Type": "application/xml"})
            if "robots.txt" in str(request.url):
                return httpx.Response(200, text="User-agent: *\nAllow: /")
            return httpx.Response(404)

        client = httpx.Client(transport=httpx.MockTransport(handler))

        res = run_web_lifecycle(source, mode="discover", client=client)

        assert res["status"] == "COMPLETED"
        assert res["discovered"] == 2
        source.refresh_from_db()
        assert source.sync_status == "COMPLETED"
        assert source.total_pages_count == 2
        assert source.pending_pages_count == 2

        pages = list(WebPage.objects.filter(web_source=source).order_by("url"))
        assert len(pages) == 2
        assert pages[0].url == "https://example.com/docs/page-a"
        assert pages[0].status == "PENDING"
        assert pages[1].url == "https://example.com/docs/page-b"
        assert pages[1].status == "PENDING"

    def test_run_web_lifecycle_sync_detects_modified_and_deleted(self, monkeypatch):
        from src.apps.projects.models import Project
        from src.apps.documents.models import WebSource, WebPage
        from src.apps.documents.web_crawler_services import run_web_lifecycle

        project = Project.objects.create(
            project_id="lifecycle_proj_02",
            display_name="Lifecycle Proj 2",
            storage_type="postgres",
        )
        source = WebSource.objects.create(
            project=project,
            root_url="https://example.com/docs/",
            allowed_domain="example.com",
            subpath_only=True,
            max_pages=10,
        )

        page_mod = WebPage.objects.create(
            web_source=source,
            url="https://example.com/docs/modified-page",
            title="Modified Page",
            status="INDEXED",
            content_hash="old_initial_hash_val",
        )
        page_del = WebPage.objects.create(
            web_source=source,
            url="https://example.com/docs/deleted-page",
            title="Deleted Page",
            status="INDEXED",
            content_hash="some_del_hash",
        )

        mock_delete_doc = MagicMock()
        monkeypatch.setattr(
            "src.postgres_rag.PostgresRAGEngine.delete_document",
            mock_delete_doc,
        )

        new_html = """<!DOCTYPE html>
        <html><body><article>
        <h1>Updated Content</h1>
        <p>This page has drastically changed and will have a brand new content hash representation.</p>
        </article></body></html>"""

        def handler(request: httpx.Request):
            url_str = str(request.url)
            if "sitemap.xml" in url_str or "robots.txt" in url_str:
                return httpx.Response(404)
            if "modified-page" in url_str:
                return httpx.Response(200, text=new_html, headers={"Content-Type": "text/html"})
            if "deleted-page" in url_str:
                return httpx.Response(404)
            return httpx.Response(404)

        client = httpx.Client(transport=httpx.MockTransport(handler))

        res = run_web_lifecycle(source, mode="sync", client=client)

        assert res["status"] == "COMPLETED"
        assert res["modified"] == 1
        assert res["deleted"] == 1

        page_mod.refresh_from_db()
        assert page_mod.status == "MODIFIED"

        page_del.refresh_from_db()
        assert page_del.status == "DELETED"
        assert page_del.http_status == 404
        # Verify vector deletion was called for 404 page
        mock_delete_doc.assert_called_with("https://example.com/docs/deleted-page")

    def test_run_web_lifecycle_index_new(self, monkeypatch):
        from src.apps.projects.models import Project
        from src.apps.documents.models import WebSource, WebPage
        from src.apps.documents.web_crawler_services import run_web_lifecycle

        project = Project.objects.create(
            project_id="lifecycle_proj_03",
            display_name="Lifecycle Proj 3",
            storage_type="postgres",
        )
        source = WebSource.objects.create(
            project=project,
            root_url="https://example.com/docs/",
            allowed_domain="example.com",
            subpath_only=True,
            max_pages=10,
        )

        page_pending = WebPage.objects.create(
            web_source=source,
            url="https://example.com/docs/pending-page",
            title="Pending Page",
            status="PENDING",
        )
        page_mod = WebPage.objects.create(
            web_source=source,
            url="https://example.com/docs/modified-page",
            title="Modified Page",
            status="MODIFIED",
            content_hash="old_hash_to_purge",
        )

        mock_delete_doc = MagicMock()
        monkeypatch.setattr(
            "src.postgres_rag.PostgresRAGEngine.delete_document",
            mock_delete_doc,
        )

        sample_html = """<!DOCTYPE html>
        <html><body><article>
        <h1>Indexed Page</h1>
        <p>This is adequate body copy for indexing into the project vector index.</p>
        </article></body></html>"""

        mock_index_doc = MagicMock()
        monkeypatch.setattr(
            "src.apps.documents.services.LlamaIndexIngestionPipeline.index_document",
            mock_index_doc,
        )

        def handler(request: httpx.Request):
            return httpx.Response(200, text=sample_html, headers={"Content-Type": "text/html"})

        client = httpx.Client(transport=httpx.MockTransport(handler))

        res = run_web_lifecycle(source, mode="index_new", client=client)

        assert res["status"] == "COMPLETED"
        assert res["indexed"] == 2

        page_pending.refresh_from_db()
        assert page_pending.status == "INDEXED"

        page_mod.refresh_from_db()
        assert page_mod.status == "INDEXED"

        # Purge was called for the modified page before re-indexing
        mock_delete_doc.assert_called_with("https://example.com/docs/modified-page")

        source.refresh_from_db()
        assert source.indexed_pages_count == 2
        assert source.pending_pages_count == 0

        project.refresh_from_db()
        assert project.document_count == 2

