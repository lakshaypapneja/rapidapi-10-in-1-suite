import json
from pathlib import Path
from typing import Any
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

SPECS_DIR = Path(__file__).parent / "openapi_specs"
SPECS_DIR.mkdir(exist_ok=True)

INDIVIDUAL_APIS = [
    ("01_web_to_markdown.json", "Web2Markdown & AI Context Extractor API", "Convert any URL into clean, token-efficient Markdown with metadata, reading time, and links for LLMs & RAG pipelines.", api_01_web_markdown.router),
    ("02_b2b_lead_extractor.json", "B2B Domain & Company Lead Enrichment API", "Extract emails, phone numbers, social media profiles, key pages, and tech stack from any company website.", api_02_lead_extractor.router),
    ("03_seo_and_geo_audit.json", "Technical SEO & AI Search (GEO) Audit API", "Audit any webpage for 0-100 Technical SEO score, meta tags, heading structure, JSON-LD schema, and AI-search readiness.", api_03_seo_audit.router),
    ("04_email_intelligence.json", "Disposable Email, MX DNS & B2B Verification API", "Validate email syntax, live MX DNS records, disposable email providers, role accounts, and typo suggestions.", api_04_email_intel.router),
    ("05_youtube_transcript_intel.json", "YouTube Transcript, Hook & Pacing Extractor API", "Fetch full YouTube transcripts, first-30-second viral hooks, word counts, and speaking pace (WPM) without an API key.", api_05_youtube_intel.router),
    ("06_llm_pii_redactor.json", "Smart PII Redaction & LLM Prompt Sanitizer API", "Detect and redact emails, phones, SSNs, credit cards, IP addresses, and API keys from text before sending to LLMs.", api_06_pii_redactor.router),
    ("07_llm_json_repair.json", "LLM Broken JSON Repair & Extractor API", "Deterministically strip markdown fences, conversational chatter, trailing commas, and single quotes to repair broken LLM JSON.", api_07_json_repair.router),
    ("08_security_entropy_audit.json", "Password Entropy & Secret Leak Scanner API", "Calculate Shannon entropy, GPU crack time, and scan code/text snippets for accidentally leaked API keys and tokens.", api_08_security_audit.router),
    ("09_cron_schedule_parser.json", "Universal Cron & Natural Language Schedule API", "Convert cron expressions or English phrases into human-readable summaries and calculate exact upcoming run timestamps across timezones.", api_09_cron_schedule.router),
    ("10_text_readability_analytics.json", "Readability, Keyword Density & Sentiment Scorer API", "Compute Flesch-Kincaid grade level, reading ease, lexical diversity, sentiment polarity, and top SEO keyword density.", api_10_text_analytics.router),
    ("11_token_cost_estimator.json", "Token Counter & Multi-Model Cost Estimator API", "Calculate token count and pricing comparison across GPT-4o, Claude 3.5, and Gemini 1.5.", api_11_token_estimator.router),
    ("12_markdown_cleaner.json", "Markdown to Clean Text & TTS Formatter API", "Strip Markdown formatting, code fences, and tags to prepare clean text for text-to-speech audio engines.", api_12_markdown_cleaner.router),
    ("13_rag_chunker.json", "Text Chunking & RAG Document Splitter API", "Segment long documents into overlapping token-friendly chunks for vector databases.", api_13_rag_chunker.router),
    ("14_prompt_security.json", "Prompt Injection & Jailbreak Detector API", "Heuristic security scanner for adversarial attacks and prompt extraction attempts.", api_14_prompt_security.router),
    ("15_vector_math.json", "Embedding Vector Normalizer & Cosine Similarity API", "Compute dot products, cosine similarity, distance, and L2 normalization on embedding arrays.", api_15_vector_math.router),
    ("16_ai_citations.json", "AI Citation & Source Grounding Extractor API", "Extract URLs and footnote reference brackets from unstructured LLM generations.", api_16_ai_citations.router),
    ("17_prompt_hydrator.json", "System Prompt Template Hydrator & Validator API", "Safely hydrate {{variable}} prompt templates with missing placeholder detection.", api_17_prompt_hydrator.router),
    ("18_text_dedupe.json", "LLM Output Repetition & Loop Deduplicator API", "Detect and clean sentence and paragraph loops produced by generative models.", api_18_text_dedupe.router),
    ("19_regex_tester.json", "Regex Tester & Pattern Match Explainer API", "Validate regular expressions, extract match indices, and provide plain-English explanations.", api_19_regex_tester.router),
    ("20_code_detector.json", "Code Snippet Language & Runtime Detector API", "Identify programming language, target runtime, and structural properties of code snippets.", api_20_code_detector.router),
]


def _sanitize_for_rapidapi_oas30(node: Any) -> Any:
    if isinstance(node, list):
        return [_sanitize_for_rapidapi_oas30(item) for item in node]

    if not isinstance(node, dict):
        return node

    if "parameters" in node and isinstance(node["parameters"], list):
        filtered_params = [
            p
            for p in node["parameters"]
            if not (isinstance(p, dict) and p.get("name", "").lower() == "x-rapidapi-proxy-secret")
        ]
        if filtered_params:
            node["parameters"] = _sanitize_for_rapidapi_oas30(filtered_params)
        else:
            del node["parameters"]

    for union_key in ("anyOf", "oneOf"):
        if union_key in node and isinstance(node[union_key], list):
            items = node[union_key]
            non_null_items = [
                item
                for item in items
                if not (isinstance(item, dict) and item.get("type") == "null")
            ]
            has_null = len(non_null_items) < len(items)

            if len(non_null_items) == 0:
                del node[union_key]
                node["type"] = "string"
                node["nullable"] = True
            elif len(non_null_items) == 1:
                del node[union_key]
                single = _sanitize_for_rapidapi_oas30(non_null_items[0])
                for k, v in single.items():
                    if k not in node:
                        node[k] = v
                if has_null:
                    node["nullable"] = True
            else:
                node[union_key] = [_sanitize_for_rapidapi_oas30(i) for i in non_null_items]
                if has_null:
                    node["nullable"] = True

    for key, val in list(node.items()):
        if key == "type" and val == "null":
            node[key] = "string"
            node["nullable"] = True
        else:
            node[key] = _sanitize_for_rapidapi_oas30(val)

    return node


def export_all_specs():
    live_servers = [
        {
            "url": "https://rapidapi-10-in-1-suite.onrender.com",
            "description": "Production Render Cloud Server",
        }
    ]

    bundle_schema = get_openapi(
        title=full_app.title,
        version="1.1.0",
        openapi_version="3.0.3",
        description=full_app.description,
        routes=full_app.routes,
        servers=live_servers,
    )
    bundle_schema = _sanitize_for_rapidapi_oas30(bundle_schema)
    bundle_path = SPECS_DIR / "all_10_apis_bundle.json"
    bundle_path.write_text(json.dumps(bundle_schema, indent=2))
    print(f"Exported bundle: {bundle_path.name}")

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
        schema = _sanitize_for_rapidapi_oas30(schema)
        out_path = SPECS_DIR / filename
        out_path.write_text(json.dumps(schema, indent=2))
        print(f"Exported: {out_path.name}")


if __name__ == "__main__":
    export_all_specs()
