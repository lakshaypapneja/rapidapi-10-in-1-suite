# RapidAPI 10-in-1 Developer & AI Utility Suite

A production-ready FastAPI server hosting **10 high-demand APIs** with zero external paid API dependencies, plus standalone **OpenAPI 3.0.3 JSON specifications** in `openapi_specs/` for 1-click RapidAPI Studio import.

## Included APIs
1. **Web2Markdown & AI Context Extractor** (`POST /api/v1/web-to-markdown/extract`)
2. **B2B Domain & Company Lead Enrichment** (`POST /api/v1/lead-extractor/enrich`)
3. **Technical SEO & GEO (AI Search) Audit** (`POST /api/v1/seo-audit/analyze`)
4. **Disposable Email, MX DNS & B2B Intelligence** (`POST /api/v1/email-verify/check`)
5. **YouTube Transcript, Viral Hook & Pacing Extractor** (`POST /api/v1/youtube-intel/transcript`)
6. **Smart PII Redaction & LLM Sanitizer** (`POST /api/v1/pii-redactor/sanitize`)
7. **LLM Output Repair & Messy JSON Parser** (`POST /api/v1/json-repair/repair`)
8. **Password Entropy & Secret Leak Auditor** (`POST /api/v1/security-audit/evaluate`)
9. **Universal Cron, Natural Language Schedule & Timezone** (`POST /api/v1/cron-schedule/parse`)
10. **Readability, Sentiment & Content Quality Scorer** (`POST /api/v1/text-analytics/score`)

## Deploy to Render (1-Click)
1. Connect this GitHub repository on [Render.com](https://render.com) (**New +** -> **Web Service** or **Blueprint**).
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Optional Environment Variable: `RAPIDAPI_PROXY_SECRET` (from your RapidAPI Studio -> Gateway settings).
