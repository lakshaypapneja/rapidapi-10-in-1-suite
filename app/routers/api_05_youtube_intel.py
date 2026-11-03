import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from youtube_transcript_api import YouTubeTranscriptApi

router = APIRouter(
    prefix="/api/v1/youtube-intel",
    tags=["5. YouTube Transcript, Metadata & Viral Hook Extractor"],
)

YT_ID_PATTERNS = [
    re.compile(r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_\-]{11})"),
    re.compile(r"^([a-zA-Z0-9_\-]{11})$"),
]


class YouTubeIntelRequest(BaseModel):
    video_url_or_id: str = Field(
        default="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        description="YouTube video URL, Shorts URL, or 11-character Video ID.",
    )
    languages: list[str] = Field(
        default=["en"],
        description="Preferred transcript language codes in priority order.",
    )


class YouTubeIntelResponse(BaseModel):
    video_id: str
    full_text: str
    opening_hook_first_30s: str
    word_count: int
    estimated_speaking_wpm: float
    total_duration_seconds: float
    segments: list[dict[str, float | str]]


def _extract_video_id(raw: str) -> str | None:
    raw = raw.strip()
    for pattern in YT_ID_PATTERNS:
        m = pattern.search(raw)
        if m:
            return m.group(1)
    return None


@router.post(
    "/transcript",
    response_model=YouTubeIntelResponse,
    summary="Extract timestamped transcript, opening 30s viral hook, and pacing metrics from YouTube",
)
async def get_youtube_transcript(payload: YouTubeIntelRequest):
    video_id = _extract_video_id(payload.video_url_or_id)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube video URL or ID.")

    try:
        ytt_api = YouTubeTranscriptApi()
        if hasattr(ytt_api, "fetch"):
            fetched = ytt_api.fetch(video_id, languages=payload.languages)
            raw_segments = [
                {
                    "text": getattr(item, "text", item.get("text", "") if isinstance(item, dict) else ""),
                    "start": float(getattr(item, "start", item.get("start", 0.0) if isinstance(item, dict) else 0.0)),
                    "duration": float(
                        getattr(item, "duration", item.get("duration", 0.0) if isinstance(item, dict) else 0.0)
                    ),
                }
                for item in fetched
            ]
        else:
            raw_segments = YouTubeTranscriptApi.get_transcript(
                video_id, languages=payload.languages
            )
    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Could not retrieve transcript for video '{video_id}': {exc}",
        )

    full_text = " ".join(seg["text"].replace("\n", " ").strip() for seg in raw_segments).strip()
    hook_text = " ".join(
        seg["text"].replace("\n", " ").strip()
        for seg in raw_segments
        if float(seg["start"]) <= 30.0
    ).strip()

    total_duration = (
        float(raw_segments[-1]["start"]) + float(raw_segments[-1]["duration"])
        if raw_segments
        else 0.0
    )
    words = len(full_text.split())
    wpm = round((words / (total_duration / 60.0)), 1) if total_duration > 0 else 0.0

    return YouTubeIntelResponse(
        video_id=video_id,
        full_text=full_text,
        opening_hook_first_30s=hook_text,
        word_count=words,
        estimated_speaking_wpm=wpm,
        total_duration_seconds=round(total_duration, 2),
        segments=raw_segments[:250],
    )
