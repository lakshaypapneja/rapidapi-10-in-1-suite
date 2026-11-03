import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/pii-redactor",
    tags=["6. Smart PII Redaction & Data Sanitizer for LLMs"],
)

PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b")),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("CREDIT_CARD", re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
    ("IPV4", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    (
        "API_KEY",
        re.compile(
            r"\b(?:sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{30,}|AIza[0-9A-Za-z\-_]{35}|AKIA[0-9A-Z]{16})\b"
        ),
    ),
    (
        "PHONE",
        re.compile(
            r"(?:\+\d{1,3}[\s\-]?)?(?:\(\d{3}\)[\s\-]?|\b\d{3}[\s\-])\d{3}[\s\-]\d{4}\b"
        ),
    ),
]


class PiiRedactRequest(BaseModel):
    text: str = Field(
        default=(
            "Customer John Doe (email: john.doe@acme.com, phone: +1 (415) 555-2671, "
            "SSN: 123-45-6789) used card 4532-0151-1283-0366 from IP 192.168.1.42 "
            "with key sk-proj1234567890abcdefghijklmnop."
        ),
        description="Raw text or LLM prompt to sanitize and strip PII/secrets from.",
    )
    placeholder_style: str = Field(
        default="numbered",
        description="Use 'numbered' (e.g. [EMAIL_1]) for reversible mapping or 'masked' (e.g. [REDACTED_EMAIL]).",
    )


class PiiRedactResponse(BaseModel):
    sanitized_text: str
    total_redactions: int
    counts_by_type: dict[str, int]
    redaction_map: dict[str, str]
    safe_for_llm: bool


@router.post(
    "/sanitize",
    response_model=PiiRedactResponse,
    summary="Redact PII (emails, phones, SSNs, credit cards, IPs, API keys) with reversible token map",
)
async def sanitize_pii(payload: PiiRedactRequest):
    sanitized = payload.text
    counts: dict[str, int] = {}
    redaction_map: dict[str, str] = {}
    total = 0

    for label, pattern in PII_PATTERNS:
        counter = 0

        def _replacer(match: re.Match[str]) -> str:
            nonlocal counter, total
            val = match.group(0)
            counter += 1
            total += 1
            counts[label] = counts.get(label, 0) + 1
            token = (
                f"[{label}_{counter}]"
                if payload.placeholder_style == "numbered"
                else f"[REDACTED_{label}]"
            )
            redaction_map[token] = val
            return token

        sanitized = pattern.sub(_replacer, sanitized)

    return PiiRedactResponse(
        sanitized_text=sanitized,
        total_redactions=total,
        counts_by_type=counts,
        redaction_map=redaction_map,
        safe_for_llm=True,
    )
