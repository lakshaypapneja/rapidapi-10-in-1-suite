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
    api_11_token_estimator,
    api_12_markdown_cleaner,
    api_13_rag_chunker,
    api_14_prompt_security,
    api_15_vector_math,
    api_16_ai_citations,
    api_17_prompt_hydrator,
    api_18_text_dedupe,
    api_19_regex_tester,
    api_20_code_detector,
)
from app.security import verify_rapidapi_secret

app = FastAPI(
    title="AI & Developer 20-in-1 Utility Suite (RapidAPI Ready)",
    description=(
        "Production-ready collection of 20 high-demand APIs built for RapidAPI monetization with $0.00 COGS. "
        "Includes Web2Markdown, B2B Lead Enrichment, SEO Audit, Email Verifier, YouTube Transcript, "
        "PII Redactor, JSON Repair, Password Auditor, Cron Parser, Text Analytics, Token Cost Estimator, "
        "Markdown-to-TTS Cleaner, RAG Chunker, Prompt Injection Scanner, Vector Math, Citation Extractor, "
        "Prompt Template Hydrator, Text Deduplicator, Regex Tester, and Code Language Detector."
    ),
    version="1.1.0",
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
        "suite": "RapidAPI 20-in-1 Developer & AI Monetization Suite",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "total_apis": 20,
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
            {"id": 11, "name": "Token Counter & Multi-Model Cost Estimator", "endpoint": "/api/v1/token-cost-estimator/calculate"},
            {"id": 12, "name": "Markdown to Clean Plain Text & TTS Formatter", "endpoint": "/api/v1/markdown-cleaner/clean"},
            {"id": 13, "name": "Text Chunking & RAG Document Splitter", "endpoint": "/api/v1/rag-chunker/split"},
            {"id": 14, "name": "Prompt Injection & Jailbreak Detector", "endpoint": "/api/v1/prompt-security/scan"},
            {"id": 15, "name": "Embedding Vector Normalizer & Cosine Similarity", "endpoint": "/api/v1/vector-math/similarity"},
            {"id": 16, "name": "AI Citation & Source Grounding Extractor", "endpoint": "/api/v1/ai-citations/extract"},
            {"id": 17, "name": "System Prompt Template Hydrator & Validator", "endpoint": "/api/v1/prompt-hydrator/hydrate"},
            {"id": 18, "name": "LLM Output Loop & Repetition Deduplicator", "endpoint": "/api/v1/deduplicate-text/dedupe"},
            {"id": 19, "name": "Regex Tester & Pattern Match Explainer", "endpoint": "/api/v1/regex-tester/test"},
            {"id": 20, "name": "Code Snippet Language & Runtime Detector", "endpoint": "/api/v1/code-detector/detect"},
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
app.include_router(api_11_token_estimator.router)
app.include_router(api_12_markdown_cleaner.router)
app.include_router(api_13_rag_chunker.router)
app.include_router(api_14_prompt_security.router)
app.include_router(api_15_vector_math.router)
app.include_router(api_16_ai_citations.router)
app.include_router(api_17_prompt_hydrator.router)
app.include_router(api_18_text_dedupe.router)
app.include_router(api_19_regex_tester.router)
app.include_router(api_20_code_detector.router)
