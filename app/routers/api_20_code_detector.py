import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/code-detector",
    tags=["20. Code Snippet Language & Runtime Detector"],
)

LANGUAGE_SIGNATURES: list[tuple[str, list[re.Pattern[str]], str]] = [
    ("Python", [re.compile(r"\bdef\s+\w+\s*\("), re.compile(r"\bimport\s+\w+"), re.compile(r"\bfrom\s+\w+\s+import"), re.compile(r":\s*$")], "python"),
    ("JavaScript", [re.compile(r"\bconst\s+\w+\s*="), re.compile(r"\blet\s+\w+\s*="), re.compile(r"=>"), re.compile(r"console\.log\(")], "node"),
    ("TypeScript", [re.compile(r"\binterface\s+\w+"), re.compile(r":\s*(string|number|boolean|any)"), re.compile(r"\btype\s+\w+\s*=")], "node/deno/bun"),
    ("HTML", [re.compile(r"<!DOCTYPE html>", re.I), re.compile(r"<\s*html\b", re.I), re.compile(r"<\s*div\b", re.I), re.compile(r"<\s*/\w+>")], "browser"),
    ("SQL", [re.compile(r"\bSELECT\b", re.I), re.compile(r"\bFROM\b", re.I), re.compile(r"\bWHERE\b", re.I), re.compile(r"\bINSERT\s+INTO\b", re.I)], "database"),
    ("JSON", [re.compile(r'^\s*[\{\[]'), re.compile(r'":\s*'), re.compile(r'[\}\]]\s*$')], "data"),
    ("Go", [re.compile(r"\bpackage\s+\w+"), re.compile(r"\bfunc\s+\w+\("), re.compile(r":=")], "go"),
    ("Rust", [re.compile(r"\bfn\s+\w+\("), re.compile(r"\blet\s+mut\b"), re.compile(r"::\w+")], "rust"),
    ("Bash / Shell", [re.compile(r"^#!/bin/(bash|sh)"), re.compile(r"\becho\s+"), re.compile(r"\bcurl\s+-")], "shell"),
]


class CodeDetectRequest(BaseModel):
    code_snippet: str = Field(
        default="import asyncio\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef hello():\n    return {'status': 'ok'}",
        description="Raw code snippet to detect programming language and runtime environment for.",
    )


class CodeDetectResponse(BaseModel):
    detected_language: str
    runtime_environment: str
    confidence_score: float
    line_count: int
    has_comments: bool


@router.post(
    "/detect",
    response_model=CodeDetectResponse,
    summary="Identify programming language, runtime, and structure of code snippets for AI agent pipelines",
)
async def detect_code_language(payload: CodeDetectRequest):
    code = payload.code_snippet
    lines = code.split("\n")
    best_lang = "Plain Text"
    best_runtime = "unknown"
    best_matches = 0

    for lang, patterns, runtime in LANGUAGE_SIGNATURES:
        matches = sum(1 for p in patterns if p.search(code))
        if matches > best_matches:
            best_matches = matches
            best_lang = lang
            best_runtime = runtime

    confidence = round(min(1.0, best_matches / 3.0), 2) if best_matches > 0 else 0.20
    has_comments = bool(re.search(r"(//|#|/\*|<!--)", code))

    return CodeDetectResponse(
        detected_language=best_lang,
        runtime_environment=best_runtime,
        confidence_score=confidence,
        line_count=len(lines),
        has_comments=has_comments,
    )
