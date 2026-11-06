# AI & Developer 100-in-1 Mega Utility Suite

**One subscription. 100 production-ready APIs.** Built for AI engineers, SaaS founders, growth teams, and automation developers (n8n, Make, Zapier, LangChain).

- ⚡ High-speed in-memory execution (sub-150ms average latency)
- 🔒 Zero logs stored — completely stateless and secure
- 💰 Zero external API dependencies — 100% reliable uptime

---

## Complete Category Breakdown (100 Endpoints)

### 1. Web Scraping & AI Context Extraction (APIs 1-10)
- `POST /api/v1/web-to-markdown/extract` — URL to clean, token-efficient Markdown for LLMs & RAG.
- `POST /api/v1/lead-extractor/enrich` — Company website to emails, phones, socials, and tech stack.
- `POST /api/v1/seo-audit/analyze` — 0-100 Technical SEO & AI Search (GEO) audit score.
- `POST /api/v1/email-verify/check` — Syntax, live MX DNS, disposable detection, and typo fix.
- `POST /api/v1/youtube-intel/transcript` — YouTube video transcript, 30s viral hook, and WPM pace.
- `POST /api/v1/pii-redactor/sanitize` — Redact SSN, credit cards, emails, phones, and API keys.
- `POST /api/v1/json-repair/repair` — Fix unclosed brackets, markdown fences, and single quotes in broken LLM JSON.
- `POST /api/v1/security-audit/evaluate` — Password entropy, GPU crack time, and leaked token scanner.
- `POST /api/v1/cron-schedule/parse` — Plain English phrases or 5-field cron to next execution timestamps.
- `POST /api/v1/text-analytics/score` — Flesch-Kincaid readability, lexical diversity, and sentiment.

### 2. AI Prompt Engineering & Vector Tools (APIs 11-20)
- `POST /api/v1/token-cost-estimator/calculate` — Token counts and cost projections across GPT-4o, Claude 3.5, and Gemini 1.5.
- `POST /api/v1/markdown-cleaner/clean` — Strip Markdown tags and code blocks into speech-ready plain text for TTS.
- `POST /api/v1/rag-chunker/split` — Sentence, paragraph, and sliding-window chunking for vector DBs.
- `POST /api/v1/prompt-security/scan` — Heuristic scanner for prompt injections, DAN personas, and jailbreaks.
- `POST /api/v1/vector-math/similarity` — Fast cosine similarity, distance, and dot products on vector arrays.
- `POST /api/v1/ai-citations/extract` — Extract citations, footnote references `[1]`, and URLs from AI text.
- `POST /api/v1/prompt-hydrator/hydrate` — Safely inject variables into `{{variable}}` prompt templates.
- `POST /api/v1/deduplicate-text/dedupe` — Clean repetitive loop hallucinations produced by smaller LLMs.
- `POST /api/v1/regex-tester/test` — Validate regular expressions with match ranges and token explanations.
- `POST /api/v1/code-detector/detect` — Detect language, runtime environment, and structure from code snippets.

### 3. Web & Domain Intelligence (APIs 21-35)
- `POST /api/v1/web-intel/robots-parser` — Extract sitemaps and disallowed paths from robots.txt.
- `POST /api/v1/web-intel/opengraph-scraper` — Extract OpenGraph image, title, and Twitter card previews.
- `POST /api/v1/web-intel/favicon-extractor` — Extract favicon.ico, Apple touch icons, and SVG logos.
- `POST /api/v1/web-intel/dns-lookup` — Resolve A, AAAA, MX, TXT, CNAME, and NS records.
- `POST /api/v1/web-intel/redirect-tracer` — Trace 301/302 redirect hops to final landing URLs.
- `POST /api/v1/web-intel/ssl-checker` — Check SSL support, HTTPS status, and HSTS security.
- `POST /api/v1/web-intel/headers-inspector` — Inspect raw HTTP response headers.
- `POST /api/v1/web-intel/url-parser` — Parse URL into domain, path, query parameters, and fragments.
- `POST /api/v1/web-intel/domain-extractor` — Extract unique domains and hostnames from unstructured text.
- `POST /api/v1/web-intel/broken-link-checker` — Scan page hyperlinks for HTTP 404/500 broken targets.
- `POST /api/v1/web-intel/canonical-cleaner` — Strip UTM tracking, fbclid, and gclid parameters.
- `POST /api/v1/web-intel/mx-risk-scorer` — Score domain mail exchanger risk and deliverability.
- `POST /api/v1/web-intel/tech-fingerprint` — Identify web servers (Cloudflare, Nginx, Express, Vercel).
- `POST /api/v1/web-intel/domain-tld-parser` — Extract root domain, multi-part TLD (`.co.uk`), and subdomains.
- `POST /api/v1/web-intel/rss-feed-parser` — Parse RSS and Atom XML feeds into clean JSON.

### 4. Security, Cryptography & Auth (APIs 36-50)
- `POST /api/v1/security/hash-generator` — Generate MD5, SHA-1, SHA-256, and SHA-512 hashes.
- `POST /api/v1/security/hmac-signer` — Generate HMAC signatures for webhook authentication.
- `POST /api/v1/security/jwt-decoder` — Decode JWT headers and claims without secret key.
- `POST /api/v1/security/api-key-generator` — Cryptographically secure API keys and tokens.
- `POST /api/v1/security/uuid-generator` — Generate cryptographically secure UUID v4 identifiers.
- `POST /api/v1/security/uuid-validator` — Validate UUID syntax, version, and variant.
- `POST /api/v1/security/password-generator` — Generate passwords with customizable policies.
- `POST /api/v1/security/base64-converter` — Encode and decode UTF-8 Base64 strings.
- `POST /api/v1/security/hex-converter` — Encode and decode Hexadecimal strings.
- `POST /api/v1/security/url-encoder-decoder` — RFC 3986 percent-encoding encoder/decoder.
- `POST /api/v1/security/rot13-cipher` — Reversible ROT13 obfuscation cipher.
- `POST /api/v1/security/passphrase-generator` — Diceware-style memorizable passphrase generator.
- `POST /api/v1/security/security-headers-scanner` — Audit HSTS, CSP, and X-Frame-Options headers.
- `POST /api/v1/security/sqli-detector` — Scan strings for SQL injection signatures.
- `POST /api/v1/security/xss-detector` — Scan input text for Cross-Site Scripting (XSS) payloads.

### 5. International Data Validation & Cleansing (APIs 51-65)
- `POST /api/v1/validation/phone-validator` — International phone validation and E.164 formatting.
- `POST /api/v1/validation/credit-card-validator` — Luhn checksum validation and card brand detection.
- `POST /api/v1/validation/iban-validator` — International Bank Account Number (IBAN) checksum verification.
- `POST /api/v1/validation/ip-validator` — IPv4, IPv6, and CIDR range private/loopback inspector.
- `POST /api/v1/validation/user-agent-parser` — Extract browser, OS, and device family from user agents.
- `POST /api/v1/validation/semver-comparator` — Compare and validate Semantic Versions (SemVer).
- `POST /api/v1/validation/mac-address-formatter` — Validate and format MAC addresses into canonical format.
- `POST /api/v1/validation/iso-date-validator` — Validate ISO 8601 timestamps and convert to Unix epoch.
- `POST /api/v1/validation/color-converter` — Convert between HEX, RGB, and HSL color formats.
- `POST /api/v1/validation/text-normalizer` — Strip excessive spaces, tabs, and duplicate line breaks.
- `POST /api/v1/validation/isbn-validator` — Validate ISBN-10 and ISBN-13 book barcodes.
- `POST /api/v1/validation/mime-detector` — Identify standard IANA MIME types from file extensions.
- `POST /api/v1/validation/json-validator` — Validate JSON syntax and return structural types.
- `POST /api/v1/validation/postal-code-validator` — International postal code syntax validator.
- `POST /api/v1/validation/geo-coordinate-validator` — Latitude/Longitude boundary and hemisphere inspector.

### 6. Data Transformers & Converters (APIs 66-80)
- `POST /api/v1/transformers/json-to-csv` — Flatten JSON array into standard tabular CSV.
- `POST /api/v1/transformers/csv-to-json` — Convert CSV text into structured JSON records.
- `POST /api/v1/transformers/yaml-to-json` — Convert YAML configuration into formatted JSON.
- `POST /api/v1/transformers/json-to-yaml` — Convert JSON object into clean YAML.
- `POST /api/v1/transformers/xml-to-json` — Convert XML into structured JSON.
- `POST /api/v1/transformers/html-table-to-json` — Scrape and extract HTML `<table>` into JSON arrays.
- `POST /api/v1/transformers/text-case-converter` — Convert between camelCase, snake_case, kebab-case, and PascalCase.
- `POST /api/v1/transformers/json-formatter` — Minify or beautify JSON with byte-saving metrics.
- `POST /api/v1/transformers/sql-formatter` — Uppercase SQL keywords and clean indentation.
- `POST /api/v1/transformers/markdown-to-html` — Convert Markdown into semantic HTML.
- `POST /api/v1/transformers/binary-converter` — Convert 8-bit binary to text and vice versa.
- `POST /api/v1/transformers/json-flattener` — Flatten nested JSON into dot-notation keys.
- `POST /api/v1/transformers/word-frequency-counter` — Count and rank term frequencies in text.
- `POST /api/v1/transformers/slug-generator` — Generate SEO-friendly URL slugs with diacritic removal.
- `POST /api/v1/transformers/text-diff` — Unified diff comparison between two text blocks.

### 7. Math, Timezones & Financial Calculations (APIs 81-90)
- `POST /api/v1/math-calc/timezone-converter` — Convert timestamps across any IANA timezone.
- `POST /api/v1/math-calc/unit-converter` — Distance, weight, temperature, and data size converter.
- `POST /api/v1/math-calc/compound-interest` — Future value and compound interest calculator.
- `POST /api/v1/math-calc/loan-amortization` — Loan and mortgage monthly payment breakdown.
- `POST /api/v1/math-calc/percentage-calculator` — Price discount, savings ratio, and percentage delta.
- `POST /api/v1/math-calc/descriptive-statistics` — Mean, median, variance, and standard deviation solver.
- `POST /api/v1/math-calc/byte-storage-formatter` — Convert byte counts into KB, MB, GB, and TB units.
- `POST /api/v1/math-calc/math-evaluator` — Safe AST-based algebraic expression evaluator.
- `POST /api/v1/math-calc/relative-time-formatter` — Convert timestamps to human phrases ("3 hours ago").
- `POST /api/v1/math-calc/geometry-calculator` — Area and perimeter solver for circles, rectangles, and triangles.

### 8. Content, Media & Mock Data Generators (APIs 91-100)
- `POST /api/v1/content-mock/qr-code-generator` — High-res dynamic QR code generator (Base64 PNG).
- `POST /api/v1/content-mock/lorem-ipsum-generator` — Placeholder lorem ipsum paragraph generator.
- `POST /api/v1/content-mock/fake-user-generator` — Realistic mock user profiles for testing.
- `POST /api/v1/content-mock/color-palette-generator` — Harmonious and complementary color schemes.
- `POST /api/v1/content-mock/seo-schema-builder` — Schema.org JSON-LD and HTML meta tag generator.
- `POST /api/v1/content-mock/profanity-filter` — Multi-word profanity masker and content moderation filter.
- `POST /api/v1/content-mock/social-char-counter` — Twitter, LinkedIn, and Instagram character length checker.
- `POST /api/v1/content-mock/markdown-table-builder` — Clean Markdown table builder from row arrays.
- `POST /api/v1/content-mock/developer-quote` — Curated computer science and engineering quotes.
- `GET /api/v1/content-mock/suite-summary` — 100-in-1 suite summary and status check.

---

## Plans & Pricing

| Plan | Price | Monthly Quota | Best For |
|---|---|---|---|
| **Basic** | $0 / month | 100 requests | Testing, small hobby scripts |
| **Pro** | $9.99 / month | 5,000 requests | Indie developers, side projects |
| **Ultra** | $29.99 / month | 25,000 requests | Startups, production SaaS apps |
| **Mega** | $79.99 / month | 100,000 requests | High-volume pipelines, agencies |
