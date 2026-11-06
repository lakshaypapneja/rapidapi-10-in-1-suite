import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/regex-tester",
    tags=["19. Regex Tester & Pattern Match Explainer"],
)


class RegexTestRequest(BaseModel):
    pattern: str = Field(
        default=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        description="Regular expression pattern to test.",
    )
    test_string: str = Field(
        default="Contact us at support@example.com or sales.team@acme.co.uk for inquiries.",
        description="Target string to search.",
    )
    flags: str = Field(
        default="i",
        description="Regex flags: 'i' (ignore case), 'm' (multiline), 's' (dotall).",
    )


class RegexMatchItem(BaseModel):
    match: str
    start: int
    end: int
    groups: list[str]


class RegexTestResponse(BaseModel):
    is_valid_pattern: bool
    total_matches: int
    matches: list[RegexMatchItem]
    explanation: list[str]


def _explain_regex(pattern: str) -> list[str]:
    notes: list[str] = []
    if "^" in pattern:
        notes.append("Matches from the start of the string or line (^).")
    if "$" in pattern:
        notes.append("Matches until the end of the string or line ($).")
    if r"\b" in pattern:
        notes.append("Enforces word boundary positions (\\b).")
    if r"\d" in pattern:
        notes.append("Matches digit characters [0-9].")
    if r"\s" in pattern:
        notes.append("Matches whitespace characters (spaces, tabs, line breaks).")
    if "+" in pattern:
        notes.append("Contains one-or-more repetition (+).")
    if "*" in pattern:
        notes.append("Contains zero-or-more repetition (*).")
    if "?" in pattern:
        notes.append("Contains optional qualifiers or non-greedy matching (?).")
    if not notes:
        notes.append("Standard literal and token matching sequence.")
    return notes


@router.post(
    "/test",
    response_model=RegexTestResponse,
    summary="Validate, test, and extract matches with indices and plain-English regex token explanations",
)
async def test_regex_pattern(payload: RegexTestRequest):
    re_flags = 0
    if "i" in payload.flags.lower():
        re_flags |= re.IGNORECASE
    if "m" in payload.flags.lower():
        re_flags |= re.MULTILINE
    if "s" in payload.flags.lower():
        re_flags |= re.DOTALL

    try:
        compiled = re.compile(payload.pattern, re_flags)
    except re.error as exc:
        return RegexTestResponse(
            is_valid_pattern=False,
            total_matches=0,
            matches=[],
            explanation=[f"Regex syntax error: {exc}"],
        )

    matches: list[RegexMatchItem] = []
    for m in compiled.finditer(payload.test_string):
        matches.append(
            RegexMatchItem(
                match=m.group(0),
                start=m.start(),
                end=m.end(),
                groups=[str(g) for g in m.groups()],
            )
        )
        if len(matches) >= 50:
            break

    return RegexTestResponse(
        is_valid_pattern=True,
        total_matches=len(matches),
        matches=matches,
        explanation=_explain_regex(payload.pattern),
    )
