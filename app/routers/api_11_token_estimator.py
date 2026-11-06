import math
import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/token-cost-estimator",
    tags=["11. Token Counter & Multi-Model Cost Estimator"],
)

# Standard pricing estimates per 1M tokens (USD)
MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku": {"input": 0.80, "output": 4.00},
    "gemini-1-5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1-5-flash": {"input": 0.075, "output": 0.30},
}


class TokenEstimateRequest(BaseModel):
    text: str = Field(
        default="Analyze the quarterly performance and build a detailed summary report for stakeholders.",
        description="Text or prompt to estimate tokens and generation costs for.",
    )
    expected_output_tokens: int = Field(
        default=500,
        ge=0,
        description="Expected generation length in tokens to project total round-trip cost.",
    )


class TokenEstimateResponse(BaseModel):
    estimated_input_tokens: int
    character_count: int
    word_count: int
    pricing_comparison: dict[str, dict[str, float]]


@router.post(
    "/calculate",
    response_model=TokenEstimateResponse,
    summary="Estimate input/output token counts and round-trip costs across top LLM models",
)
async def calculate_tokens_and_cost(payload: TokenEstimateRequest):
    text = payload.text.strip()
    chars = len(text)
    words = len(re.findall(r"\b\w+\b", text))
    
    # Standard heuristic approximation for multi-language Latin/Unicode (~4 chars/token or 0.75 words/token)
    est_tokens = max(1, int(math.ceil(chars / 3.8))) if chars else 0

    pricing_comp: dict[str, dict[str, float]] = {}
    for model_name, rates in MODEL_PRICING.items():
        in_cost = (est_tokens / 1_000_000.0) * rates["input"]
        out_cost = (payload.expected_output_tokens / 1_000_000.0) * rates["output"]
        total_cost = in_cost + out_cost
        pricing_comp[model_name] = {
            "input_cost_usd": round(in_cost, 6),
            "projected_output_cost_usd": round(out_cost, 6),
            "total_estimated_usd": round(total_cost, 6),
        }

    return TokenEstimateResponse(
        estimated_input_tokens=est_tokens,
        character_count=chars,
        word_count=words,
        pricing_comparison=pricing_comp,
    )
