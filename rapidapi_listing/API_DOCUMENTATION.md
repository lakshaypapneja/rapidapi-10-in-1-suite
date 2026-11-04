# AI & Developer 10-in-1 Utility Suite

**One subscription. Ten production-ready APIs.** Built for AI engineers, SaaS founders, growth teams and automation builders (n8n, Make, Zapier).

- ⚡ Fast JSON responses, no third-party keys required
- 🔒 No data stored — every request is processed in memory and discarded
- 🧩 All endpoints use simple `POST` + JSON bodies

---

## Quick Start

```bash
curl -X POST "https://ai-developer-10-in-1-utility-suite.p.rapidapi.com/api/v1/web-to-markdown/extract" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
  -H "X-RapidAPI-Host: ai-developer-10-in-1-utility-suite.p.rapidapi.com" \
  -d '{"url": "https://example.com"}'
```

---

## The 10 APIs

| # | Endpoint | What it does | Typical use case |
|---|----------|--------------|------------------|
| 1 | `/api/v1/web-to-markdown/extract` | URL → clean Markdown + title, description, token count, links | RAG pipelines, AI agents, LLM context |
| 2 | `/api/v1/lead-extractor/enrich` | Domain → emails, phones, socials, tech stack, key pages | Sales prospecting, CRM enrichment |
| 3 | `/api/v1/seo-audit/analyze` | URL → 0-100 SEO score, grade, issues, AI-search (GEO) readiness | SEO tools, agency reports |
| 4 | `/api/v1/email-verify/check` | Email → syntax, live MX, disposable, free/role/B2B, typo fix, risk score | Signup forms, lead list cleaning |
| 5 | `/api/v1/youtube-intel/transcript` | YouTube URL → transcript, first-30s hook, WPM, timestamps | Content repurposing, video summarizers |
| 6 | `/api/v1/pii-redactor/sanitize` | Text → PII/secrets redacted + reversible token map | Safe LLM prompts, GDPR/HIPAA logging |
| 7 | `/api/v1/json-repair/repair` | Broken LLM output → valid JSON | LLM apps, agent tool-calling |
| 8 | `/api/v1/security-audit/evaluate` | Password entropy + crack time; scans text for leaked API keys | Signup flows, DevSecOps, log scanning |
| 9 | `/api/v1/cron-schedule/parse` | Cron or "every weekday at 9am" → explanation + next run times (any timezone) | Schedulers, workflow builders |
| 10 | `/api/v1/text-analytics/score` | Text → Flesch readability, grade level, sentiment, keyword density | Copywriting & content QA tools |

---

## Examples

### 1. Web2Markdown
**Request**
```json
{ "url": "https://example.com", "include_links": true, "include_images": false }
```
**Response (trimmed)**
```json
{
  "title": "Example Domain",
  "markdown": "# Example Domain\n\nThis domain is for use in illustrative examples...",
  "word_count": 28,
  "estimated_llm_tokens": 39,
  "reading_time_minutes": 0.14
}
```

### 2. B2B Lead Enrichment
**Request**
```json
{ "domain_or_url": "stripe.com" }
```
**Response (trimmed)**
```json
{
  "company_name": "Stripe",
  "emails": ["..."],
  "social_profiles": { "linkedin": ["https://www.linkedin.com/company/stripe"], "twitter_x": ["https://twitter.com/stripe"] },
  "detected_tech_stack": ["Next.js", "Stripe", "Google Analytics / GTM"],
  "important_pages": { "pricing": "https://stripe.com/pricing", "contact": "https://stripe.com/contact" }
}
```

### 4. Email Intelligence
**Request**
```json
{ "email": "john@gmial.com" }
```
**Response**
```json
{
  "is_valid_syntax": true,
  "has_mx_records": false,
  "is_disposable": false,
  "suggested_typo_fix": "john@gmail.com",
  "deliverability_risk_score": 100,
  "verdict": "undeliverable_no_mx"
}
```

### 6. PII Redactor
**Request**
```json
{ "text": "Email john@acme.com, card 4532-0151-1283-0366", "placeholder_style": "numbered" }
```
**Response**
```json
{
  "sanitized_text": "Email [EMAIL_1], card [CREDIT_CARD_1]",
  "redaction_map": { "[EMAIL_1]": "john@acme.com", "[CREDIT_CARD_1]": "4532-0151-1283-0366" },
  "total_redactions": 2
}
```

### 7. LLM JSON Repair
**Request**
```json
{ "raw_llm_output": "Sure! ```json\n{'name': 'Acme', 'active': True, 'tags': ['a','b',],}\n```" }
```
**Response**
```json
{
  "success": true,
  "parsed_data": { "name": "Acme", "active": true, "tags": ["a", "b"] },
  "repairs_applied": ["stripped_markdown_code_fences", "removed_trailing_commas", "normalized_python_literals", "converted_single_quoted_dict_to_json"]
}
```

### 9. Cron Parser
**Request**
```json
{ "expression_or_text": "every weekday at 9am", "timezone_name": "America/New_York", "next_runs_count": 3 }
```
**Response**
```json
{
  "cron_expression": "0 9 * * 1-5",
  "human_summary": "Runs at 09:00 Monday through Friday (weekdays)",
  "next_executions_iso": ["2026-11-04T09:00:00-05:00", "..."]
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad input (invalid URL, unreachable site, unknown timezone) |
| 404 | Resource not found (e.g. YouTube video has no transcript) |
| 422 | Validation error / JSON could not be repaired |
| 429 | Plan quota exceeded — upgrade your plan |

## Plans

| Plan | Price | Requests / month |
|------|-------|------------------|
| Basic | $0 | 100 |
| Pro | $9.99 | 5,000 |
| Ultra | $29.99 | 25,000 |
| Mega | $79.99 | 100,000 |

Need a higher volume or a custom endpoint? Use **Contact Provider**.
