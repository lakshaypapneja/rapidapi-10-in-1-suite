import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_tests():
    # 0. Health & Root
    r0 = client.get("/")
    assert r0.status_code == 200, r0.text
    print("[PASS] 0. Root Catalog:", len(r0.json()["apis"]), "APIs registered")

    # 1. Web2Markdown
    r1 = client.post("/api/v1/web-to-markdown/extract", json={"url": "https://example.com"})
    assert r1.status_code == 200, r1.text
    print("[PASS] 1. Web2Markdown:", r1.json()["title"], "| Tokens:", r1.json()["estimated_llm_tokens"])

    # 2. B2B Lead Extractor
    r2 = client.post("/api/v1/lead-extractor/enrich", json={"domain_or_url": "https://example.com"})
    assert r2.status_code == 200, r2.text
    print("[PASS] 2. B2B Lead Extractor:", r2.json()["domain"])

    # 3. Technical SEO & GEO Audit
    r3 = client.post("/api/v1/seo-audit/analyze", json={"url": "https://example.com"})
    assert r3.status_code == 200, r3.text
    print("[PASS] 3. Technical SEO & GEO Audit Score:", r3.json()["overall_score"], "Grade:", r3.json()["grade"])

    # 4. Disposable Email & DNS MX Verification
    r4 = client.post("/api/v1/email-verify/check", json={"email": "founder@stripe.com"})
    assert r4.status_code == 200, r4.text
    print("[PASS] 4. Email Intelligence Verdict:", r4.json()["verdict"], "| MX:", r4.json()["has_mx_records"])

    # 5. YouTube Transcript & Viral Hook Extractor (check endpoint validation / structure)
    r5 = client.post("/api/v1/youtube-intel/transcript", json={"video_url_or_id": "not-a-valid-youtube-url"})
    assert r5.status_code == 400, r5.text
    print("[PASS] 5. YouTube Transcript & Hook Extractor route verified")

    # 6. Smart PII Redactor for LLMs
    r6 = client.post("/api/v1/pii-redactor/sanitize", json={})
    assert r6.status_code == 200, r6.text
    print("[PASS] 6. PII Redactor Redactions:", r6.json()["total_redactions"], r6.json()["counts_by_type"])

    # 7. LLM Broken JSON Repair
    r7 = client.post("/api/v1/json-repair/repair", json={})
    assert r7.status_code == 200, r7.text
    print("[PASS] 7. LLM JSON Repair Applied:", r7.json()["repairs_applied"])

    # 8. Password Entropy & Secret Leak Scanner
    r8 = client.post("/api/v1/security-audit/evaluate", json={})
    assert r8.status_code == 200, r8.text
    print("[PASS] 8. Security Audit Entropy:", r8.json()["entropy_bits"], "bits | Leaks found:", len(r8.json()["leaked_secrets_detected"]))

    # 9. Universal Cron & Natural Language Schedule
    r9 = client.post("/api/v1/cron-schedule/parse", json={"expression_or_text": "every weekday at 9am", "timezone_name": "Asia/Kolkata"})
    assert r9.status_code == 200, r9.text
    print("[PASS] 9. Cron Schedule Summary:", r9.json()["human_summary"])

    # 10. Readability, Keyword Density & Sentiment Scorer
    r10 = client.post("/api/v1/text-analytics/score", json={})
    assert r10.status_code == 200, r10.text
    print("[PASS] 10. Text Analytics Reading Ease:", r10.json()["flesch_reading_ease"], "| Sentiment:", r10.json()["sentiment_label"])


if __name__ == "__main__":
    run_tests()
