import re
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/web-to-markdown",
    tags=["1. Web2Markdown & AI Context Extractor"],
)


class WebToMarkdownRequest(BaseModel):
    url: str = Field(
        default="https://example.com",
        description="Target webpage URL to scrape and convert into clean LLM-ready Markdown.",
    )
    include_links: bool = Field(
        default=True,
        description="Whether to preserve hyperlinks in the Markdown output.",
    )
    include_images: bool = Field(
        default=False,
        description="Whether to include image Markdown tags.",
    )


class WebToMarkdownResponse(BaseModel):
    url: str
    title: str
    description: str
    markdown: str
    word_count: int
    estimated_llm_tokens: int
    reading_time_minutes: float
    links_extracted: list[dict[str, str]]


def _html_to_clean_markdown(
    soup: BeautifulSoup, base_url: str, include_links: bool, include_images: bool
) -> str:
    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "iframe",
            "svg",
            "canvas",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
        ]
    ):
        tag.decompose()

    lines: list[str] = []
    root = soup.find("main") or soup.find("article") or soup.body or soup

    for elem in root.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "pre", "img"]
    ):
        name = elem.name
        if name == "img":
            if include_images:
                src = elem.get("src")
                if src:
                    alt = (elem.get("alt") or "image").strip()
                    lines.append(f"![{alt}]({urljoin(base_url, src)})")
            continue

        text = elem.get_text(" ", strip=True)
        if not text:
            continue

        if include_links and name in ("p", "li"):
            for a in elem.find_all("a", href=True):
                link_text = a.get_text(" ", strip=True)
                href = urljoin(base_url, a["href"])
                if link_text and href.startswith("http"):
                    text = text.replace(link_text, f"[{link_text}]({href})", 1)

        if name.startswith("h") and len(name) == 2 and name[1].isdigit():
            level = int(name[1])
            lines.append(f"\n{'#' * level} {text}\n")
        elif name == "li":
            lines.append(f"- {text}")
        elif name == "blockquote":
            lines.append(f"> {text}")
        elif name == "pre":
            lines.append(f"\n```\n{elem.get_text()}\n```\n")
        else:
            lines.append(text)

    markdown = "\n\n".join(lines)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    return markdown


@router.post(
    "/extract",
    response_model=WebToMarkdownResponse,
    summary="Convert any URL to clean LLM-ready Markdown & metadata",
)
async def extract_markdown(payload: WebToMarkdownRequest):
    url = payload.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {exc}")

    soup = BeautifulSoup(resp.text, "lxml")
    title = (soup.title.string if soup.title and soup.title.string else "").strip()
    meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if not meta_desc_tag:
        meta_desc_tag = soup.find(
            "meta", attrs={"property": re.compile(r"^og:description$", re.I)}
        )
    description = (meta_desc_tag.get("content", "") if meta_desc_tag else "").strip()

    links: list[dict[str, str]] = []
    seen_hrefs: set[str] = set()
    for a in soup.find_all("a", href=True):
        full_href = urljoin(str(resp.url), a["href"])
        if full_href.startswith(("http://", "https://")) and full_href not in seen_hrefs:
            seen_hrefs.add(full_href)
            links.append(
                {
                    "text": a.get_text(" ", strip=True)[:100] or full_href,
                    "url": full_href,
                }
            )
            if len(links) >= 50:
                break

    markdown = _html_to_clean_markdown(
        soup, str(resp.url), payload.include_links, payload.include_images
    )
    words = len(markdown.split())
    estimated_tokens = max(1, int(len(markdown) / 4))
    reading_time = round(words / 200.0, 2)

    return WebToMarkdownResponse(
        url=str(resp.url),
        title=title,
        description=description,
        markdown=markdown,
        word_count=words,
        estimated_llm_tokens=estimated_tokens,
        reading_time_minutes=reading_time,
        links_extracted=links,
    )
