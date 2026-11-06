import ipaddress
import re
from fastapi import APIRouter
import phonenumbers
from pydantic import BaseModel, Field
from ua_parser import user_agent_parser

router = APIRouter(prefix="/api/v1/validation", tags=["Data Validation & Cleansing (APIs 51-65)"])

# 51. Phone Number Validator & E.164 Formatter
class PhoneRequest(BaseModel):
    phone_number: str = Field(default="+1 415 555 2671")
    default_region: str = Field(default="US")

class PhoneResponse(BaseModel):
    is_valid: bool
    e164_format: str | None
    international_format: str | None
    country_code: int | None
    region_code: str | None

@router.post("/phone-validator", response_model=PhoneResponse, summary="51. International Phone Number & E.164 Formatter")
async def validate_phone(payload: PhoneRequest):
    try:
        p = phonenumbers.parse(payload.phone_number, payload.default_region)
        valid = phonenumbers.is_valid_number(p)
        return PhoneResponse(
            is_valid=valid,
            e164_format=phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164) if valid else None,
            international_format=phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.INTERNATIONAL) if valid else None,
            country_code=p.country_code if valid else None,
            region_code=phonenumbers.region_code_for_number(p) if valid else None,
        )
    except Exception:
        return PhoneResponse(is_valid=False, e164_format=None, international_format=None, country_code=None, region_code=None)

# 52. Credit Card Luhn Algorithm Validator
class CardRequest(BaseModel):
    card_number: str = Field(default="4532 0151 1283 0366")

class CardResponse(BaseModel):
    is_valid_luhn: bool
    card_brand: str
    masked_number: str

@router.post("/credit-card-validator", response_model=CardResponse, summary="52. Credit Card Luhn Checksum & Brand Detector")
async def validate_card(payload: CardRequest):
    digits = re.sub(r"\D", "", payload.card_number)
    if not digits:
        return CardResponse(is_valid_luhn=False, card_brand="Unknown", masked_number="")
    # Luhn
    checksum = 0
    reverse_digits = digits[::-1]
    for i, ch in enumerate(reverse_digits):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9: d -= 9
        checksum += d
    valid = (checksum % 10 == 0)
    brand = "Visa" if digits.startswith("4") else "Mastercard" if digits[:2] in ["51","52","53","54","55"] else "Amex" if digits[:2] in ["34","37"] else "Discover" if digits.startswith("6011") else "Unknown"
    masked = f"**** **** **** {digits[-4:]}" if len(digits) >= 4 else digits
    return CardResponse(is_valid_luhn=valid, card_brand=brand, masked_number=masked)

# 53. IBAN Bank Account Validator
class IbanRequest(BaseModel):
    iban: str = Field(default="GB82 WEST 1234 5698 7654 32")

class IbanResponse(BaseModel):
    is_valid: bool
    country_code: str
    cleaned_iban: str

@router.post("/iban-validator", response_model=IbanResponse, summary="53. International Bank Account Number (IBAN) Checksum Validator")
async def validate_iban(payload: IbanRequest):
    clean = re.sub(r"\s+", "", payload.iban).upper()
    if len(clean) < 4:
        return IbanResponse(is_valid=False, country_code="", cleaned_iban=clean)
    reordered = clean[4:] + clean[:4]
    numeric = ""
    for ch in reordered:
        if ch.isdigit(): numeric += ch
        elif ch.isalpha(): numeric += str(ord(ch) - 55)
        else: return IbanResponse(is_valid=False, country_code=clean[:2], cleaned_iban=clean)
    valid = (int(numeric) % 97 == 1) if numeric.isdigit() else False
    return IbanResponse(is_valid=valid, country_code=clean[:2], cleaned_iban=clean)

# 54. IP Address & CIDR Range Inspector
class IpRequest(BaseModel):
    ip_or_cidr: str = Field(default="192.168.1.100")

class IpResponse(BaseModel):
    is_valid: bool
    ip_version: int | None
    is_private: bool | None
    is_loopback: bool | None

@router.post("/ip-validator", response_model=IpResponse, summary="54. IPv4 / IPv6 & CIDR Structure and Private Network Inspector")
async def validate_ip(payload: IpRequest):
    try:
        net = ipaddress.ip_network(payload.ip_or_cidr.strip(), strict=False)
        return IpResponse(is_valid=True, ip_version=net.version, is_private=net.is_private, is_loopback=net.is_loopback)
    except ValueError:
        return IpResponse(is_valid=False, ip_version=None, is_private=None, is_loopback=None)

# 55. User-Agent String Parser
class UaRequest(BaseModel):
    user_agent: str = Field(default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

class UaResponse(BaseModel):
    browser_family: str
    browser_version: str
    os_family: str
    os_version: str
    device_family: str
    is_bot: bool

@router.post("/user-agent-parser", response_model=UaResponse, summary="55. Comprehensive User-Agent OS, Browser & Device Deconstructor")
async def parse_user_agent(payload: UaRequest):
    parsed = user_agent_parser.Parse(payload.user_agent)
    b = parsed["user_agent"]
    os = parsed["os"]
    dev = parsed["device"]
    b_ver = f"{b.get('major','')}.{b.get('minor','')}".rstrip(".")
    os_ver = f"{os.get('major','')}.{os.get('minor','')}".rstrip(".")
    is_bot = "bot" in payload.user_agent.lower() or "crawler" in payload.user_agent.lower()
    return UaResponse(
        browser_family=b.get("family", "Unknown"),
        browser_version=b_ver or "Unknown",
        os_family=os.get("family", "Unknown"),
        os_version=os_ver or "Unknown",
        device_family=dev.get("family", "Other"),
        is_bot=is_bot,
    )

# 56. SemVer (Semantic Versioning) Validator & Comparator
class SemVerRequest(BaseModel):
    version_a: str = Field(default="1.10.4")
    version_b: str = Field(default="2.0.0-beta")

class SemVerResponse(BaseModel):
    version_a_valid: bool
    version_b_valid: bool
    comparison: str

@router.post("/semver-comparator", response_model=SemVerResponse, summary="56. Semantic Versioning (SemVer) Validator and Comparator")
async def compare_semver(payload: SemVerRequest):
    semver_re = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$")
    m_a = semver_re.match(payload.version_a.strip())
    m_b = semver_re.match(payload.version_b.strip())
    if not m_a or not m_b:
        return SemVerResponse(version_a_valid=bool(m_a), version_b_valid=bool(m_b), comparison="invalid_syntax")
    tuple_a = tuple(map(int, m_a.groups()[:3]))
    tuple_b = tuple(map(int, m_b.groups()[:3]))
    comp = "equal" if tuple_a == tuple_b else "older" if tuple_a < tuple_b else "newer"
    return SemVerResponse(version_a_valid=True, version_b_valid=True, comparison=comp)

# 57. MAC Address Formatter & Validator
class MacRequest(BaseModel):
    mac_address: str = Field(default="001A2B3C4D5E")

class MacResponse(BaseModel):
    is_valid: bool
    colon_format: str | None
    dash_format: str | None

@router.post("/mac-address-formatter", response_model=MacResponse, summary="57. Network MAC Address Validator and Canonical Formatter")
async def format_mac(payload: MacRequest):
    clean = re.sub(r"[^0-9A-Fa-f]", "", payload.mac_address).upper()
    if len(clean) != 12:
        return MacResponse(is_valid=False, colon_format=None, dash_format=None)
    colon = ":".join(clean[i:i+2] for i in range(0, 12, 2))
    dash = "-".join(clean[i:i+2] for i in range(0, 12, 2))
    return MacResponse(is_valid=True, colon_format=colon, dash_format=dash)

# 58. ISO 8601 Date & Timestamp Validator
class IsoDateRequest(BaseModel):
    timestamp_str: str = Field(default="2026-11-07T00:41:33Z")

class IsoDateResponse(BaseModel):
    is_valid_iso: bool
    unix_epoch: int | None
    utc_iso: str | None

@router.post("/iso-date-validator", response_model=IsoDateResponse, summary="58. ISO 8601 Timestamp Validator and Unix Epoch Converter")
async def validate_iso_date(payload: IsoDateRequest):
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(payload.timestamp_str.replace("Z", "+00:00"))
        return IsoDateResponse(is_valid_iso=True, unix_epoch=int(dt.timestamp()), utc_iso=dt.isoformat())
    except Exception:
        return IsoDateResponse(is_valid_iso=False, unix_epoch=None, utc_iso=None)

# 59. Color Code Converter (HEX, RGB, HSL)
class ColorRequest(BaseModel):
    hex_code: str = Field(default="#4F46E5")

class ColorResponse(BaseModel):
    hex: str
    rgb: str
    hsl: str

@router.post("/color-converter", response_model=ColorResponse, summary="59. Color Code Transformer (HEX to RGB and HSL)")
async def convert_color(payload: ColorRequest):
    h = payload.hex_code.lstrip("#")
    if len(h) != 6:
        h = "000000"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    import colorsys
    h_norm, l_norm, s_norm = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    hsl_str = f"hsl({int(h_norm*360)}, {int(s_norm*100)}%, {int(l_norm*100)}%)"
    return ColorResponse(hex=f"#{h.upper()}", rgb=f"rgb({r}, {g}, {b})", hsl=hsl_str)

# 60. Clean Plain Text Normalizer
class TextNormRequest(BaseModel):
    raw_text: str = Field(default="  Multiple   spaces\r\n\r\nand   tabs\t\there.  ")

class TextNormResponse(BaseModel):
    normalized_text: str
    char_count: int

@router.post("/text-normalizer", response_model=TextNormResponse, summary="60. Whitespace and Line Break Normalizer")
async def normalize_text(payload: TextNormRequest):
    t = payload.raw_text.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return TextNormResponse(normalized_text=t, char_count=len(t))

# 61. ISBN Book Barcode Validator
class IsbnRequest(BaseModel):
    isbn: str = Field(default="978-3-16-148410-0")

class IsbnResponse(BaseModel):
    is_valid: bool
    isbn_version: str

@router.post("/isbn-validator", response_model=IsbnResponse, summary="61. ISBN-10 & ISBN-13 Checksum Validator")
async def validate_isbn(payload: IsbnRequest):
    digits = re.sub(r"[-\s]", "", payload.isbn)
    if len(digits) == 13 and digits.isdigit():
        check = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
        return IsbnResponse(is_valid=(check % 10 == 0), isbn_version="ISBN-13")
    return IsbnResponse(is_valid=False, isbn_version="Unknown")

# 62. MIME Type from Extension Detector
class MimeRequest(BaseModel):
    file_extension_or_name: str = Field(default="report.pdf")

class MimeResponse(BaseModel):
    filename: str
    mime_type: str

@router.post("/mime-detector", response_model=MimeResponse, summary="62. File Extension to Standard IANA MIME Type Resolver")
async def detect_mime(payload: MimeRequest):
    import mimetypes
    mime, _ = mimetypes.guess_type(payload.file_extension_or_name)
    return MimeResponse(filename=payload.file_extension_or_name, mime_type=mime or "application/octet-stream")

# 63. JSON Schema Quick Validator
class JsonValidRequest(BaseModel):
    raw_json_string: str = Field(default='{"status": "ok", "code": 200}')

class JsonValidResponse(BaseModel):
    is_valid_json: bool
    object_type: str
    error_message: str | None

@router.post("/json-validator", response_model=JsonValidResponse, summary="63. JSON Syntax and Structural Integrity Checker")
async def check_json_validity(payload: JsonValidRequest):
    import json
    try:
        obj = json.loads(payload.raw_json_string)
        return JsonValidResponse(is_valid_json=True, object_type=type(obj).__name__, error_message=None)
    except Exception as exc:
        return JsonValidResponse(is_valid_json=False, object_type="invalid", error_message=str(exc))

# 64. International Postal Code Format Checker
class PostalRequest(BaseModel):
    postal_code: str = Field(default="90210")
    country_code: str = Field(default="US")

class PostalResponse(BaseModel):
    is_valid_format: bool
    country_code: str

@router.post("/postal-code-validator", response_model=PostalResponse, summary="64. International Postal Code Syntax Formatter")
async def validate_postal(payload: PostalRequest):
    POSTAL_REGEX = {
        "US": r"^\d{5}(-\d{4})?$",
        "UK": r"^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$",
        "CA": r"^[A-Z]\d[A-Z] \d[A-Z]\d$",
        "IN": r"^\d{6}$",
        "DE": r"^\d{5}$",
        "FR": r"^\d{5}$",
    }
    pat = POSTAL_REGEX.get(payload.country_code.upper(), r"^[\dA-Za-z -]{3,10}$")
    match = bool(re.match(pat, payload.postal_code.strip(), re.I))
    return PostalResponse(is_valid_format=match, country_code=payload.country_code.upper())

# 65. Latitude & Longitude Coordinate Validator
class GeoCoordRequest(BaseModel):
    latitude: float = Field(default=37.7749)
    longitude: float = Field(default=-122.4194)

class GeoCoordResponse(BaseModel):
    is_valid_coordinates: bool
    hemisphere: str

@router.post("/geo-coordinate-validator", response_model=GeoCoordResponse, summary="65. Geographic Latitude and Longitude Boundary Validator")
async def validate_coordinates(payload: GeoCoordRequest):
    valid_lat = -90.0 <= payload.latitude <= 90.0
    valid_lng = -180.0 <= payload.longitude <= 180.0
    valid = valid_lat and valid_lng
    ns = "North" if payload.latitude >= 0 else "South"
    ew = "East" if payload.longitude >= 0 else "West"
    return GeoCoordResponse(is_valid_coordinates=valid, hemisphere=f"{ns}-{ew}" if valid else "Invalid")
