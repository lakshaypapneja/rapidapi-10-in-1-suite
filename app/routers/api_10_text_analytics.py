from collections import Counter
import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/text-analytics",
    tags=["10. Readability, Sentiment & Content Quality Scorer"],
)

STOPWORDS = {
    "the", "and", "to", "of", "in", "a", "is", "that", "for", "it", "on", "with",
    "as", "are", "this", "by", "be", "at", "or", "from", "an", "not", "have", "has",
}

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "profitable", "fast", "easy", "best",
    "love", "success", "effective", "powerful", "clean", "reliable", "smart", "growth",
}

NEGATIVE_WORDS = {
    "bad", "slow", "broken", "error", "fail", "worst", "hard", "expensive",
    "poor", "bug", "issue", "problem", "risk", "weak", "difficult", "crash",
}


class TextAnalyticsRequest(BaseModel):
    text: str = Field(
        default=(
            "Building micro-APIs is one of the fastest and most reliable ways for developers "
            "to create recurring digital income. By solving specific technical bottlenecks cleanly, "
            "your service saves engineering teams hours of work every single week."
        ),
        description="Article, ad copy, or LLM output to score for readability, keyword density, and sentiment.",
    )


class TextAnalyticsResponse(BaseModel):
    character_count: int
    word_count: int
    sentence_count: int
    average_words_per_sentence: float
    flesch_reading_ease: float
    flesch_kincaid_grade_level: float
    reading_difficulty_label: str
    lexical_diversity_ratio: float
    sentiment_score: float
    sentiment_label: str
    top_keywords: list[dict[str, int | float | str]]


def _count_syllables(word: str) -> int:
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    word = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", word)
    word = re.sub(r"^y", "", word)
    vowels = re.findall(r"[aeiouy]{1,2}", word)
    return max(1, len(vowels))


@router.post(
    "/score",
    response_model=TextAnalyticsResponse,
    summary="Compute Flesch-Kincaid readability, lexical diversity, sentiment polarity, and top SEO keywords",
)
async def score_text_analytics(payload: TextAnalyticsRequest):
    text = payload.text.strip()
    words = re.findall(r"\b[a-zA-Z0-9']+\b", text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

    word_count = len(words)
    sentence_count = max(1, len(sentences))
    syllables = sum(_count_syllables(w) for w in words) if word_count else 0

    avg_wps = round(word_count / sentence_count, 2) if word_count else 0.0
    avg_spw = (syllables / word_count) if word_count else 0.0

    flesch_ease = (
        round(206.835 - (1.015 * avg_wps) - (84.6 * avg_spw), 2) if word_count else 0.0
    )
    fk_grade = (
        round((0.39 * avg_wps) + (11.8 * avg_spw) - 15.59, 2) if word_count else 0.0
    )

    difficulty = (
        "very_easy"
        if flesch_ease >= 80
        else "easy_conversational"
        if flesch_ease >= 60
        else "standard_business"
        if flesch_ease >= 45
        else "complex_academic"
    )

    lower_words = [w.lower() for w in words]
    unique_ratio = round(len(set(lower_words)) / word_count, 3) if word_count else 0.0

    pos_hits = sum(1 for w in lower_words if w in POSITIVE_WORDS)
    neg_hits = sum(1 for w in lower_words if w in NEGATIVE_WORDS)
    sentiment = round((pos_hits - neg_hits) / max(1, pos_hits + neg_hits), 2)
    sentiment_label = (
        "positive" if sentiment > 0.15 else "negative" if sentiment < -0.15 else "neutral"
    )

    content_words = [w for w in lower_words if len(w) > 2 and w not in STOPWORDS]
    counts = Counter(content_words).most_common(10)
    top_keywords = [
        {
            "keyword": kw,
            "count": count,
            "density_percent": round((count / max(1, word_count)) * 100, 2),
        }
        for kw, count in counts
    ]

    return TextAnalyticsResponse(
        character_count=len(text),
        word_count=word_count,
        sentence_count=len(sentences),
        average_words_per_sentence=avg_wps,
        flesch_reading_ease=flesch_ease,
        flesch_kincaid_grade_level=max(0.0, fk_grade),
        reading_difficulty_label=difficulty,
        lexical_diversity_ratio=unique_ratio,
        sentiment_score=sentiment,
        sentiment_label=sentiment_label,
        top_keywords=top_keywords,
    )
