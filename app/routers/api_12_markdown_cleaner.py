import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/markdown-cleaner",
    tags=["12. Markdown to Clean Plain Text & TTS Formatter"],
)


class CleanMarkdownRequest(BaseModel):
    markdown_text: str = Field(
        default="# Quarterly Report\n\nHere is the link: [Dashboard](https://example.com/stats). **Note:** `API_KEY` is required!\n\n- Point 1\n- Point 2\n\n```python\nprint('hello')\n```",
        description="Raw markdown string to strip into pure conversational speech/plain text.",
    )
    strip_code_blocks: bool = Field(
        default=True,
        description="Whether to completely remove code snippets/blocks for speech synthesis (TTS).",
    )


class CleanMarkdownResponse(BaseModel):
    clean_text: str
    original_char_count: int
    cleaned_char_count: int
    estimated_speaking_duration_seconds: float


@router.post(
    "/clean",
    response_model=CleanMarkdownResponse,
    summary="Strip Markdown tags, links, and code fences into clean plain text for TTS and speech pipelines",
)
async def clean_markdown_for_tts(payload: CleanMarkdownRequest):
    text = payload.markdown_text

    if payload.strip_code_blocks:
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`[^`]+`", "", text)

    # Remove headers (#)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove link formatting: [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove image formatting: ![alt](url) -> ""
    text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
    # Remove bold/italics
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    # Remove blockquotes
    text = re.sub(r"^\s*>\s+", "", text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Remove bullet markers (- * +)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    # Normalize multiple newlines and spaces
    clean = re.sub(r"\n{2,}", "\n\n", text)
    clean = re.sub(r"[ \t]+", " ", clean).strip()

    words = len(clean.split())
    # Standard speaking rate ~140 words per minute
    speaking_sec = round((words / 140.0) * 60, 1) if words else 0.0

    return CleanMarkdownResponse(
        clean_text=clean,
        original_char_count=len(payload.markdown_text),
        cleaned_char_count=len(clean),
        estimated_speaking_duration_seconds=speaking_sec,
    )
