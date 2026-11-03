import ast
import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/json-repair",
    tags=["7. LLM Output Repair & Messy JSON Parser"],
)


class JsonRepairRequest(BaseModel):
    raw_llm_output: str = Field(
        default=(
            "Sure! Here is the JSON you requested:\n```json\n"
            "{\n  'name': 'Acme AI',\n  'active': True,\n  'NullField': None,\n"
            "  'tags': ['saas', 'b2b',],\n}\n```\nHope this helps!"
        ),
        description="Malformed LLM response containing markdown fences, single quotes, trailing commas, or unclosed brackets.",
    )


class JsonRepairResponse(BaseModel):
    success: bool
    repaired_json_string: str
    parsed_data: dict | list | str | int | float | bool | None
    repairs_applied: list[str]


@router.post(
    "/repair",
    response_model=JsonRepairResponse,
    summary="Extract and deterministically repair broken or markdown-wrapped JSON from LLM outputs",
)
async def repair_llm_json(payload: JsonRepairRequest):
    raw = payload.raw_llm_output.strip()
    repairs: list[str] = []

    fence_match = re.search(r"```(?:json|javascript|js|python)?\s*([\s\S]*?)```", raw, re.I)
    if fence_match:
        raw = fence_match.group(1).strip()
        repairs.append("stripped_markdown_code_fences")
    else:
        first_brace = min(
            [i for i in (raw.find("{"), raw.find("[")) if i != -1],
            default=-1,
        )
        last_brace = max(raw.rfind("}"), raw.rfind("]"))
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            if first_brace > 0 or last_brace < len(raw) - 1:
                raw = raw[first_brace : last_brace + 1]
                repairs.append("trimmed_conversational_chatter")

    try:
        parsed = json.loads(raw)
        return JsonRepairResponse(
            success=True,
            repaired_json_string=json.dumps(parsed, indent=2),
            parsed_data=parsed,
            repairs_applied=repairs or ["already_valid_json"],
        )
    except Exception:
        pass

    candidate = re.sub(r"//.*?$", "", raw, flags=re.MULTILINE)
    if candidate != raw:
        repairs.append("removed_line_comments")

    candidate_no_trailing = re.sub(r",\s*([}\]])", r"\1", candidate)
    if candidate_no_trailing != candidate:
        repairs.append("removed_trailing_commas")
        candidate = candidate_no_trailing

    candidate_py = re.sub(r"\bTrue\b", "true", candidate)
    candidate_py = re.sub(r"\bFalse\b", "false", candidate_py)
    candidate_py = re.sub(r"\bNone\b", "null", candidate_py)
    if candidate_py != candidate:
        repairs.append("normalized_python_literals")
        candidate = candidate_py

    open_curly = candidate.count("{") - candidate.count("}")
    open_square = candidate.count("[") - candidate.count("]")
    if open_square > 0:
        candidate += "]" * open_square
        repairs.append(f"closed_{open_square}_missing_brackets")
    if open_curly > 0:
        candidate += "}" * open_curly
        repairs.append(f"closed_{open_curly}_missing_braces")

    try:
        parsed = json.loads(candidate)
        return JsonRepairResponse(
            success=True,
            repaired_json_string=json.dumps(parsed, indent=2),
            parsed_data=parsed,
            repairs_applied=repairs,
        )
    except Exception:
        pass

    try:
        py_candidate = re.sub(r"\btrue\b", "True", candidate)
        py_candidate = re.sub(r"\bfalse\b", "False", py_candidate)
        py_candidate = re.sub(r"\bnull\b", "None", py_candidate)
        parsed = ast.literal_eval(py_candidate)
        repairs.append("converted_single_quoted_dict_to_json")
        return JsonRepairResponse(
            success=True,
            repaired_json_string=json.dumps(parsed, indent=2),
            parsed_data=parsed,
            repairs_applied=repairs,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Unable to deterministically repair payload into valid JSON: {exc}",
        )
