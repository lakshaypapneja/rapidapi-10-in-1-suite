import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.main import app as full_app
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

SPECS_DIR = Path(__file__).parent / "openapi_specs"
SPECS_DIR.mkdir(exist_ok=True)

INDIVIDUAL_APIS = [
    (
        "01_web_to_markdown.json",
        "Web2Markdown & AI Context Extractor API",
        "Convert any URL into clean, token-efficient Markdown with metadata, reading time, and links for LLMs & RAG pipelines.",
        api_01_web_markdown.router,
    ),
    (
        "02_b2b_lead_extractor.json",
        "B2B Domain & Company Lead Enrichment API",
        "Extract emails, phone numbers, social media profiles, key pages, and tech stack from any company website.",
        api_02_lead_extractor.router,
    ),
    (
        "03_seo_and_geo_audit.json",
        "Technical SEO & AI Search (GEO) Audit API",
        "Audit any webpage for 0-100 Technical SEO score, meta tags, heading structure, JSON-LD schema, and AI-search readiness.",
        api_03_seo_audit.router,
    ),
    (
        "04_email_intelligence.json",
        "Disposable Email, MX DNS & B2B Verification API",
        "Validate email syntax, live MX DNS records, disposable email providers, role accounts, and typo suggestions.",
        api_04_email_intel.router,
    ),
    (
        "05_youtube_transcript_intel.json",
        "YouTube Transcript, Hook & Pacing Extractor API",
        "Fetch full YouTube transcripts, first-30-second viral hooks, word counts, and speaking pace (WPM) without an API key.",
        api_05_youtube_intel.router,
    ),
    (
        "06_llm_pii_redactor.json",
        "Smart PII Redaction & LLM Prompt Sanitizer API",
        "Detect and redact emails, phones, SSNs, credit cards, IP addresses, and API keys from text before sending to LLMs.",
        api_06_pii_redactor.router,
    ),
    (
        "07_llm_json_repair.json",
        "LLM Broken JSON Repair & Extractor API",
        "Deterministically strip markdown fences, conversational chatter, trailing commas, and single quotes to repair broken LLM JSON.",
        api_07_json_repair.router,
    ),
    (
        "08_security_entropy_audit.json",
        "Password Entropy & Secret Leak Scanner API",
        "Calculate Shannon entropy, GPU crack time, and scan code/text snippets for accidentally leaked API keys and tokens.",
        api_08_security_audit.router,
    ),
    (
        "09_cron_schedule_parser.json",
        "Universal Cron & Natural Language Schedule API",
        "Convert cron expressions or English phrases into human-readable summaries and calculate exact upcoming run timestamps across timezones.",
        api_09_cron_schedule.router,
    ),
    (
        "10_text_readability_analytics.json",
        "Readability, Keyword Density & Sentiment Scorer API",
        "Compute Flesch-Kincaid grade level, reading ease, lexical diversity, sentiment polarity, and top SEO keyword density.",
        api_10_text_analytics.router,
    ),
]


def export_all_specs():
    live_servers = [{"url": "https://rapidapi-10-in-1-suite.onrender.com", "description": "Production Render Cloud Server"}]

    # 1. Export unified bundle spec
    bundle_schema = get_openapi(
        title=full_app.title,
        version="1.0.0",
        openapi_version="3.0.3",
        description=full_app.description,
        routes=full_app.routes,
        servers=live_servers,
    )
    bundle_path = SPECS_DIR / "all_10_apis_bundle.json"
    bundle_path.write_text(json.dumps(bundle_schema, indent=2))
    print(f"Exported: {bundle_path.name}")

    # 2. Export 10 standalone OpenAPI 3.0.3 specs for RapidAPI 1-click import
    for filename, title, description, router in INDIVIDUAL_APIS:
        sub_app = FastAPI(title=title, description=description, version="1.0.0")
        sub_app.include_router(router)
        schema = get_openapi(
            title=title,
            version="1.0.0",
            openapi_version="3.0.3",
            description=description,
            routes=sub_app.routes,
            servers=live_servers,
        )
        out_path = SPECS_DIR / filename
        out_path.write_text(json.dumps(schema, indent=2))
        print(f"Exported: {out_path.name}")


if __name__ == "__main__":
    export_all_specs()
