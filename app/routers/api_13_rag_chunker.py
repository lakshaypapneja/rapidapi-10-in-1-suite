import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/rag-chunker",
    tags=["13. Text Chunking & RAG Document Splitter"],
)


class ChunkRequest(BaseModel):
    document_text: str = Field(
        default="Antigravity agents allow automated coding. They read codebase structure, edit files, and run tests. In addition, they integrate with external MCP servers for extended capabilities. Deployment is managed via cloud providers.",
        description="Source document text to segment into RAG vector-store chunks.",
    )
    chunk_size: int = Field(default=150, ge=50, le=4000, description="Target chunk size in characters.")
    overlap: int = Field(default=30, ge=0, le=1000, description="Overlap in characters between consecutive chunks.")
    split_mode: str = Field(
        default="sentence",
        description="Splitting strategy: 'sentence', 'paragraph', or 'fixed'.",
    )


class ChunkItem(BaseModel):
    chunk_index: int
    char_count: int
    approx_tokens: int
    text: str


class ChunkResponse(BaseModel):
    total_chunks: int
    total_characters: int
    chunks: list[ChunkItem]


@router.post(
    "/split",
    response_model=ChunkResponse,
    summary="Segment text into overlapping chunks optimized for RAG embeddings and Vector DBs",
)
async def chunk_document(payload: ChunkRequest):
    text = payload.document_text.strip()
    if not text:
        return ChunkResponse(total_chunks=0, total_characters=0, chunks=[])

    chunks_list: list[str] = []

    if payload.split_mode == "paragraph":
        raw_units = [p.strip() for p in text.split("\n\n") if p.strip()]
    elif payload.split_mode == "sentence":
        raw_units = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    else:
        raw_units = []

    if raw_units:
        current_chunk: list[str] = []
        current_len = 0
        for unit in raw_units:
            if current_len + len(unit) > payload.chunk_size and current_chunk:
                combined = " ".join(current_chunk)
                chunks_list.append(combined)
                # Keep end of chunk for overlap
                overlap_text = combined[-payload.overlap :] if payload.overlap > 0 else ""
                current_chunk = [overlap_text, unit] if overlap_text else [unit]
                current_len = sum(len(x) for x in current_chunk)
            else:
                current_chunk.append(unit)
                current_len += len(unit)
        if current_chunk:
            chunks_list.append(" ".join(current_chunk).strip())
    else:
        # Fixed length sliding window
        step = max(1, payload.chunk_size - payload.overlap)
        for i in range(0, len(text), step):
            segment = text[i : i + payload.chunk_size].strip()
            if segment:
                chunks_list.append(segment)

    results: list[ChunkItem] = []
    for idx, c in enumerate(chunks_list):
        results.append(
            ChunkItem(
                chunk_index=idx,
                char_count=len(c),
                approx_tokens=max(1, int(len(c) / 4)),
                text=c,
            )
        )

    return ChunkResponse(
        total_chunks=len(results),
        total_characters=len(text),
        chunks=results,
    )
