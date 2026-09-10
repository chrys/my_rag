"""
Web crawler service for URL normalization, sitemap parsing, BFS spidering,
boilerplate stripping with Trafilatura, and LlamaIndex vector ingestion.
"""

import logging
import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Set

import httpx

logger = logging.getLogger(__name__)

# Common tracking / marketing parameters to strip
TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "_ga",
    "mc_cid",
    "mc_eid",
}


def sanitize_url(url: str) -> Optional[str]:
    """
    Sanitize and normalize URL:
    - Rejects non-HTTP(S) schemes.
    - Strips fragments (#...).
    - Filters out marketing/analytics tracking query parameters (utm_*, fbclid).
    - Normalizes scheme/host to lowercase.
    """
    if not url or not isinstance(url, str):
        return None

    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        return None

    if not parsed.netloc:
        return None

    # Parse and filter query parameters
    filtered_queries = []
    if parsed.query:
        for pair in parsed.query.split("&"):
            if not pair:
                continue
            key = pair.split("=")[0].lower()
            if key not in TRACKING_PARAMS:
                filtered_queries.append(pair)

    clean_query = "&".join(filtered_queries)

    # Ensure trailing slash if no path is given
    path = parsed.path
    if not path:
        path = "/"

    sanitized = urllib.parse.urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        path,
        "",  # params
        clean_query,
        "",  # fragment stripped
    ))

    return sanitized


def is_within_boundary(url: str, base_url: str, subpath_only: bool = True) -> bool:
    """
    Check whether a target URL falls within the allowed domain/subpath boundary.
    - If subpath_only is True: url must start with base_url prefix (or base path prefix).
    - If subpath_only is False: url must match the same FQDN (netloc).
    """
    clean_target = sanitize_url(url)
    clean_base = sanitize_url(base_url)
    if not clean_target or not clean_base:
        return False

    parsed_target = urllib.parse.urlparse(clean_target)
    parsed_base = urllib.parse.urlparse(clean_base)

    if parsed_target.netloc != parsed_base.netloc:
        return False

    if not subpath_only:
        return True

    # Check path prefix
    base_path = parsed_base.path.rstrip("/")
    target_path = parsed_target.path.rstrip("/")

    if not base_path:
        return True

    return target_path == base_path or target_path.startswith(f"{base_path}/")


def parse_sitemap(
    sitemap_url: str,
    base_url: str,
    subpath_only: bool = True,
    client: Optional[httpx.Client] = None,
    visited_sitemaps: Optional[Set[str]] = None,
    max_urls: int = 500,
) -> List[Dict[str, Any]]:
    """
    Parse a sitemap.xml or sitemapindex.
    Recursively descends into nested sitemaps and extracts URLs matching boundary rules.
    """
    if visited_sitemaps is None:
        visited_sitemaps = set()

    clean_sitemap_url = sanitize_url(sitemap_url)
    if not clean_sitemap_url or clean_sitemap_url in visited_sitemaps:
        return []

    visited_sitemaps.add(clean_sitemap_url)
    discovered_urls: List[Dict[str, Any]] = []

    own_client = False
    if client is None:
        client = httpx.Client(timeout=10.0, follow_redirects=True)
        own_client = True

    try:
        resp = client.get(clean_sitemap_url)
        if resp.status_code != 200:
            return []

        root = ET.fromstring(resp.content)
        tag_name = root.tag.lower()

        # Strip namespace if present
        def get_clean_tag(elem: ET.Element) -> str:
            return elem.tag.split("}")[-1].lower() if "}" in elem.tag else elem.tag.lower()

        root_clean_tag = get_clean_tag(root)

        # Handle sitemapindex (nested sitemaps)
        if root_clean_tag == "sitemapindex":
            for child in root:
                if get_clean_tag(child) == "sitemap":
                    loc_elem = child.find("{*}loc") if child.find("{*}loc") is not None else child.find("loc")
                    if loc_elem is not None and loc_elem.text:
                        sub_sitemap_url = loc_elem.text.strip()
                        sub_results = parse_sitemap(
                            sub_sitemap_url,
                            base_url=base_url,
                            subpath_only=subpath_only,
                            client=client,
                            visited_sitemaps=visited_sitemaps,
                            max_urls=max_urls,
                        )
                        discovered_urls.extend(sub_results)
                        if len(discovered_urls) >= max_urls:
                            break

        # Handle standard urlset
        elif root_clean_tag == "urlset":
            for child in root:
                if get_clean_tag(child) == "url":
                    loc_elem = child.find("{*}loc") if child.find("{*}loc") is not None else child.find("loc")
                    lastmod_elem = child.find("{*}lastmod") if child.find("{*}lastmod") is not None else child.find("lastmod")

                    if loc_elem is not None and loc_elem.text:
                        raw_loc = loc_elem.text.strip()
                        sanitized_loc = sanitize_url(raw_loc)
                        if sanitized_loc and is_within_boundary(sanitized_loc, base_url, subpath_only):
                            lastmod_val = lastmod_elem.text.strip() if (lastmod_elem is not None and lastmod_elem.text) else ""
                            discovered_urls.append({
                                "url": sanitized_loc,
                                "lastmod": lastmod_val,
                            })
                            if len(discovered_urls) >= max_urls:
                                break

    except Exception as exc:
        logger.warning(f"Error parsing sitemap at '{clean_sitemap_url}': {exc}")
    finally:
        if own_client:
            client.close()

    return discovered_urls


import urllib.robotparser
from collections import deque
import time
from bs4 import BeautifulSoup

IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar",
    ".mp4", ".mp3", ".wav", ".avi", ".mov",
    ".exe", ".dmg", ".iso", ".bin", ".apk",
}


def check_robots_txt(
    base_url: str,
    target_url: str,
    user_agent: str = "*",
    client: Optional[httpx.Client] = None,
) -> bool:
    """
    Check if a target URL is allowed by the host's robots.txt.
    Returns True if allowed or if robots.txt cannot be retrieved.
    """
    parsed_base = urllib.parse.urlparse(base_url)
    robots_url = f"{parsed_base.scheme}://{parsed_base.netloc}/robots.txt"

    own_client = False
    if client is None:
        client = httpx.Client(timeout=5.0, follow_redirects=True)
        own_client = True

    try:
        resp = client.get(robots_url)
        if resp.status_code == 200:
            parser = urllib.robotparser.RobotFileParser()
            parser.parse(resp.text.splitlines())
            return parser.can_fetch(user_agent, target_url)
        # If 404 or other status, assume allowed
        return True
    except Exception as exc:
        logger.debug(f"robots.txt check failed for '{robots_url}': {exc}. Defaulting to allowed.")
        return True
    finally:
        if own_client:
            client.close()


def crawl_site_bfs(
    root_url: str,
    max_depth: int = 4,
    max_pages: int = 100,
    subpath_only: bool = True,
    client: Optional[httpx.Client] = None,
    crawl_delay_ms: int = 0,
) -> List[Dict[str, Any]]:
    """
    Bounded breadth-first search spider starting from root_url.
    Returns a list of dicts with url, depth, title, and raw_html.
    """
    clean_root = sanitize_url(root_url)
    if not clean_root:
        return []

    own_client = False
    if client is None:
        client = httpx.Client(timeout=10.0, follow_redirects=True)
        own_client = True

    visited: Set[str] = set()
    queue: deque = deque([(clean_root, 0)])
    results: List[Dict[str, Any]] = []

    try:
        while queue and len(results) < max_pages:
            current_url, depth = queue.popleft()
            if current_url in visited:
                continue

            visited.add(current_url)

            # Check robots.txt
            if not check_robots_txt(clean_root, current_url, client=client):
                logger.info(f"Skipping disbarred URL by robots.txt: {current_url}")
                continue

            try:
                resp = client.get(current_url)
                if resp.status_code != 200:
                    continue

                content_type = resp.headers.get("content-type", "").lower()
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    continue

                html_text = resp.text
                soup = BeautifulSoup(html_text, "html.parser")

                # Extract title
                title = ""
                title_tag = soup.find("title")
                if title_tag and title_tag.string:
                    title = title_tag.string.strip()
                elif soup.find("h1"):
                    title = soup.find("h1").get_text(strip=True)

                results.append({
                    "url": current_url,
                    "depth": depth,
                    "title": title[:500],
                    "raw_html": html_text,
                    "http_status": resp.status_code,
                })

                if depth < max_depth and len(results) < max_pages:
                    for link in soup.find_all("a", href=True):
                        raw_href = link["href"].strip()
                        resolved_href = urllib.parse.urljoin(current_url, raw_href)
                        sanitized_link = sanitize_url(resolved_href)

                        if not sanitized_link or sanitized_link in visited:
                            continue

                        # Check extension
                        parsed_link = urllib.parse.urlparse(sanitized_link)
                        path_ext = os.path.splitext(parsed_link.path)[1].lower()
                        if path_ext in IGNORED_EXTENSIONS:
                            continue

                        if is_within_boundary(sanitized_link, clean_root, subpath_only):
                            queue.append((sanitized_link, depth + 1))

                if crawl_delay_ms > 0:
                    time.sleep(crawl_delay_ms / 1000.0)

            except Exception as req_err:
                logger.warning(f"Failed crawling '{current_url}': {req_err}")

    finally:
        if own_client:
            client.close()

    return results


import hashlib
import tempfile
import trafilatura
from django.utils import timezone
from django.conf import settings


def extract_clean_markdown(html_content: str) -> Optional[str]:
    """
    Extract clean, semantic Markdown from raw HTML using base Trafilatura.
    Strips navigation bars, footers, cookie banners, scripts, and ads.
    Falls back to BeautifulSoup boilerplate stripping if Trafilatura fails.
    """
    if not html_content or len(html_content.strip()) < 50:
        return None

    try:
        extracted = trafilatura.extract(
            html_content,
            output_format="markdown",
            include_links=True,
            include_tables=True,
            favor_recall=True,
        )
        if extracted and len(extracted.strip()) >= 50:
            return extracted.strip()
    except Exception as exc:
        logger.debug(f"Trafilatura extraction notice: {exc}")

    # Fallback to BeautifulSoup cleaning
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["nav", "header", "footer", "script", "style", "aside", "noscript", "svg"]):
            tag.decompose()

        main_body = soup.find("main") or soup.find("article") or soup.find("body") or soup
        text = main_body.get_text(separator="\n\n", strip=True)
        if text and len(text) >= 50:
            return text
    except Exception as exc:
        logger.warning(f"BeautifulSoup fallback extraction failed: {exc}")

    return None


def process_web_page_indexing(
    web_page: Any,
    project_id: str,
    raw_html: Optional[str] = None,
    client: Optional[httpx.Client] = None,
) -> bool:
    """
    Fetch (if needed), sanitize into Markdown, enrich metadata,
    and index the web page into LlamaIndex / PGVectorStore.
    """
    from src.apps.documents.services import LlamaIndexIngestionPipeline

    html = raw_html
    own_client = False

    if not html:
        if client is None:
            client = httpx.Client(timeout=10.0, follow_redirects=True)
            own_client = True

        try:
            resp = client.get(web_page.url)
            web_page.http_status = resp.status_code
            web_page.last_scraped_at = timezone.now()
            etag_hdr = resp.headers.get("etag", "")
            if etag_hdr:
                web_page.etag = etag_hdr
            lastmod_hdr = resp.headers.get("last-modified", "")
            if lastmod_hdr:
                web_page.last_modified_header = lastmod_hdr

            if resp.status_code != 200:
                web_page.status = "FAILED"
                web_page.error_message = f"HTTP request failed with status code {resp.status_code}"
                web_page.save()
                return False

            html = resp.text
        except Exception as net_err:
            web_page.status = "FAILED"
            web_page.error_message = f"Failed fetching URL: {net_err}"
            web_page.save()
            return False
        finally:
            if own_client:
                client.close()

    markdown_text = extract_clean_markdown(html)
    if not markdown_text:
        web_page.status = "FAILED"
        web_page.error_message = "Content could not be extracted or page requires client-side JavaScript rendering."
        web_page.save()
        return False

    content_hash = hashlib.sha256(markdown_text.encode("utf-8")).hexdigest()

    # Prepend YAML-like metadata header to markdown for LlamaIndex
    formatted_content = f"# {web_page.title or web_page.url}\n\nSource: {web_page.url}\n\n{markdown_text}"

    tmp_dir = os.path.join(getattr(settings, "BASE_DIR", os.getcwd()), "tmp_test_dir")
    os.makedirs(tmp_dir, exist_ok=True)

    tmp_file = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False, dir=tmp_dir) as tmp:
            tmp.write(formatted_content)
            tmp_path = tmp.name
            tmp_file = tmp_path

        pipeline = LlamaIndexIngestionPipeline(project_id=project_id)
        pipeline.index_document(
            file_path=tmp_path,
            original_filename=web_page.url,
            strategy="markdown"
        )

        web_page.status = "INDEXED"
        web_page.content_hash = content_hash
        web_page.last_indexed_at = timezone.now()
        web_page.error_message = ""
        web_page.save()
        return True

    except Exception as idx_err:
        logger.error(f"Failed indexing web page '{web_page.url}': {idx_err}")
        web_page.status = "FAILED"
        web_page.error_message = str(idx_err)
        web_page.save()
        return False
    finally:
        if tmp_file and os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except OSError:
                pass


def discover_pages_for_source(
    web_source: Any,
    client: Optional[httpx.Client] = None,
) -> int:
    """
    Discovers URLs belonging to a WebSource via sitemap and BFS spidering.
    Inserts newly discovered pages into the database with status 'PENDING'.
    Returns the count of newly discovered WebPage records.
    """
    from src.apps.documents.models import WebPage

    own_client = False
    if client is None:
        client = httpx.Client(timeout=10.0, follow_redirects=True)
        own_client = True

    discovered_items: List[Dict[str, Any]] = []
    seen_urls: Set[str] = set(
        web_source.pages.values_list("url", flat=True)
    )

    try:
        # 1. Sitemap-first discovery
        parsed = urllib.parse.urlparse(web_source.root_url)
        sitemap_candidates = [
            f"{parsed.scheme}://{parsed.netloc}/sitemap.xml",
            urllib.parse.urljoin(web_source.root_url, "sitemap.xml"),
            urllib.parse.urljoin(web_source.root_url, "/sitemap.xml"),
        ]
        unique_candidates = list(dict.fromkeys(sitemap_candidates))

        for candidate in unique_candidates:
            sitemap_entries = parse_sitemap(
                candidate,
                base_url=web_source.root_url,
                subpath_only=web_source.subpath_only,
                client=client,
                max_urls=web_source.max_pages,
            )
            for entry in sitemap_entries:
                u = entry["url"]
                if u not in seen_urls:
                    seen_urls.add(u)
                    discovered_items.append({"url": u, "depth": 1, "title": ""})
                    if len(seen_urls) >= web_source.max_pages:
                        break
            if len(seen_urls) >= web_source.max_pages:
                break

        # 2. BFS spider fallback or supplement if under max_pages
        remaining_slots = web_source.max_pages - len(seen_urls)
        if remaining_slots > 0:
            spider_results = crawl_site_bfs(
                root_url=web_source.root_url,
                max_depth=web_source.max_depth,
                max_pages=web_source.max_pages,
                subpath_only=web_source.subpath_only,
                client=client,
            )
            for item in spider_results:
                u = item["url"]
                if u not in seen_urls:
                    seen_urls.add(u)
                    discovered_items.append({
                        "url": u,
                        "depth": item.get("depth", 0),
                        "title": item.get("title", ""),
                    })
                    if len(seen_urls) >= web_source.max_pages:
                        break

        # 3. Create WebPage records for newly discovered items
        new_pages = []
        for item in discovered_items:
            new_pages.append(
                WebPage(
                    web_source=web_source,
                    url=item["url"],
                    title=item.get("title", "")[:500],
                    depth=item.get("depth", 0),
                    status="PENDING",
                )
            )

        if new_pages:
            WebPage.objects.bulk_create(new_pages, ignore_conflicts=True)

        return len(new_pages)

    finally:
        if own_client:
            client.close()


def run_web_lifecycle(
    web_source: Any,
    mode: str = "sync",
    client: Optional[httpx.Client] = None,
) -> Dict[str, Any]:
    """
    Execute website crawling, delta synchronization, or vector indexing lifecycle.

    Modes:
    - 'discover': Discover URLs, populate WebPage with status='PENDING'.
    - 'sync': Check existing pages; if HTTP 404/410, purge vector store and mark DELETED.
              If content SHA-256 changed, mark MODIFIED. Discover any new URLs.
    - 'index_new': Index only PENDING and MODIFIED pages (purging old vectors before re-indexing).
    - 'full': Full discovery + complete re-index of all pages.
    """
    own_client = False
    if client is None:
        client = httpx.Client(timeout=10.0, follow_redirects=True)
        own_client = True

    stats: Dict[str, Any] = {
        "status": "COMPLETED",
        "mode": mode,
        "discovered": 0,
        "indexed": 0,
        "modified": 0,
        "deleted": 0,
        "failed": 0,
        "errors": [],
    }

    try:
        # Phase A: Discovery
        if mode in ("discover", "sync", "full"):
            web_source.sync_status = "DISCOVERING"
            web_source.save(update_fields=["sync_status", "updated_at"])
            discovered_count = discover_pages_for_source(web_source, client=client)
            stats["discovered"] = discovered_count

        # Phase B: Sync / Delta Verification
        if mode in ("sync",):
            existing_pages = list(web_source.pages.exclude(status="DELETED"))
            for page in existing_pages:
                try:
                    resp = client.get(page.url)
                    page.http_status = resp.status_code
                    page.last_scraped_at = timezone.now()

                    if resp.status_code in (404, 410):
                        # Purge vector embeddings
                        try:
                            from src.postgres_rag import PostgresRAGEngine
                            engine = PostgresRAGEngine(project_id=web_source.project.project_id)
                            engine.delete_document(page.url)
                        except Exception as purge_err:
                            logger.warning(f"Failed deleting vectors for 404 page '{page.url}': {purge_err}")

                        page.status = "DELETED"
                        page.save()
                        stats["deleted"] += 1

                    elif resp.status_code == 200:
                        md = extract_clean_markdown(resp.text)
                        if md:
                            new_hash = hashlib.sha256(md.encode("utf-8")).hexdigest()
                            if page.content_hash and page.content_hash != new_hash:
                                page.status = "MODIFIED"
                                stats["modified"] += 1
                        page.save()
                except Exception as check_err:
                    logger.warning(f"Error checking page '{page.url}' during sync: {check_err}")

        # Phase C: Vector Indexing
        if mode in ("index_new", "full"):
            web_source.sync_status = "INDEXING"
            web_source.save(update_fields=["sync_status", "updated_at"])

            if mode == "full":
                target_pages = list(web_source.pages.exclude(status="DELETED"))
            else:
                target_pages = list(web_source.pages.filter(status__in=["PENDING", "MODIFIED"]))

            for page in target_pages:
                if page.status == "MODIFIED" or mode == "full":
                    # Purge stale embeddings before re-embedding
                    try:
                        from src.postgres_rag import PostgresRAGEngine
                        engine = PostgresRAGEngine(project_id=web_source.project.project_id)
                        engine.delete_document(page.url)
                    except Exception as purge_err:
                        logger.warning(f"Failed purging vectors before re-indexing '{page.url}': {purge_err}")

                success = process_web_page_indexing(
                    web_page=page,
                    project_id=web_source.project.project_id,
                    client=client,
                )
                if success:
                    stats["indexed"] += 1
                else:
                    stats["failed"] += 1

        # Phase D: Update WebSource counters and Project stats
        web_source.total_pages_count = web_source.pages.count()
        web_source.indexed_pages_count = web_source.pages.filter(status="INDEXED").count()
        web_source.pending_pages_count = web_source.pages.filter(status__in=["PENDING", "MODIFIED"]).count()
        web_source.failed_pages_count = web_source.pages.filter(status="FAILED").count()
        web_source.sync_status = "COMPLETED"
        web_source.last_synced_at = timezone.now()
        web_source.error_message = ""
        web_source.save()

        # Update Project document count
        project = web_source.project
        project.document_count = web_source.indexed_pages_count
        project.save(update_fields=["document_count"])

        return stats

    except Exception as exc:
        logger.error(f"Error executing web lifecycle mode '{mode}' on WebSource {web_source.id}: {exc}", exc_info=True)
        web_source.sync_status = "FAILED"
        web_source.error_message = str(exc)
        web_source.save()

        stats["status"] = "FAILED"
        stats["error"] = str(exc)
        return stats

    finally:
        if own_client:
            client.close()

