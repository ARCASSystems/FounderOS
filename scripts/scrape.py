#!/usr/bin/env python3
"""scrape.py - small web fetch + parse utility for Founder OS.

Public surface:
    fetch_html(url, *, render_js=False, timeout=30) -> str
    extract_text(html, selector=None) -> str
    extract_links(html, base_url) -> list[str]
    extract_meta(html) -> dict   # title, description, og:* tags

Behaviour:
    - Realistic Chrome-on-Windows User-Agent.
    - 3x exponential backoff on 429 / 5xx via tenacity.
    - HEAD-checks robots.txt; warns but proceeds unless --strict.
    - --render flag triggers a LAZY playwright import (not at module level).
    - No LLM calls. Pure fetch + parse.

Dependencies:
    pip install httpx selectolax tenacity
    # optional, only for --render:
    pip install playwright && python -m playwright install chromium

CLI:
    python scripts/scrape.py <url>                    # HTML to stdout
    python scripts/scrape.py <url> --extract og       # OpenGraph tags as JSON
    python scripts/scrape.py <url> --extract meta     # full meta dict as JSON
    python scripts/scrape.py <url> --extract links    # newline-separated links
    python scripts/scrape.py <url> --extract text     # extracted body text
    python scripts/scrape.py <url> --selector "main"  # text inside selector
    python scripts/scrape.py <url> --strict           # abort if robots disallows
    python scripts/scrape.py <url> --render           # use playwright (lazy)
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from selectolax.parser import HTMLParser
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": CHROME_UA,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class RetryableHTTPError(Exception):
    """Raised on 429 / 5xx so tenacity retries."""


def _is_retryable_status(status: int) -> bool:
    return status == 429 or 500 <= status < 600


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((RetryableHTTPError, httpx.TransportError)),
)
def _get(url: str, timeout: int) -> httpx.Response:
    with httpx.Client(
        headers=DEFAULT_HEADERS,
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        resp = client.get(url)
        if _is_retryable_status(resp.status_code):
            raise RetryableHTTPError(f"{resp.status_code} for {url}")
        return resp


def _check_robots(url: str, timeout: int = 10) -> tuple[bool, str]:
    """Best-effort robots.txt check via HEAD (then GET if needed).

    Returns (allowed, message). Conservative: on any error we allow.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return True, ""
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        with httpx.Client(
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            head = client.head(robots_url)
            if head.status_code >= 400:
                return True, ""
            body = client.get(robots_url).text
    except httpx.HTTPError:
        return True, ""

    # Minimal Disallow check for User-agent: *
    path = parsed.path or "/"
    in_star = False
    for raw in body.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            in_star = value == "*"
        elif in_star and key == "disallow" and value:
            if path.startswith(value):
                return False, f"robots.txt disallows {value} for User-agent: *"
    return True, ""


def fetch_html(
    url: str,
    *,
    render_js: bool = False,
    timeout: int = 30,
) -> str:
    """Fetch and return HTML text. render_js=True triggers lazy playwright import."""
    if render_js:
        # Lazy import - we never load Playwright at module level.
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "render_js=True requires Playwright. Install with: "
                "pip install playwright && python -m playwright install chromium"
            ) from exc

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                ctx = browser.new_context(user_agent=CHROME_UA)
                page = ctx.new_page()
                page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
                return page.content()
            finally:
                browser.close()

    resp = _get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_text(html: str, selector: Optional[str] = None) -> str:
    tree = HTMLParser(html)
    if selector:
        node = tree.css_first(selector)
        if node is None:
            return ""
        return node.text(separator=" ", strip=True)
    body = tree.body
    if body is None:
        return tree.text(separator=" ", strip=True)
    return body.text(separator=" ", strip=True)


def extract_links(html: str, base_url: str) -> list[str]:
    tree = HTMLParser(html)
    out: list[str] = []
    seen: set[str] = set()
    for node in tree.css("a[href]"):
        href = node.attributes.get("href")
        if not href:
            continue
        href = href.strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        absolute = urljoin(base_url, href)
        if absolute not in seen:
            seen.add(absolute)
            out.append(absolute)
    return out


def extract_meta(html: str) -> dict:
    """Return a dict of title, description, and og:* / twitter:* tags."""
    tree = HTMLParser(html)
    meta: dict[str, str] = {}

    title_node = tree.css_first("title")
    if title_node is not None:
        meta["title"] = title_node.text(strip=True)

    for node in tree.css("meta"):
        attrs = node.attributes
        name = (attrs.get("name") or attrs.get("property") or "").strip().lower()
        content = attrs.get("content")
        if not name or content is None:
            continue
        if name == "description" or name.startswith("og:") or name.startswith("twitter:"):
            meta[name] = content.strip()

    return meta


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="scrape.py",
        description="Fetch a URL and optionally extract structured data.",
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument(
        "--extract",
        choices=["html", "og", "meta", "links", "text"],
        default="html",
        help="What to return (default: html)",
    )
    parser.add_argument(
        "--selector",
        default=None,
        help="CSS selector for --extract text",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Use Playwright for JS-rendered pages (lazy import)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Abort if robots.txt disallows the path",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])

    allowed, msg = _check_robots(args.url)
    if not allowed:
        if args.strict:
            sys.stderr.write(f"BLOCKED: {msg}\n")
            return 2
        sys.stderr.write(f"WARN: {msg} - proceeding anyway (no --strict)\n")

    try:
        html = fetch_html(args.url, render_js=args.render, timeout=args.timeout)
    except Exception as exc:  # noqa: BLE001 - CLI surface
        sys.stderr.write(f"ERROR fetching {args.url}: {exc}\n")
        return 1

    if args.extract == "html":
        sys.stdout.write(html)
        return 0

    if args.extract == "og":
        meta = extract_meta(html)
        og = {k: v for k, v in meta.items() if k.startswith("og:")}
        sys.stdout.write(json.dumps(og, indent=2, ensure_ascii=False))
        sys.stdout.write("\n")
        return 0

    if args.extract == "meta":
        meta = extract_meta(html)
        sys.stdout.write(json.dumps(meta, indent=2, ensure_ascii=False))
        sys.stdout.write("\n")
        return 0

    if args.extract == "links":
        for link in extract_links(html, args.url):
            sys.stdout.write(link + "\n")
        return 0

    if args.extract == "text":
        sys.stdout.write(extract_text(html, args.selector))
        sys.stdout.write("\n")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
