from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


DEFAULT_SOURCE_URL = "https://appserver.coes.org.pe/waMediciones/Help"


@dataclass(frozen=True)
class CrawledPage:
    url: str
    title: str
    text: str


def normalize_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def fetch_html(url: str, timeout_seconds: float = 20.0) -> str:
    headers = {
        "User-Agent": (
            "coes-web-qa-api/0.1.0 "
            "(educational project; contact: github.com/RommelPa)"
        )
    }

    with httpx.Client(
        timeout=timeout_seconds,
        follow_redirects=True,
        headers=headers,
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def extract_text_from_html(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = ""
    if soup.title is not None:
        title = normalize_text(soup.title.get_text(" ", strip=True))

    main_content = (
        soup.find("div", class_="body-content")
        or soup.find("main")
        or soup.find("body")
        or soup
    )

    text = main_content.get_text("\n", strip=True)
    text = normalize_text(text)

    return title, text


def _is_allowed_help_url(url: str, expected_netloc: str, help_path: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return False

    if parsed.netloc != expected_netloc:
        return False

    return parsed.path.startswith(help_path)


def discover_help_links(html: str, base_url: str, help_path: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    parsed_base = urlparse(base_url)

    links: list[str] = []

    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()

        if not href or href.startswith(("mailto:", "javascript:")):
            continue

        absolute_url = urljoin(base_url, href)
        absolute_url, _fragment = urldefrag(absolute_url)

        if _is_allowed_help_url(
            absolute_url,
            expected_netloc=parsed_base.netloc,
            help_path=help_path,
        ):
            links.append(absolute_url)

    return sorted(set(links))


def crawl_website(
    start_url: str = DEFAULT_SOURCE_URL,
    max_pages: int = 80,
    timeout_seconds: float = 20.0,
) -> list[CrawledPage]:
    parsed_start = urlparse(start_url)
    help_path = parsed_start.path.rstrip("/")

    queue: deque[str] = deque([start_url])
    visited: set[str] = set()
    pages: list[CrawledPage] = []

    while queue and len(pages) < max_pages:
        current_url = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)

        html = fetch_html(current_url, timeout_seconds=timeout_seconds)
        title, text = extract_text_from_html(html)

        if len(text) >= 100:
            pages.append(CrawledPage(url=current_url, title=title, text=text))

        for link in discover_help_links(html, current_url, help_path):
            if link not in visited:
                queue.append(link)

    return pages