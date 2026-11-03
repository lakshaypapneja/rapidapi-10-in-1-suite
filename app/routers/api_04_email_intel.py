import re
import dns.resolver
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/email-verify",
    tags=["4. Disposable Email, Domain & Syntax Intelligence"],
)

EMAIL_SYNTAX_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@([a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})$")

DISPOSABLE_DOMAINS = {
    "mailinator.com",
    "guerrillamail.com",
    "10minutemail.com",
    "tempmail.com",
    "temp-mail.org",
    "yopmail.com",
    "trashmail.com",
    "sharklasers.com",
    "getnada.com",
    "maildrop.cc",
    "dispostable.com",
    "fakeinbox.com",
    "throwawaymail.com",
    "mohmal.com",
    "burnermail.io",
}

FREE_PROVIDERS = {
    "gmail.com",
    "googlemail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "icloud.com",
    "aol.com",
    "proton.me",
    "protonmail.com",
    "zoho.com",
    "gmx.com",
}

ROLE_PREFIXES = {
    "admin",
    "support",
    "info",
    "sales",
    "contact",
    "billing",
    "help",
    "office",
    "team",
    "security",
    "careers",
    "hr",
    "noreply",
    "no-reply",
}

COMMON_TYPOS = {
    "gmial.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmail.co": "gmail.com",
    "gnail.com": "gmail.com",
    "hotmial.com": "hotmail.com",
    "yaho.com": "yahoo.com",
    "yahooo.com": "yahoo.com",
    "outlok.com": "outlook.com",
}


class EmailVerifyRequest(BaseModel):
    email: str = Field(
        default="founder@stripe.com",
        description="Email address to validate for syntax, MX DNS records, disposable provider, and B2B status.",
    )


class EmailVerifyResponse(BaseModel):
    email: str
    is_valid_syntax: bool
    domain: str | None
    has_mx_records: bool
    mx_hosts: list[str]
    is_disposable: bool
    is_free_provider: bool
    is_role_account: bool
    is_b2b_corporate: bool
    suggested_typo_fix: str | None
    deliverability_risk_score: int
    verdict: str


@router.post(
    "/check",
    response_model=EmailVerifyResponse,
    summary="Verify email syntax, live DNS MX records, disposable domains, and B2B status",
)
async def check_email(payload: EmailVerifyRequest):
    raw_email = payload.email.strip()
    match = EMAIL_SYNTAX_RE.match(raw_email)
    if not match:
        return EmailVerifyResponse(
            email=raw_email,
            is_valid_syntax=False,
            domain=None,
            has_mx_records=False,
            mx_hosts=[],
            is_disposable=False,
            is_free_provider=False,
            is_role_account=False,
            is_b2b_corporate=False,
            suggested_typo_fix=None,
            deliverability_risk_score=100,
            verdict="invalid_syntax",
        )

    local_part, domain = raw_email.split("@", 1)
    domain = domain.lower()
    local_clean = local_part.lower().split("+")[0]

    typo_domain = COMMON_TYPOS.get(domain)
    suggested_fix = f"{local_part}@{typo_domain}" if typo_domain else None

    is_disposable = domain in DISPOSABLE_DOMAINS
    is_free = domain in FREE_PROVIDERS
    is_role = local_clean in ROLE_PREFIXES

    mx_hosts: list[str] = []
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=4.0)
        mx_hosts = sorted(
            [str(r.exchange).rstrip(".") for r in answers],
            key=lambda x: x,
        )
    except Exception:
        mx_hosts = []

    has_mx = len(mx_hosts) > 0
    is_b2b = has_mx and not is_disposable and not is_free

    risk = 0
    if not has_mx:
        risk += 85
    if is_disposable:
        risk += 90
    if typo_domain:
        risk += 50
    if is_role:
        risk += 15
    risk = min(100, risk)

    verdict = (
        "disposable_blocked"
        if is_disposable
        else "undeliverable_no_mx"
        if not has_mx
        else "risky_typo_detected"
        if typo_domain
        else "valid_b2b"
        if is_b2b
        else "valid_personal"
    )

    return EmailVerifyResponse(
        email=raw_email,
        is_valid_syntax=True,
        domain=domain,
        has_mx_records=has_mx,
        mx_hosts=mx_hosts[:5],
        is_disposable=is_disposable,
        is_free_provider=is_free,
        is_role_account=is_role,
        is_b2b_corporate=is_b2b,
        suggested_typo_fix=suggested_fix,
        deliverability_risk_score=risk,
        verdict=verdict,
    )
