import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/ai-citations",
    tags=["16. AI Citation & Source Grounding Extractor"],
)


class CitationFormatRequest(BaseModel):
    unstructured_text: str = Field(
        default="According to the latest documentation [1], FastMCP allows building tools rapidly. Also refer to (Source: https://example.com/docs) for deployment tips.",
        description="Unstructured LLM generation containing citations, references, or footnotes.",
    )


class CitationItem(BaseModel):
    index: int
    raw_reference: str
    target_source: str
    reference_type: str


class CitationFormatResponse(BaseModel):
    clean_text: str
    total_citations: int
    citations: list[CitationItem]


@router.post(
    "/extract",
    response_model=CitationFormatResponse,
    summary="Extract footnote citations, URLs, and source brackets from unstructured LLM answers",
)
async def extract_citations(payload: CitationFormatRequest):
    text = payload.unstructured_text
    citations: list[CitationItem] = []
    idx = 1

    # Extract bracket footnotes [1], [Source: ...], etc.
    bracket_matches = re.finditer(r"\[([^\]]+)\]", text)
    for m in bracket_matches:
        content = m.group(1).strip()
        ref_type = "url" if "http" in content else "footnote" if content.isdigit() else "label"
        citations.append(
            CitationItem(
                index=idx,
                raw_reference=m.group(0),
                target_source=content,
                reference_type=ref_type,
            )
        )
        idx += 1

    # Extract bare URLs
    url_matches = re.finditer(r"(?<!\()https?://[^\s\)]+", text)
    for m in url_matches:
        url_str = m.group(0)
        if not any(url_str in c.target_source for c in citations):
            citations.append(
                CitationItem(
                    index=idx,
                    raw_reference=url_str,
                    target_source=url_str,
                    reference_type="url",
                )
            )
            idx += 1

    # Clean text with normalized [1], [2] tags
    clean = re.sub(r"\(Source:\s*[^)]+\)", "", text).strip()

    return CitationFormatResponse(
        clean_text=clean,
        total_citations=len(citations),
        citations=citations,
    )
