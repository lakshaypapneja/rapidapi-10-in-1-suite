from datetime import datetime, timezone
import math
from zoneinfo import ZoneInfo
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/math-calc", tags=["Math, Finance & Timezone Converters (APIs 81-90)"])

# 81. Timezone Timestamp Converter
class TzConvertRequest(BaseModel):
    timestamp_iso: str = Field(default="2026-11-07T00:41:33Z")
    target_timezone: str = Field(default="Asia/Kolkata")

class TzConvertResponse(BaseModel):
    original_iso: str
    target_timezone: str
    converted_iso: str
    is_dst: bool

@router.post("/timezone-converter", response_model=TzConvertResponse, summary="81. Universal IANA Timezone Timestamp Converter")
async def convert_timezone(payload: TzConvertRequest):
    try:
        dt = datetime.fromisoformat(payload.timestamp_iso.replace("Z", "+00:00"))
        tz = ZoneInfo(payload.target_timezone)
        converted = dt.astimezone(tz)
        return TzConvertResponse(
            original_iso=payload.timestamp_iso,
            target_timezone=payload.target_timezone,
            converted_iso=converted.isoformat(),
            is_dst=bool(converted.dst()),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

# 82. Unit Converter (Length, Weight, Temperature, Data)
class UnitRequest(BaseModel):
    value: float = Field(default=100.0)
    from_unit: str = Field(default="km", description="km, miles, kg, lbs, celsius, fahrenheit, mb, gb")
    to_unit: str = Field(default="miles")

class UnitResponse(BaseModel):
    input_value: float
    converted_value: float
    conversion_formula: str

@router.post("/unit-converter", response_model=UnitResponse, summary="82. Universal Distance, Weight, Temp & Data Unit Converter")
async def convert_units(payload: UnitRequest):
    u_from = payload.from_unit.lower()
    u_to = payload.to_unit.lower()
    v = payload.value
    if u_from == "km" and u_to == "miles": res = v * 0.621371; formula = "km * 0.621371"
    elif u_from == "miles" and u_to == "km": res = v * 1.60934; formula = "miles * 1.60934"
    elif u_from == "kg" and u_to == "lbs": res = v * 2.20462; formula = "kg * 2.20462"
    elif u_from == "lbs" and u_to == "kg": res = v * 0.453592; formula = "lbs * 0.453592"
    elif u_from == "celsius" and u_to == "fahrenheit": res = (v * 9/5) + 32; formula = "(C * 9/5) + 32"
    elif u_from == "fahrenheit" and u_to == "celsius": res = (v - 32) * 5/9; formula = "(F - 32) * 5/9"
    elif u_from == "gb" and u_to == "mb": res = v * 1024; formula = "gb * 1024"
    elif u_from == "mb" and u_to == "gb": res = v / 1024; formula = "mb / 1024"
    else: res = v; formula = "identity"
    return UnitResponse(input_value=v, converted_value=round(res, 4), conversion_formula=formula)

# 83. Compound Interest & Investment Return Calculator
class CompoundRequest(BaseModel):
    principal: float = Field(default=1000.0)
    annual_rate_percent: float = Field(default=8.0)
    years: int = Field(default=5)
    compound_frequency_per_year: int = Field(default=12)

class CompoundResponse(BaseModel):
    future_value: float
    total_interest_earned: float

@router.post("/compound-interest", response_model=CompoundResponse, summary="83. Compound Interest and Future Value Calculator")
async def calc_compound(payload: CompoundRequest):
    r = payload.annual_rate_percent / 100.0
    n = payload.compound_frequency_per_year
    t = payload.years
    fv = payload.principal * ((1 + (r / n)) ** (n * t))
    return CompoundResponse(future_value=round(fv, 2), total_interest_earned=round(fv - payload.principal, 2))

# 84. Loan & Mortgage Monthly Amortization Calculator
class LoanRequest(BaseModel):
    loan_amount: float = Field(default=250000.0)
    annual_interest_percent: float = Field(default=6.5)
    term_years: int = Field(default=30)

class LoanResponse(BaseModel):
    monthly_payment: float
    total_payment: float
    total_interest: float

@router.post("/loan-amortization", response_model=LoanResponse, summary="84. Mortgage & Loan Monthly Payment Amortization Calculator")
async def calc_loan(payload: LoanRequest):
    r = (payload.annual_interest_percent / 100.0) / 12.0
    n = payload.term_years * 12
    if r == 0: monthly = payload.loan_amount / n
    else: monthly = payload.loan_amount * (r * ((1 + r) ** n)) / (((1 + r) ** n) - 1)
    tot = monthly * n
    return LoanResponse(monthly_payment=round(monthly, 2), total_payment=round(tot, 2), total_interest=round(tot - payload.loan_amount, 2))

# 85. Percentage & Discount Calculator
class PercentRequest(BaseModel):
    original_price: float = Field(default=99.0)
    discount_percent: float = Field(default=25.0)

class PercentResponse(BaseModel):
    discount_amount: float
    final_price: float
    savings_ratio: float

@router.post("/percentage-calculator", response_model=PercentResponse, summary="85. Retail Price Discount and Percentage Delta Calculator")
async def calc_discount(payload: PercentRequest):
    disc = payload.original_price * (payload.discount_percent / 100.0)
    final_p = payload.original_price - disc
    return PercentResponse(discount_amount=round(disc, 2), final_price=round(final_p, 2), savings_ratio=payload.discount_percent)

# 86. Descriptive Statistics Calculator (Mean, Median, StdDev)
class StatsRequest(BaseModel):
    numbers: list[float] = Field(default=[12.5, 45.0, 67.2, 12.5, 89.0, 34.1])

class StatsResponse(BaseModel):
    count: int
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float

@router.post("/descriptive-statistics", response_model=StatsResponse, summary="86. Array Descriptive Statistics (Mean, Median, Variance, StdDev)")
async def calc_stats(payload: StatsRequest):
    nums = sorted(payload.numbers)
    if not nums: raise HTTPException(status_code=400, detail="Array cannot be empty")
    n = len(nums)
    mean = sum(nums) / n
    median = (nums[n//2] if n % 2 != 0 else (nums[n//2 - 1] + nums[n//2]) / 2.0)
    variance = sum((x - mean) ** 2 for x in nums) / max(1, n - 1) if n > 1 else 0.0
    return StatsResponse(count=n, mean=round(mean, 4), median=round(median, 4), std_dev=round(math.sqrt(variance), 4), min_value=min(nums), max_value=max(nums))

# 87. Byte & Storage Size Formatter
class ByteFormatRequest(BaseModel):
    bytes_count: int = Field(default=1073741824)

class ByteFormatResponse(BaseModel):
    human_readable: str
    in_kb: float
    in_mb: float
    in_gb: float

@router.post("/byte-storage-formatter", response_model=ByteFormatResponse, summary="87. Raw Byte Count to Human-Readable Units (KB, MB, GB, TB)")
async def format_bytes(payload: ByteFormatRequest):
    b = payload.bytes_count
    kb = b / 1024.0
    mb = kb / 1024.0
    gb = mb / 1024.0
    human = f"{gb:.2f} GB" if gb >= 1.0 else f"{mb:.2f} MB" if mb >= 1.0 else f"{kb:.2f} KB" if kb >= 1.0 else f"{b} B"
    return ByteFormatResponse(human_readable=human, in_kb=round(kb, 2), in_mb=round(mb, 2), in_gb=round(gb, 2))

# 88. Safe Math Expression Evaluator
class MathEvalRequest(BaseModel):
    expression: str = Field(default="(15 * 4) + (250 / 5) - 10")

class MathEvalResponse(BaseModel):
    expression: str
    result: float

@router.post("/math-evaluator", response_model=MathEvalResponse, summary="88. Safe Arithmetic Expression Evaluator (No Eval Vulnerability)")
async def eval_math(payload: MathEvalRequest):
    import ast
    import operator
    ALLOWED = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.USub: operator.neg}
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return node.value
        elif isinstance(node, ast.BinOp): return ALLOWED[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp): return ALLOWED[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported operation")
    try:
        tree = ast.parse(payload.expression, mode="eval")
        ans = _eval(tree.body)
        return MathEvalResponse(expression=payload.expression, result=round(float(ans), 6))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid mathematical expression")

# 89. Epoch Timestamp to Relative Time Formatter ("5 minutes ago")
class RelativeTimeRequest(BaseModel):
    timestamp_epoch: int = Field(default=1762497600)

class RelativeTimeResponse(BaseModel):
    relative_time: str
    seconds_delta: int

@router.post("/relative-time-formatter", response_model=RelativeTimeResponse, summary="89. Epoch Timestamp to Human Relative Time ('2 hours ago')")
async def format_relative_time(payload: RelativeTimeRequest):
    import time
    now = int(time.time())
    delta = now - payload.timestamp_epoch
    past = delta >= 0
    s = abs(delta)
    if s < 60: rel = "just now"
    elif s < 3600: rel = f"{s//60} minutes {'ago' if past else 'from now'}"
    elif s < 86400: rel = f"{s//3600} hours {'ago' if past else 'from now'}"
    else: rel = f"{s//86400} days {'ago' if past else 'from now'}"
    return RelativeTimeResponse(relative_time=rel, seconds_delta=delta)

# 90. Geometric Area & Perimeter Calculator
class GeometryRequest(BaseModel):
    shape: str = Field(default="rectangle", description="'rectangle', 'circle', or 'triangle'")
    dimension_a: float = Field(default=10.0, description="width or radius or base")
    dimension_b: float = Field(default=5.0, description="height or 0.0 for circle")

class GeometryResponse(BaseModel):
    shape: str
    area: float
    perimeter: float

@router.post("/geometry-calculator", response_model=GeometryResponse, summary="90. Geometric Area and Perimeter Solver for Circles, Rectangles, Triangles")
async def calc_geometry(payload: GeometryRequest):
    s = payload.shape.lower()
    a, b = payload.dimension_a, payload.dimension_b
    if s == "circle":
        area = math.pi * (a ** 2)
        perim = 2 * math.pi * a
    elif s == "triangle":
        area = 0.5 * a * b
        perim = a + b + math.sqrt(a**2 + b**2)
    else: # rectangle
        area = a * b
        perim = 2 * (a + b)
    return GeometryResponse(shape=s, area=round(area, 4), perimeter=round(perim, 4))
