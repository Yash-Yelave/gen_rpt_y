from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    query: str


@dataclass
class SourceDocument:
    title: str
    url: str
    query: str
    snippet: str
    content: str


def search_web(query: str, max_results: int = 5) -> List[SearchResult]:
    url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    results: List[SearchResult] = []
    seen = set()

    for node in soup.select(".result"):
        anchor = node.select_one(".result__title a") or node.select_one("a.result__a") or node.find("a")
        if not anchor:
            continue
        href = anchor.get("href", "").strip()
        title = anchor.get_text(" ", strip=True)
        snippet_node = node.select_one(".result__snippet") or node.select_one(".snippet")
        snippet = snippet_node.get_text(" ", strip=True) if snippet_node else ""
        clean_url = _normalize_url(href)
        if not clean_url or clean_url in seen:
            continue
        seen.add(clean_url)
        results.append(SearchResult(title=title, url=clean_url, snippet=snippet, query=query))
        if len(results) >= max_results:
            break

    return results


def fetch_page_text(url: str, max_chars: int = 7000) -> str:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type and "xml" not in content_type:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe", "form"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    lines = []
    for tag_name in ["h1", "h2", "h3", "p", "li"]:
        for tag in soup.find_all(tag_name):
            text = tag.get_text(" ", strip=True)
            text = re.sub(r"\s+", " ", text)
            if len(text) >= 40:
                lines.append(text)

    merged = "\n".join(lines)
    merged = re.sub(r"\n{3,}", "\n\n", merged)
    merged = merged[:max_chars]
    return f"{title}\n\n{merged}".strip()


def collect_sources(queries: List[str], per_query: int = 3, max_sources: int = 8) -> List[SourceDocument]:
    docs: List[SourceDocument] = []
    seen = set()

    for query in queries:
        try:
            search_results = search_web(query, max_results=per_query)
        except Exception:
            continue

        for result in search_results:
            if result.url in seen:
                continue
            seen.add(result.url)
            try:
                content = fetch_page_text(result.url)
            except Exception:
                content = ""
            if len(content) < 200:
                continue
            docs.append(
                SourceDocument(
                    title=result.title,
                    url=result.url,
                    query=result.query,
                    snippet=result.snippet,
                    content=content,
                )
            )
            if len(docs) >= max_sources:
                return docs

    return docs


def _normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return ""
    return url
