from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    api_01_web_markdown,
    api_02_lead_extractor,
    api_03_seo_audit,
    api_04_email_intel,
    api_05_youtube_intel,
    api_06_pii_redactor,
    api_07_json_repair,
    api_08_security_audit,
    api_09_cron_schedule,
    api_10_text_analytics,
)
from app.security import verify_rapidapi_secret

app = FastAPI(
    title="AI & Developer Utility 10-API Suite (RapidAPI Ready)",
    description=(
        "Production-ready collection of 10 high-demand APIs built for RapidAPI monetization. "
        "Includes Web2Markdown, B2B Lead Enrichment, Technical SEO & GEO Audit, Email Intelligence, "
        "YouTube Transcript & Hook Extractor, PII Redactor for LLMs, Broken JSON Repair, "
        "Password/Secret Leak Auditor, Universal Cron Parser, and Readability/Sentiment Scorer."
    ),
    version="1.0.0",
    dependencies=[Depends(verify_rapidapi_secret)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health & Catalog"])
async def root_catalog():
    return {
        "status": "online",
        "suite": "RapidAPI 10-in-1 Developer & AI Monetization Suite",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "apis": [
            {"id": 1, "name": "Web2Markdown & AI Context Extractor", "endpoint": "/api/v1/web-to-markdown/extract"},
            {"id": 2, "name": "B2B Domain & Company Lead Enrichment", "endpoint": "/api/v1/lead-extractor/enrich"},
            {"id": 3, "name": "Technical SEO & GEO (AI Search) Audit", "endpoint": "/api/v1/seo-audit/analyze"},
            {"id": 4, "name": "Disposable Email, Domain & Syntax Intelligence", "endpoint": "/api/v1/email-verify/check"},
            {"id": 5, "name": "YouTube Transcript, Metadata & Viral Hook Extractor", "endpoint": "/api/v1/youtube-intel/transcript"},
            {"id": 6, "name": "Smart PII Redaction & Data Sanitizer for LLMs", "endpoint": "/api/v1/pii-redactor/sanitize"},
            {"id": 7, "name": "LLM Output Repair & Messy JSON Parser", "endpoint": "/api/v1/json-repair/repair"},
            {"id": 8, "name": "Password Entropy & Secret Leak Auditor", "endpoint": "/api/v1/security-audit/evaluate"},
            {"id": 9, "name": "Universal Cron, Natural Language Schedule & Timezone", "endpoint": "/api/v1/cron-schedule/parse"},
            {"id": 10, "name": "Readability, Sentiment & Content Quality Scorer", "endpoint": "/api/v1/text-analytics/score"},
        ],
    }


@app.get("/health", tags=["Health & Catalog"])
async def health_check():
    return {"status": "healthy"}


app.include_router(api_01_web_markdown.router)
app.include_router(api_02_lead_extractor.router)
app.include_router(api_03_seo_audit.router)
app.include_router(api_04_email_intel.router)
app.include_router(api_05_youtube_intel.router)
app.include_router(api_06_pii_redactor.router)
app.include_router(api_07_json_repair.router)
app.include_router(api_08_security_audit.router)
app.include_router(api_09_cron_schedule.router)
app.include_router(api_10_text_analytics.router)
