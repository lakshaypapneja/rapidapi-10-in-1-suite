import re
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/prompt-hydrator",
    tags=["17. System Prompt Template Hydrator & Validator"],
)


class HydrateRequest(BaseModel):
    template: str = Field(
        default="You are an expert in {{domain}}. Your tone is {{tone}}. Answer the user query: {{query}}.",
        description="Prompt template containing {{variable}} placeholders.",
    )
    variables: dict[str, str] = Field(
        default={"domain": "Python Development", "tone": "concise and practical", "query": "How do I build an API?"},
        description="Key-value mapping of variables to inject.",
    )
    strict: bool = Field(
        default=False,
        description="If True, missing variables raise an error; if False, unfilled tags are reported in missing_variables.",
    )


class HydrateResponse(BaseModel):
    hydrated_prompt: str
    injected_count: int
    missing_variables: list[str]
    detected_variables: list[str]


@router.post(
    "/hydrate",
    response_model=HydrateResponse,
    summary="Safely inject variables into {{variable}} prompt templates with missing-field validation",
)
async def hydrate_prompt_template(payload: HydrateRequest):
    template = payload.template
    found_vars = sorted(list(set(re.findall(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", template))))

    missing: list[str] = []
    injected = 0
    result = template

    for var in found_vars:
        if var in payload.variables:
            val = str(payload.variables[var])
            result = re.sub(r"\{\{\s*" + re.escape(var) + r"\s*\}\}", val, result)
            injected += 1
        else:
            missing.append(var)

    return HydrateResponse(
        hydrated_prompt=result,
        injected_count=injected,
        missing_variables=missing,
        detected_variables=found_vars,
    )
