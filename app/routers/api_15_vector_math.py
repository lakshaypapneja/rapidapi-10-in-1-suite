import math
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/vector-math",
    tags=["15. Embedding Vector Normalizer & Cosine Similarity"],
)


class CosineRequest(BaseModel):
    vector_a: list[float] = Field(
        default=[0.12, 0.45, -0.67, 0.89],
        description="First embedding vector array.",
    )
    vector_b: list[float] = Field(
        default=[0.10, 0.40, -0.70, 0.85],
        description="Second embedding vector array (must have identical dimension).",
    )


class CosineResponse(BaseModel):
    dimension: int
    dot_product: float
    cosine_similarity: float
    cosine_distance: float


class NormalizeRequest(BaseModel):
    vector: list[float] = Field(
        default=[3.0, 4.0, 0.0],
        description="Vector array to normalize to unit length (L2 norm = 1.0).",
    )


class NormalizeResponse(BaseModel):
    original_magnitude: float
    normalized_vector: list[float]


@router.post(
    "/similarity",
    response_model=CosineResponse,
    summary="Compute high-speed dot product, cosine similarity and distance between two embedding vectors",
)
async def compute_similarity(payload: CosineRequest):
    a = payload.vector_a
    b = payload.vector_b
    if len(a) != len(b):
        raise HTTPException(
            status_code=400,
            detail=f"Vector dimension mismatch: vector_a has {len(a)} items, vector_b has {len(b)} items.",
        )
    if not a:
        raise HTTPException(status_code=400, detail="Vectors cannot be empty.")

    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))

    if mag_a == 0 or mag_b == 0:
        sim = 0.0
    else:
        sim = dot / (mag_a * mag_b)

    sim = max(-1.0, min(1.0, sim))
    dist = 1.0 - sim

    return CosineResponse(
        dimension=len(a),
        dot_product=round(dot, 6),
        cosine_similarity=round(sim, 6),
        cosine_distance=round(dist, 6),
    )


@router.post(
    "/normalize",
    response_model=NormalizeResponse,
    summary="Normalize an embedding vector to unit length (L2 normalization)",
)
async def normalize_vector(payload: NormalizeRequest):
    v = payload.vector
    if not v:
        raise HTTPException(status_code=400, detail="Vector cannot be empty.")

    mag = math.sqrt(sum(x * x for x in v))
    if mag == 0:
        norm = v
    else:
        norm = [round(x / mag, 6) for x in v]

    return NormalizeResponse(original_magnitude=round(mag, 6), normalized_vector=norm)
