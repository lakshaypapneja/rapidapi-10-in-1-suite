import re
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/lead-extractor",
    tags=["2. B2B Domain & Company Lead Enrichment"],
)

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(
    r"(?:\+\d{1,3}[\s\-]?)?(?:\(\d{2,4}\)[\s\-]?|\d{2,4}[\s\-])\d{3,4}[\s\-]?\d{3,4}"
)

SOCIAL_PATTERNS = {
    "linkedin": re.compile(r"https?://(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_\-]+", re.I),
    "twitter_x": re.compile(r"https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+", re.I),
    "github": re.compile(r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_\-]+", re.I),
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.\-]+", re.I),
    "youtube": re.compile(r"https?://(?:www\.)?youtube\.com/(?:@|channel/|c/|user/)[a-zA-Z0-9_\-]+", re.I),
    "facebook": re.compile(r"https?://(?:www\.)?facebook\.com/[a-zA-Z0-9.\-]+", re.I),
}

TECH_SIGNATURES = {
    "Next.js": ["_next/static", "__NEXT_DATA__"],
    "React": ["react", "data-reactroot"],
    "Vue.js": ["__vue__", "vue.min.js", "data-v-"],
    "WordPress": ["wp-content", "wp-includes"],
    "Shopify": ["cdn.shopify.com", "Shopify.theme"],
    "Webflow": ["webflow.js", "data-wf-site"],
    "Stripe": ["js.stripe.com"],
    "Google Analytics / GTM": ["googletagmanager.com", "google-analytics.com", "gtag("],
    "HubSpot": ["js.hs-scripts.com", "hs-analytics"],
    "Intercom": ["widget.intercom.io", "Intercom("],
    "Cloudflare": ["cdnjs.cloudflare.com", "__cf_bm"],
    "Tailwind CSS": ["tailwind"],
}


class LeadExtractRequest(BaseModel):
    domain_or_url: str = Field(
        default="https://stripe.com",
        description="Company domain or website URL to extract B2B contact leads, socials, and tech stack.",
    )


class LeadExtractResponse(BaseModel):
    domain: str
    resolved_url: str
    company_name: str
    tagline_or_description: str
    emails: list[str]
    phone_numbers: list[str]
    social_profiles: dict[str, list[str]]
    detected_tech_stack: list[str]
    important_pages: dict[str, str]


@router.post(
    "/enrich",
    response_model=LeadExtractResponse,
    summary="Extract emails, phones, social profiles, and tech stack from any company domain",
)
async def enrich_company_domain(payload: LeadExtractRequest):
    url = payload.domain_or_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {
        "User-Agent": (
            "Mozilla/Polite-B2B-Enricher/1.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to reach domain: {exc}")

    html = resp.text
    soup = BeautifulSoup(html, "lxml")
    parsed_url = urlparse(str(resp.url))
    domain = parsed_url.netloc

    raw_emails = set(EMAIL_REGEX.findall(html))
    ignore_ext = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".js", ".css", ".woff")
    clean_emails = sorted(
        e.lower()
        for e in raw_emails
        if not e.lower().endswith(ignore_ext) and not e.lower().startswith("example@")
    )[:25]

    text_content = soup.get_text(" ", strip=True)
    raw_phones = set(PHONE_REGEX.findall(text_content))
    clean_phones = sorted(
        p.strip() for p in raw_phones if 7 <= sum(c.isdigit() for c in p) <= 15
    )[:15]

    socials: dict[str, list[str]] = {}
    for platform, pattern in SOCIAL_PATTERNS.items():
        matches = sorted(set(pattern.findall(html)))
        if matches:
            socials[platform] = matches[:5]

    detected_tech: list[str] = []
    server_header = resp.headers.get("server", "")
    if "cloudflare" in server_header.lower():
        detected_tech.append("Cloudflare")
    if "vercel" in server_header.lower() or "x-vercel-id" in resp.headers:
        detected_tech.append("Vercel")

    for tech_name, markers in TECH_SIGNATURES.items():
        if any(marker.lower() in html.lower() for marker in markers):
            if tech_name not in detected_tech:
                detected_tech.append(tech_name)

    important_pages: dict[str, str] = {}
    page_keywords = {
        "pricing": ["pricing", "plans"],
        "about": ["about", "company", "team"],
        "contact": ["contact", "support", "talk-to-sales"],
        "careers": ["careers", "jobs", "hiring"],
        "privacy": ["privacy"],
        "blog": ["blog", "news", "resources"],
    }
    for a in soup.find_all("a", href=True):
        href_lower = a["href"].lower()
        full_url = urljoin(str(resp.url), a["href"])
        for category, kws in page_keywords.items():
            if category not in important_pages and any(kw in href_lower for kw in kws):
                important_pages[category] = full_url

    og_site = soup.find("meta", attrs={"property": "og:site_name"})
    title_str = (soup.title.string if soup.title and soup.title.string else "").strip()
    company_name = (
        og_site["content"].strip()
        if og_site and og_site.get("content")
        else title_str.split("|")[0].split("-")[0].strip() or domain
    )

    desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    tagline = (desc_tag.get("content", "") if desc_tag else "").strip()

    return LeadExtractResponse(
        domain=domain,
        resolved_url=str(resp.url),
        company_name=company_name,
        tagline_or_description=tagline,
        emails=clean_emails,
        phone_numbers=clean_phones,
        social_profiles=socials,
        detected_tech_stack=detected_tech,
        important_pages=important_pages,
    )
