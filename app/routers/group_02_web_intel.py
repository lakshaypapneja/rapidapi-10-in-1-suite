import re
from urllib.parse import urljoin, urlparse
import dns.resolver
from fastapi import APIRouter, HTTPException
import httpx
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/web-intel", tags=["Web & Domain Intelligence (APIs 21-35)"])

# 21. Sitemap & Robots.txt Parser
class RobotsRequest(BaseModel):
    domain_or_url: str = Field(default="https://example.com")

class RobotsResponse(BaseModel):
    robots_url: str
    sitemaps_found: list[str]
    disallowed_paths: list[str]
    crawl_delay: str | None

@router.post("/robots-parser", response_model=RobotsResponse, summary="21. Robots.txt and Sitemap Directives Parser")
async def parse_robots(payload: RobotsRequest):
    url = payload.domain_or_url if payload.domain_or_url.startswith("http") else f"https://{payload.domain_or_url}"
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(robots_url)
            lines = resp.text.split("\n") if resp.status_code == 200 else []
    except Exception:
        lines = []

    sitemaps = [l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("sitemap:")]
    disallows = [l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("disallow:") and len(l.split(":", 1)) > 1]
    delay = next((l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("crawl-delay:")), None)
    return RobotsResponse(robots_url=robots_url, sitemaps_found=sitemaps, disallowed_paths=disallows[:30], crawl_delay=delay)

# 22. OpenGraph & Social Preview Scraper
class OgRequest(BaseModel):
    url: str = Field(default="https://github.com")

class OgResponse(BaseModel):
    url: str
    title: str | None
    description: str | None
    image: str | None
    site_name: str | None
    card_type: str | None

@router.post("/opengraph-scraper", response_model=OgResponse, summary="22. OpenGraph & Twitter Card Preview Scraper")
async def scrape_opengraph(payload: OgRequest):
    url = payload.url if payload.url.startswith("http") else f"https://{payload.url}"
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; SocialPreview/1.0)"})
            html = resp.text
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {exc}")

    def get_meta(prop: str) -> str | None:
        m = re.search(rf'<meta[^>]+(?:property|name)=["\'](?:og:|twitter:)?{prop}["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if not m:
            m = re.search(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:|twitter:)?{prop}["\']', html, re.I)
        return m.group(1).strip() if m else None

    return OgResponse(
        url=url,
        title=get_meta("title"),
        description=get_meta("description"),
        image=get_meta("image"),
        site_name=get_meta("site_name"),
        card_type=get_meta("card"),
    )

# 23. Favicon & Brand Asset Extractor
class FaviconRequest(BaseModel):
    domain_or_url: str = Field(default="https://stripe.com")

class FaviconResponse(BaseModel):
    domain: str
    favicons: list[str]

@router.post("/favicon-extractor", response_model=FaviconResponse, summary="23. Favicon, Apple Touch Icon & Logo Extractor")
async def extract_favicons(payload: FaviconRequest):
    url = payload.domain_or_url if payload.domain_or_url.startswith("http") else f"https://{payload.domain_or_url}"
    parsed = urlparse(url)
    default_icon = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
    icons = [default_icon]
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(url)
            matches = re.findall(r'<link[^>]+rel=["\'](?:shortcut icon|icon|apple-touch-icon)["\'][^>]+href=["\']([^"\']+)["\']', resp.text, re.I)
            for m in matches:
                full_icon = urljoin(url, m)
                if full_icon not in icons:
                    icons.append(full_icon)
    except Exception:
        pass
    return FaviconResponse(domain=parsed.netloc, favicons=icons)

# 24. DNS Lookup (A, AAAA, MX, TXT, NS, CNAME)
class DnsRequest(BaseModel):
    domain: str = Field(default="google.com")
    record_type: str = Field(default="A", description="A, AAAA, MX, TXT, NS, or CNAME")

class DnsResponse(BaseModel):
    domain: str
    record_type: str
    records: list[str]

@router.post("/dns-lookup", response_model=DnsResponse, summary="24. Universal DNS Record Resolver (A, MX, TXT, NS, etc.)")
async def resolve_dns(payload: DnsRequest):
    domain = re.sub(r"^https?://", "", payload.domain).split("/")[0]
    rec_type = payload.record_type.upper().strip()
    try:
        answers = dns.resolver.resolve(domain, rec_type, lifetime=5.0)
        recs = [str(r).strip() for r in answers]
    except Exception as exc:
        recs = []
    return DnsResponse(domain=domain, record_type=rec_type, records=recs)

# 25. Redirect Chain Tracer
class RedirectRequest(BaseModel):
    url: str = Field(default="https://bit.ly/3gXYZ")

class RedirectHop(BaseModel):
    status_code: int
    url: str

class RedirectResponse(BaseModel):
    initial_url: str
    final_url: str
    total_redirects: int
    chain: list[RedirectHop]

@router.post("/redirect-tracer", response_model=RedirectResponse, summary="25. HTTP 301/302 Redirect Chain and Affiliate Tracer")
async def trace_redirects(payload: RedirectRequest):
    url = payload.url if payload.url.startswith("http") else f"https://{payload.url}"
    chain: list[RedirectHop] = []
    current_url = url
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            for _ in range(10):
                resp = await client.get(current_url)
                chain.append(RedirectHop(status_code=resp.status_code, url=str(resp.url)))
                if resp.is_redirect and "location" in resp.headers:
                    current_url = urljoin(current_url, resp.headers["location"])
                else:
                    break
    except Exception:
        if not chain:
            chain.append(RedirectHop(status_code=0, url=url))
    return RedirectResponse(initial_url=url, final_url=chain[-1].url if chain else url, total_redirects=max(0, len(chain)-1), chain=chain)

# 26. SSL / TLS Certificate Checker
class SslRequest(BaseModel):
    domain: str = Field(default="github.com")

class SslResponse(BaseModel):
    domain: str
    is_https_supported: bool
    status_code: int | None
    hsts_enabled: bool

@router.post("/ssl-checker", response_model=SslResponse, summary="26. SSL / HTTPS Security & HSTS Header Verifier")
async def check_ssl(payload: SslRequest):
    domain = re.sub(r"^https?://", "", payload.domain).split("/")[0]
    https_url = f"https://{domain}"
    try:
        async with httpx.AsyncClient(timeout=8.0, verify=True) as client:
            resp = await client.get(https_url)
            hsts = "strict-transport-security" in resp.headers
            return SslResponse(domain=domain, is_https_supported=True, status_code=resp.status_code, hsts_enabled=hsts)
    except Exception:
        return SslResponse(domain=domain, is_https_supported=False, status_code=None, hsts_enabled=False)

# 27. HTTP Response Headers Inspector
class HeadersRequest(BaseModel):
    url: str = Field(default="https://example.com")

class HeadersResponse(BaseModel):
    url: str
    status_code: int
    headers: dict[str, str]

@router.post("/headers-inspector", response_model=HeadersResponse, summary="27. Raw HTTP Response Headers & Server Detector")
async def inspect_headers(payload: HeadersRequest):
    url = payload.url if payload.url.startswith("http") else f"https://{payload.url}"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.head(url)
            return HeadersResponse(url=url, status_code=resp.status_code, headers=dict(resp.headers))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

# 28. URL Query Parameter Parser & Formatter
class UrlParseRequest(BaseModel):
    url: str = Field(default="https://example.com/search?q=fastapi&sort=desc&limit=50#page2")

class UrlParseResponse(BaseModel):
    scheme: str
    domain: str
    path: str
    query_params: dict[str, str]
    fragment: str

@router.post("/url-parser", response_model=UrlParseResponse, summary="28. URL Parser & Query Parameter Deconstructor")
async def parse_url_components(payload: UrlParseRequest):
    p = urlparse(payload.url)
    from urllib.parse import parse_qsl
    q = dict(parse_qsl(p.query))
    return UrlParseResponse(scheme=p.scheme, domain=p.netloc, path=p.path, query_params=q, fragment=p.fragment)

# 29. Subdomain Extractor from Text
class DomainExtractRequest(BaseModel):
    text: str = Field(default="Visit api.stripe.com, dashboard.render.com and staging.app.io")

class DomainExtractResponse(BaseModel):
    total_found: int
    domains: list[str]

@router.post("/domain-extractor", response_model=DomainExtractResponse, summary="29. Domain and Subdomain Regex Extractor")
async def extract_domains(payload: DomainExtractRequest):
    found = re.findall(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b", payload.text)
    unique = sorted(list(set(found)))
    return DomainExtractResponse(total_found=len(unique), domains=unique)

# 30. Broken Links Scanner (Page-level)
class BrokenLinkRequest(BaseModel):
    url: str = Field(default="https://example.com")

class LinkStatus(BaseModel):
    url: str
    status_code: int
    is_broken: bool

class BrokenLinkResponse(BaseModel):
    scanned_url: str
    total_links: int
    broken_count: int
    results: list[LinkStatus]

@router.post("/broken-link-checker", response_model=BrokenLinkResponse, summary="30. Single-Page Broken Link Status Scanner")
async def check_broken_links(payload: BrokenLinkRequest):
    url = payload.url if payload.url.startswith("http") else f"https://{payload.url}"
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)
            matches = re.findall(r'<a[^>]+href=["\'](https?://[^"\']+)["\']', resp.text)
            links = list(set(matches))[:8]  # Limit to 8 to keep response quick
            
            checked: list[LinkStatus] = []
            for l in links:
                try:
                    r = await client.head(l, timeout=4.0)
                    checked.append(LinkStatus(url=l, status_code=r.status_code, is_broken=r.status_code >= 400))
                except Exception:
                    checked.append(LinkStatus(url=l, status_code=0, is_broken=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    broken = sum(1 for c in checked if c.is_broken)
    return BrokenLinkResponse(scanned_url=url, total_links=len(checked), broken_count=broken, results=checked)

# 31. Canonical URL Resolver
class CanonicalRequest(BaseModel):
    url: str = Field(default="https://example.com/index.html?utm_source=twitter")

class CanonicalResponse(BaseModel):
    submitted_url: str
    clean_canonical_url: str
    stripped_params: list[str]

@router.post("/canonical-cleaner", response_model=CanonicalResponse, summary="31. Marketing & UTM Tracking Parameter Stripper")
async def clean_canonical(payload: CanonicalRequest):
    p = urlparse(payload.url)
    from urllib.parse import parse_qsl, urlencode
    TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid", "msclkid"}
    params = parse_qsl(p.query)
    clean_params = [(k, v) for k, v in params if k.lower() not in TRACKING]
    stripped = [k for k, v in params if k.lower() in TRACKING]
    clean_url = f"{p.scheme}://{p.netloc}{p.path}"
    if clean_params:
        clean_url += f"?{urlencode(clean_params)}"
    return CanonicalResponse(submitted_url=payload.url, clean_canonical_url=clean_url, stripped_params=stripped)

# 32. Email Deliverability MX Risk Scorer
class MxRiskRequest(BaseModel):
    domain: str = Field(default="gmail.com")

class MxRiskResponse(BaseModel):
    domain: str
    has_mx: bool
    mx_records: list[str]
    risk_level: str

@router.post("/mx-risk-scorer", response_model=MxRiskResponse, summary="32. Mail Exchanger (MX) Deliverability & Reputation Scorer")
async def score_mx_risk(payload: MxRiskRequest):
    dom = re.sub(r"^https?://", "", payload.domain).split("/")[0]
    try:
        ans = dns.resolver.resolve(dom, "MX", lifetime=4.0)
        mxs = [str(r.exchange).strip() for r in ans]
    except Exception:
        mxs = []
    risk = "LOW" if len(mxs) >= 2 else "MEDIUM" if len(mxs) == 1 else "CRITICAL"
    return MxRiskResponse(domain=dom, has_mx=len(mxs) > 0, mx_records=mxs[:5], risk_level=risk)

# 33. Tech Stack Detection (Quick Fingerprint)
class TechDetectRequest(BaseModel):
    headers_json: dict[str, str] = Field(default={"server": "cloudflare", "x-powered-by": "Express"})

class TechDetectResponse(BaseModel):
    detected_technologies: list[str]

@router.post("/tech-fingerprint", response_model=TechDetectResponse, summary="33. Server Header & Infrastructure Fingerprinter")
async def fingerprint_tech(payload: TechDetectRequest):
    detected: list[str] = []
    h = {k.lower(): v.lower() for k, v in payload.headers_json.items()}
    if "cloudflare" in h.get("server", ""): detected.append("Cloudflare CDN")
    if "nginx" in h.get("server", ""): detected.append("Nginx Web Server")
    if "apache" in h.get("server", ""): detected.append("Apache HTTP Server")
    if "express" in h.get("x-powered-by", ""): detected.append("Express.js (Node.js)")
    if "next" in h.get("x-powered-by", "") or "x-nextjs-cache" in h: detected.append("Next.js")
    if "vercel" in h.get("server", "") or "x-vercel-id" in h: detected.append("Vercel Cloud")
    return TechDetectResponse(detected_technologies=detected or ["Generic HTTP Server"])

# 34. WHOIS TLD & Root Domain Parser
class TldParseRequest(BaseModel):
    hostname: str = Field(default="sub.api.products.example.co.uk")

class TldParseResponse(BaseModel):
    raw_hostname: str
    root_domain: str
    tld: str
    subdomains: list[str]

@router.post("/domain-tld-parser", response_model=TldParseResponse, summary="34. Root Domain, Subdomain & Multi-Part TLD Parser")
async def parse_tld(payload: TldParseRequest):
    host = re.sub(r"^https?://", "", payload.hostname).split("/")[0].split(":")[0]
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in ("co", "com", "org", "net", "gov", "edu"):
        tld = ".".join(parts[-2:])
        root = parts[-3] + "." + tld
        subs = parts[:-3]
    elif len(parts) >= 2:
        tld = parts[-1]
        root = parts[-2] + "." + tld
        subs = parts[:-2]
    else:
        tld = ""
        root = host
        subs = []
    return TldParseResponse(raw_hostname=host, root_domain=root, tld=tld, subdomains=subs)

# 35. RSS & Atom XML Feed Parser
class RssRequest(BaseModel):
    feed_url: str = Field(default="https://news.ycombinator.com/rss")

class FeedItem(BaseModel):
    title: str
    link: str

class RssResponse(BaseModel):
    feed_url: str
    total_items: int
    items: list[FeedItem]

@router.post("/rss-feed-parser", response_model=RssResponse, summary="35. RSS and Atom XML Feed to Clean JSON Converter")
async def parse_rss(payload: RssRequest):
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(payload.feed_url)
            titles = re.findall(r'<item>[\s\S]*?<title>([^<]+)</title>[\s\S]*?<link>([^<]+)</link>', resp.text)
            items = [FeedItem(title=t.strip(), link=l.strip()) for t, l in titles[:15]]
            return RssResponse(feed_url=payload.feed_url, total_items=len(items), items=items)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
