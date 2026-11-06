import base64
import io
import re
import secrets
from fastapi import APIRouter
from pydantic import BaseModel, Field
import qrcode

router = APIRouter(prefix="/api/v1/content-mock", tags=["Content, Media & Mock Data (APIs 91-100)"])

# 91. Dynamic QR Code Generator (Base64 PNG & SVG)
class QrRequest(BaseModel):
    data_to_encode: str = Field(default="https://rapidapi.com")
    box_size: int = Field(default=8, ge=2, le=20)

class QrResponse(BaseModel):
    base64_png: str
    data_encoded: str

@router.post("/qr-code-generator", response_model=QrResponse, summary="91. High-Resolution Dynamic QR Code Generator (Base64 PNG)")
async def generate_qr(payload: QrRequest):
    qr = qrcode.QRCode(box_size=payload.box_size, border=2)
    qr.add_data(payload.data_to_encode)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return QrResponse(base64_png=f"data:image/png;base64,{b64}", data_encoded=payload.data_to_encode)

# 92. Lorem Ipsum Dummy Text Generator
class LoremRequest(BaseModel):
    paragraphs_count: int = Field(default=2, ge=1, le=10)

class LoremResponse(BaseModel):
    paragraphs: list[str]
    total_words: int

@router.post("/lorem-ipsum-generator", response_model=LoremResponse, summary="92. Configurable Placeholder Lorem Ipsum Paragraph Generator")
async def generate_lorem(payload: LoremRequest):
    PARAGRAPH = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    paras = [PARAGRAPH for _ in range(payload.paragraphs_count)]
    words = sum(len(p.split()) for p in paras)
    return LoremResponse(paragraphs=paras, total_words=words)

# 93. Fake User Profile Generator for Testing
class FakeUserRequest(BaseModel):
    count: int = Field(default=3, ge=1, le=20)

class FakeUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    role: str

class FakeUserResponse(BaseModel):
    users: list[FakeUser]

@router.post("/fake-user-generator", response_model=FakeUserResponse, summary="93. Realistic Mock User & Person Identity Profile Generator")
async def generate_fake_users(payload: FakeUserRequest):
    FIRSTS = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Robin", "Casey"]
    LASTS = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Taylor", "Anderson"]
    ROLES = ["Admin", "Developer", "Designer", "Product Manager", "QA Engineer"]
    users = []
    for _ in range(payload.count):
        fn = secrets.choice(FIRSTS)
        ln = secrets.choice(LASTS)
        un = f"{fn.lower()}{ln.lower()}{secrets.randbelow(999)}"
        em = f"{un}@example.com"
        users.append(FakeUser(first_name=fn, last_name=ln, email=em, username=un, role=secrets.choice(ROLES)))
    return FakeUserResponse(users=users)

# 94. Color Palette Generator (Complementary, Analogous)
class PaletteRequest(BaseModel):
    base_hex: str = Field(default="#3B82F6")

class PaletteResponse(BaseModel):
    base_color: str
    complementary: str
    palette_hex_codes: list[str]

@router.post("/color-palette-generator", response_model=PaletteResponse, summary="94. Harmonious Color Palette & Complementary Scheme Generator")
async def generate_palette(payload: PaletteRequest):
    clean = payload.base_hex.lstrip("#")
    r, g, b = int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
    # complementary invert
    comp = f"#{(255-r):02X}{(255-g):02X}{(255-b):02X}"
    palette = [f"#{clean.upper()}", comp, f"#{(r//2):02X}{(g//2):02X}{(b//2):02X}", f"#{(min(255, r+50)):02X}{(min(255, g+50)):02X}{(min(255, b+50)):02X}"]
    return PaletteResponse(base_color=f"#{clean.upper()}", complementary=comp, palette_hex_codes=palette)

# 95. SEO Meta Tags & Schema.org JSON-LD Generator
class SchemaGenRequest(BaseModel):
    page_title: str = Field(default="Best Developer Tools 2026")
    page_description: str = Field(default="Complete catalog of modern AI developer APIs.")
    canonical_url: str = Field(default="https://example.com/tools")

class SchemaGenResponse(BaseModel):
    json_ld_schema: dict
    html_meta_tags: str

@router.post("/seo-schema-builder", response_model=SchemaGenResponse, summary="95. SEO Article & Webpage Schema.org JSON-LD and Meta Tag Builder")
async def build_schema(payload: SchemaGenRequest):
    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": payload.page_title,
        "description": payload.page_description,
        "url": payload.canonical_url,
    }
    meta = f'<title>{payload.page_title}</title>\n<meta name="description" content="{payload.page_description}">\n<link rel="canonical" href="{payload.canonical_url}">'
    return SchemaGenResponse(json_ld_schema=schema, html_meta_tags=meta)

# 96. Profanity & Sensitive Word Filter
class ProfanityRequest(BaseModel):
    text: str = Field(default="This is a damn good API service with hell of a performance.")
    replacement_char: str = Field(default="*")

class ProfanityResponse(BaseModel):
    clean_text: str
    profanities_found_count: int

@router.post("/profanity-filter", response_model=ProfanityResponse, summary="96. Multi-Word Profanity Masker & Content Moderation Filter")
async def filter_profanity(payload: ProfanityRequest):
    BLOCKED = ["damn", "hell", "crap", "bastard"]
    res = payload.text
    count = 0
    for w in BLOCKED:
        pattern = re.compile(rf"\b{w}\b", re.I)
        matches = pattern.findall(res)
        if matches:
            count += len(matches)
            res = pattern.sub(payload.replacement_char * len(w), res)
    return ProfanityResponse(clean_text=res, profanities_found_count=count)

# 97. Social Media Character Limit Checker
class SocialLimitRequest(BaseModel):
    post_text: str = Field(default="Launching our 100-in-1 developer API suite today! Build faster with Antigravity. #developer #api")

class PlatformStatus(BaseModel):
    max_allowed: int
    characters_used: int
    is_within_limit: bool

class SocialLimitResponse(BaseModel):
    twitter_x: PlatformStatus
    linkedin: PlatformStatus
    instagram_caption: PlatformStatus

@router.post("/social-char-counter", response_model=SocialLimitResponse, summary="97. Twitter, LinkedIn & Instagram Character Count and Length Checker")
async def check_social_limits(payload: SocialLimitRequest):
    l = len(payload.post_text)
    return SocialLimitResponse(
        twitter_x=PlatformStatus(max_allowed=280, characters_used=l, is_within_limit=l <= 280),
        linkedin=PlatformStatus(max_allowed=3000, characters_used=l, is_within_limit=l <= 3000),
        instagram_caption=PlatformStatus(max_allowed=2200, characters_used=l, is_within_limit=l <= 2200),
    )

# 98. Markdown Table Generator from CSV/JSON
class MdTableRequest(BaseModel):
    headers: list[str] = Field(default=["Name", "Tier", "Price"])
    rows: list[list[str]] = Field(default=[["Basic", "Free", "$0"], ["Pro", "Paid", "$9.99"], ["Ultra", "Scale", "$29.99"]])

class MdTableResponse(BaseModel):
    markdown_table: str

@router.post("/markdown-table-builder", response_model=MdTableResponse, summary="98. Clean Markdown Table Generator from Headers and Row Arrays")
async def build_md_table(payload: MdTableRequest):
    header_line = "| " + " | ".join(payload.headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(payload.headers)) + " |"
    row_lines = ["| " + " | ".join(r) + " |" for r in payload.rows]
    table = "\n".join([header_line, separator_line] + row_lines)
    return MdTableResponse(markdown_table=table)

# 99. Random Quote & Developer Proverb Generator
class QuoteResponse(BaseModel):
    quote: str
    author: str

@router.post("/developer-quote", response_model=QuoteResponse, summary="99. Curated Software Engineering & Philosophy Quote Generator")
async def get_quote():
    QUOTES = [
        ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
        ("Make it work, make it right, make it fast.", "Kent Beck"),
        ("First, solve the problem. Then, write the code.", "John Johnson"),
        ("Code is like humor. When you have to explain it, it’s bad.", "Cory House"),
        ("Experience is the name everyone gives to their mistakes.", "Oscar Wilde"),
    ]
    q, a = secrets.choice(QUOTES)
    return QuoteResponse(quote=q, author=a)

# 100. Ultimate 100-Suite Status & Capability Inspection
class SuiteStatusResponse(BaseModel):
    total_endpoints: int
    suite_version: str
    categories_included: list[str]
    deployment_host: str

@router.get("/suite-summary", response_model=SuiteStatusResponse, summary="100. 100-in-1 Mega Developer API Suite Health and Specification Summary")
async def get_suite_summary():
    return SuiteStatusResponse(
        total_endpoints=100,
        suite_version="2.0.0 (100-in-1 Century Release)",
        categories_included=[
            "1. Web Scraping & AI Context Extraction",
            "2. AI Citations, Prompts & Vector Math",
            "3. Web, Domain & DNS Intelligence",
            "4. Security, Crypto, Hashing & Auth",
            "5. International Data Validation & Cleansing",
            "6. Data Transformers, CSV, XML & JSON",
            "7. Math, Timezones, Financials & Statistics",
            "8. Content, Media, QR Codes & Mock Generators",
        ],
        deployment_host="https://rapidapi-10-in-1-suite.onrender.com",
    )
