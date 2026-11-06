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
    group_02_web_intel,
    group_03_security,
    group_04_validation,
    group_05_transformers,
    group_06_math_calc,
    group_07_content_mock,
)
from app.security import verify_rapidapi_secret

app = FastAPI(
    title="AI & Developer 100-in-1 Mega Utility Suite (RapidAPI Ready)",
    description=(
        "The ultimate 100-in-1 developer utility suite for AI engineers, SaaS founders, and automation builders. "
        "Includes Web Scraping, AI Agents/RAG tools, Security/Crypto, Phone/IBAN/Card Validation, Format Converters, "
        "Math/Finance, QR Code generation, Mock Data, and more — all with zero external dependencies and 100% profit margin."
    ),
    version="2.0.0",
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
        "suite": "RapidAPI 100-in-1 Mega Developer & AI Monetization Suite",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "total_apis": 100,
        "version": "2.0.0",
    }


@app.get("/health", tags=["Health & Catalog"])
async def health_check():
    return {"status": "healthy"}


# Mount Initial 20 Routers
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

# Mount 80 Additional Routers (Groups 02 to 07 -> Total 100 APIs)
app.include_router(group_02_web_intel.router)
app.include_router(group_03_security.router)
app.include_router(group_04_validation.router)
app.include_router(group_05_transformers.router)
app.include_router(group_06_math_calc.router)
app.include_router(group_07_content_mock.router)
