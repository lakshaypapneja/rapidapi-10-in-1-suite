from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from croniter import croniter
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/cron-schedule",
    tags=["9. Universal Cron, Natural Language Schedule & Timezone"],
)

NATURAL_CRON_PRESETS = {
    "every minute": "* * * * *",
    "every 5 minutes": "*/5 * * * *",
    "every 15 minutes": "*/15 * * * *",
    "every 30 minutes": "*/30 * * * *",
    "every hour": "0 * * * *",
    "hourly": "0 * * * *",
    "every day at midnight": "0 0 * * *",
    "daily": "0 0 * * *",
    "every day at 9am": "0 9 * * *",
    "every weekday at 9am": "0 9 * * 1-5",
    "weekdays at 9am": "0 9 * * 1-5",
    "every monday at 9am": "0 9 * * 1",
    "weekly": "0 0 * * 0",
    "monthly": "0 0 1 * *",
}


class CronScheduleRequest(BaseModel):
    expression_or_text: str = Field(
        default="0 9 * * 1-5",
        description="Standard 5-field cron expression (e.g. '*/15 * * * *') or natural phrase (e.g. 'every weekday at 9am').",
    )
    timezone_name: str = Field(
        default="UTC",
        description="IANA timezone name (e.g. 'UTC', 'America/New_York', 'Asia/Kolkata').",
    )
    next_runs_count: int = Field(
        default=5,
        ge=1,
        le=25,
        description="Number of upcoming execution timestamps to calculate.",
    )


class CronScheduleResponse(BaseModel):
    cron_expression: str
    human_summary: str
    timezone: str
    next_executions_iso: list[str]
    seconds_until_next_run: int


def _explain_cron(expr: str) -> str:
    parts = expr.split()
    if len(parts) != 5:
        return "Custom cron schedule"
    minute, hour, dom, month, dow = parts
    if expr == "* * * * *":
        return "Runs every single minute"
    if minute.startswith("*/") and hour == "*" and dom == "*" and month == "*" and dow == "*":
        return f"Runs every {minute[2:]} minutes"
    if dom == "*" and month == "*" and dow == "1-5":
        return f"Runs at {hour.zfill(2)}:{minute.zfill(2)} Monday through Friday (weekdays)"
    if dom == "*" and month == "*" and dow == "*":
        return f"Runs daily at {hour.zfill(2)}:{minute.zfill(2)}"
    return f"Runs at minute={minute}, hour={hour}, day={dom}, month={month}, weekday={dow}"


@router.post(
    "/parse",
    response_model=CronScheduleResponse,
    summary="Validate cron or natural text, explain in plain English, and compute next N execution times",
)
async def parse_cron_schedule(payload: CronScheduleRequest):
    raw = payload.expression_or_text.strip().lower()
    cron_expr = NATURAL_CRON_PRESETS.get(raw, payload.expression_or_text.strip())

    try:
        tz = ZoneInfo(payload.timezone_name)
    except Exception:
        raise HTTPException(
            status_code=400, detail=f"Unknown IANA timezone: {payload.timezone_name}"
        )

    now = datetime.now(tz)
    if not croniter.is_valid(cron_expr):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cron expression '{cron_expr}'. Provide a 5-field cron or supported phrase.",
        )

    itr = croniter(cron_expr, now)
    upcoming: list[datetime] = [itr.get_next(datetime) for _ in range(payload.next_runs_count)]
    delta_seconds = max(0, int((upcoming[0] - now).total_seconds()))

    return CronScheduleResponse(
        cron_expression=cron_expr,
        human_summary=_explain_cron(cron_expr),
        timezone=payload.timezone_name,
        next_executions_iso=[dt.isoformat() for dt in upcoming],
        seconds_until_next_run=delta_seconds,
    )
