import json
import re
import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/seo-audit",
    tags=["3. Technical SEO & GEO (AI Search) Audit"],
)


class SeoAuditRequest(BaseModel):
    url: str = Field(
        default="https://example.com",
        description="URL of the webpage to run a full Technical SEO & AI-Search (GEO) audit on.",
    )


class SeoAuditResponse(BaseModel):
    url: str
    overall_score: int
    grade: str
    meta: dict[str, str | int | bool | None]
    headings_summary: dict[str, list[str]]
    images_audit: dict[str, int]
    links_audit: dict[str, int]
    structured_data_json_ld_count: int
    ai_geo_readiness: dict[str, bool | str]
    issues_and_recommendations: list[str]


@router.post(
    "/analyze",
    response_model=SeoAuditResponse,
    summary="Perform a 0-100 Technical SEO & AI Search (GEO) audit on any webpage",
)
async def analyze_seo(payload: SeoAuditRequest):
    url = payload.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SEOGeoAuditor/1.0)"},
            )
            resp.raise_for_status()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not fetch URL: {exc}")

    soup = BeautifulSoup(resp.text, "lxml")
    score = 100
    issues: list[str] = []

    title = (soup.title.string if soup.title and soup.title.string else "").strip()
    if not title:
        score -= 15
        issues.append("Missing <title> tag.")
    elif len(title) < 20 or len(title) > 65:
        score -= 5
        issues.append(f"Title length ({len(title)} chars) should ideally be between 30 and 60 chars.")

    desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    description = (desc_tag.get("content", "") if desc_tag else "").strip()
    if not description:
        score -= 15
        issues.append("Missing meta description tag.")
    elif len(description) < 50 or len(description) > 165:
        score -= 5
        issues.append(
            f"Meta description length ({len(description)} chars) should ideally be 70-160 chars."
        )

    canonical_tag = soup.find("link", rel=lambda x: x and "canonical" in x.lower())
    canonical = canonical_tag.get("href") if canonical_tag else None
    if not canonical:
        score -= 5
        issues.append("Missing canonical link tag (<link rel='canonical'>).")

    og_title = soup.find("meta", attrs={"property": "og:title"})
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if not og_title or not og_image:
        score -= 5
        issues.append("Incomplete OpenGraph tags (og:title or og:image missing).")

    headings: dict[str, list[str]] = {}
    for level in range(1, 5):
        tag_name = f"h{level}"
        headings[tag_name] = [
            h.get_text(" ", strip=True) for h in soup.find_all(tag_name) if h.get_text(strip=True)
        ][:15]

    h1_count = len(headings.get("h1", []))
    if h1_count == 0:
        score -= 15
        issues.append("No <h1> heading found on the page.")
    elif h1_count > 1:
        score -= 5
        issues.append(f"Multiple <h1> headings found ({h1_count}). Stick to a single primary H1.")

    images = soup.find_all("img")
    missing_alt = sum(1 for img in images if not (img.get("alt") or "").strip())
    if images and missing_alt > 0:
        score -= min(10, missing_alt * 2)
        issues.append(f"{missing_alt} of {len(images)} images are missing descriptive alt attributes.")

    json_ld_scripts = soup.find_all("script", type="application/ld+json")
    valid_json_ld = 0
    for script in json_ld_scripts:
        try:
            if script.string:
                json.loads(script.string)
                valid_json_ld += 1
        except Exception:
            pass

    if valid_json_ld == 0:
        score -= 10
        issues.append(
            "No Schema.org JSON-LD structured data found (critical for AI search engines & rich snippets)."
        )

    all_links = soup.find_all("a", href=True)
    internal_links = sum(1 for a in all_links if a["href"].startswith("/") or str(resp.url) in a["href"])
    external_links = max(0, len(all_links) - internal_links)

    viewport_tag = soup.find("meta", attrs={"name": "viewport"})
    has_viewport = viewport_tag is not None
    if not has_viewport:
        score -= 10
        issues.append("Missing responsive <meta name='viewport'> tag.")

    score = max(0, min(100, score))
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D"

    return SeoAuditResponse(
        url=str(resp.url),
        overall_score=score,
        grade=grade,
        meta={
            "title": title,
            "title_length": len(title),
            "description": description,
            "description_length": len(description),
            "canonical": canonical,
            "has_open_graph": bool(og_title and og_image),
            "has_viewport": has_viewport,
        },
        headings_summary=headings,
        images_audit={
            "total_images": len(images),
            "missing_alt_count": missing_alt,
        },
        links_audit={
            "total_links": len(all_links),
            "internal_links": internal_links,
            "external_links": external_links,
        },
        structured_data_json_ld_count=valid_json_ld,
        ai_geo_readiness={
            "has_structured_schema_org": valid_json_ld > 0,
            "clear_heading_hierarchy": h1_count == 1 and len(headings.get("h2", [])) > 0,
            "recommendation": (
                "Ready for AI Search / LLM citation"
                if valid_json_ld > 0 and h1_count == 1
                else "Add JSON-LD schema and clear H1/H2 Q&A sections to improve AI citation rates."
            ),
        },
        issues_and_recommendations=issues,
    )
