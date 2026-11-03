import math
import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/security-audit",
    tags=["8. Password Entropy & Secret Leak Auditor"],
)

SECRET_SIGNATURES = {
    "OpenAI API Key": re.compile(r"sk-[a-zA-Z0-9\-_]{20,}"),
    "GitHub Token": re.compile(r"gh[pousr]_[a-zA-Z0-9]{30,}"),
    "AWS Access Key ID": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Google Cloud / Gemini API Key": re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    "Stripe Secret Key": re.compile(r"sk_(?:live|test)_[0-9a-zA-Z]{24,}"),
    "Slack Bot/User Token": re.compile(r"xox[baprs]-[0-9a-zA-Z\-]{10,}"),
    "Private RSA/SSH Key": re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|PGP) PRIVATE KEY-----"),
    "JSON Web Token (JWT)": re.compile(
        r"eyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}"
    ),
}

COMMON_WEAK_PATTERNS = ["1234", "password", "qwerty", "admin", "letmein", "welcome"]


class SecurityAuditRequest(BaseModel):
    password_or_secret: str = Field(
        default="Tr0ub4dor&3!2026",
        description="Password string to evaluate for entropy, crack time, and pattern weaknesses.",
    )
    code_or_text_snippet: str | None = Field(
        default="export OPENAI_API_KEY=sk-proj1234567890abcdefghijklmnop",
        description="Optional code or log snippet to scan for leaked API keys, tokens, and credentials.",
    )


class SecurityAuditResponse(BaseModel):
    password_length: int
    charset_pool_size: int
    entropy_bits: float
    strength_rating: str
    estimated_offline_crack_time: str
    weakness_warnings: list[str]
    leaked_secrets_detected: list[dict[str, str]]


def _format_duration(seconds: float) -> str:
    if seconds < 1:
        return "instantly (< 1 second)"
    if seconds < 60:
        return f"{int(seconds)} seconds"
    if seconds < 3600:
        return f"{int(seconds // 60)} minutes"
    if seconds < 86400:
        return f"{int(seconds // 3600)} hours"
    if seconds < 31536000:
        return f"{int(seconds // 86400)} days"
    years = seconds / 31536000.0
    if years > 1e9:
        return f"{years:.2e} years (centuries+)"
    return f"{int(years):,} years"


@router.post(
    "/evaluate",
    response_model=SecurityAuditResponse,
    summary="Calculate password entropy, offline GPU crack time, and scan text for leaked API secrets",
)
async def evaluate_security(payload: SecurityAuditRequest):
    pwd = payload.password_or_secret
    pool = 0
    if any(c.islower() for c in pwd):
        pool += 26
    if any(c.isupper() for c in pwd):
        pool += 26
    if any(c.isdigit() for c in pwd):
        pool += 10
    if any(not c.isalnum() for c in pwd):
        pool += 32

    entropy = round(len(pwd) * math.log2(max(pool, 2)), 2) if pwd else 0.0
    # Assume 100 billion guesses/sec offline GPU rig (1e11)
    combinations = 2**entropy if entropy < 256 else float("inf")
    crack_seconds = combinations / 1e11 if combinations != float("inf") else 1e30

    warnings: list[str] = []
    if len(pwd) < 12:
        warnings.append("Password is shorter than 12 characters.")
    for pat in COMMON_WEAK_PATTERNS:
        if pat in pwd.lower():
            warnings.append(f"Contains common dictionary/keyboard sequence '{pat}'.")
            entropy = max(10.0, entropy - 20.0)

    if re.search(r"(.)\1\1", pwd):
        warnings.append("Contains 3+ repeated consecutive characters.")

    rating = (
        "very_strong"
        if entropy >= 80
        else "strong"
        if entropy >= 60
        else "moderate"
        if entropy >= 40
        else "weak"
    )

    leaks: list[dict[str, str]] = []
    snippet = payload.code_or_text_snippet or ""
    for secret_type, pattern in SECRET_SIGNATURES.items():
        for match in pattern.findall(snippet):
            masked = match[:6] + "..." + match[-4:] if len(match) > 12 else "***"
            leaks.append({"type": secret_type, "preview": masked})

    return SecurityAuditResponse(
        password_length=len(pwd),
        charset_pool_size=pool,
        entropy_bits=entropy,
        strength_rating=rating,
        estimated_offline_crack_time=_format_duration(crack_seconds),
        weakness_warnings=warnings,
        leaked_secrets_detected=leaks,
    )
