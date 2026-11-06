import base64
import hashlib
import hmac
import json
import secrets
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/security", tags=["Security, Crypto & Auth (APIs 36-50)"])

# 36. Multi-Algorithm Hash Generator
class HashRequest(BaseModel):
    input_text: str = Field(default="Antigravity RapidAPI Suite")

class HashResponse(BaseModel):
    md5: str
    sha1: str
    sha256: str
    sha512: str

@router.post("/hash-generator", response_model=HashResponse, summary="36. Multi-Algorithm Hash Generator (MD5, SHA1, SHA256, SHA512)")
async def generate_hashes(payload: HashRequest):
    data = payload.input_text.encode("utf-8")
    return HashResponse(
        md5=hashlib.md5(data).hexdigest(),
        sha1=hashlib.sha1(data).hexdigest(),
        sha256=hashlib.sha256(data).hexdigest(),
        sha512=hashlib.sha512(data).hexdigest(),
    )

# 37. HMAC Signature Generator
class HmacRequest(BaseModel):
    message: str = Field(default="order_id=12345&amount=99")
    secret_key: str = Field(default="super_secret_webhook_key")
    algorithm: str = Field(default="sha256", description="sha256, sha512, or sha1")

class HmacResponse(BaseModel):
    algorithm: str
    hex_digest: str
    base64_digest: str

@router.post("/hmac-signer", response_model=HmacResponse, summary="37. Webhook & API HMAC Signature Generator")
async def sign_hmac(payload: HmacRequest):
    algo_map = {"sha256": hashlib.sha256, "sha512": hashlib.sha512, "sha1": hashlib.sha1}
    fn = algo_map.get(payload.algorithm.lower(), hashlib.sha256)
    sig = hmac.new(payload.secret_key.encode(), payload.message.encode(), fn).digest()
    return HmacResponse(algorithm=payload.algorithm, hex_digest=sig.hex(), base64_digest=base64.b64encode(sig).decode())

# 38. JWT Claims Inspector (Without Secret)
class JwtRequest(BaseModel):
    token: str = Field(default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")

class JwtResponse(BaseModel):
    header: dict
    payload: dict
    is_expired_claim: bool | None

@router.post("/jwt-decoder", response_model=JwtResponse, summary="38. JWT Header, Claims & Expiration Inspector")
async def decode_jwt(payload: JwtRequest):
    parts = payload.token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=400, detail="Invalid JWT format: Token must contain exactly 3 segments separated by dots.")
    def b64_decode(seg: str) -> dict:
        pad = seg + "=" * ((4 - len(seg) % 4) % 4)
        return json.loads(base64.urlsafe_b64decode(pad.encode()))
    try:
        h = b64_decode(parts[0])
        p = b64_decode(parts[1])
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to decode base64 claims: {exc}")
    import time
    exp = p.get("exp")
    is_exp = (time.time() > exp) if exp else None
    return JwtResponse(header=h, payload=p, is_expired_claim=is_exp)

# 39. Cryptographically Secure Token & API Key Generator
class TokenGenRequest(BaseModel):
    length_bytes: int = Field(default=32, ge=16, le=128)
    prefix: str = Field(default="sk_live_")

class TokenGenResponse(BaseModel):
    token: str
    entropy_bits: int

@router.post("/api-key-generator", response_model=TokenGenResponse, summary="39. Cryptographic API Key and Secret Token Generator")
async def generate_api_key(payload: TokenGenRequest):
    raw_token = secrets.token_urlsafe(payload.length_bytes)
    return TokenGenResponse(token=f"{payload.prefix}{raw_token}", entropy_bits=payload.length_bytes * 8)

# 40. UUID v4 & UUID v7 Generator
class UuidGenRequest(BaseModel):
    count: int = Field(default=5, ge=1, le=50)

class UuidGenResponse(BaseModel):
    uuids: list[str]

@router.post("/uuid-generator", response_model=UuidGenResponse, summary="40. UUID v4 Cryptographically Secure Batch Generator")
async def generate_uuids(payload: UuidGenRequest):
    return UuidGenResponse(uuids=[str(uuid.uuid4()) for _ in range(payload.count)])

# 41. UUID Validator & Version Inspector
class UuidCheckRequest(BaseModel):
    uuid_str: str = Field(default="550e8400-e29b-41d4-a716-446655440000")

class UuidCheckResponse(BaseModel):
    is_valid: bool
    version: int | None
    variant: str | None

@router.post("/uuid-validator", response_model=UuidCheckResponse, summary="41. UUID Format & Version Inspector")
async def check_uuid(payload: UuidCheckRequest):
    try:
        u = uuid.UUID(payload.uuid_str)
        return UuidCheckResponse(is_valid=True, version=u.version, variant=u.variant)
    except ValueError:
        return UuidCheckResponse(is_valid=False, version=None, variant=None)

# 42. Password Generator with Configurable Policy
class PwdGenRequest(BaseModel):
    length: int = Field(default=16, ge=8, le=64)
    include_symbols: bool = True
    include_numbers: bool = True

class PwdGenResponse(BaseModel):
    password: str
    length: int

@router.post("/password-generator", response_model=PwdGenResponse, summary="42. Custom Policy Password Generator")
async def generate_password(payload: PwdGenRequest):
    import string
    chars = string.ascii_letters
    if payload.include_numbers: chars += string.digits
    if payload.include_symbols: chars += "!@#$%^&*()-_=+"
    pwd = "".join(secrets.choice(chars) for _ in range(payload.length))
    return PwdGenResponse(password=pwd, length=len(pwd))

# 43. Base64 Text Encoder & Decoder
class B64Request(BaseModel):
    text: str = Field(default="Hello RapidAPI World!")
    mode: str = Field(default="encode", description="'encode' or 'decode'")

class B64Response(BaseModel):
    result: str
    mode: str

@router.post("/base64-converter", response_model=B64Response, summary="43. Base64 UTF-8 Text Encoder and Decoder")
async def convert_base64(payload: B64Request):
    if payload.mode.lower() == "decode":
        try:
            res = base64.b64decode(payload.text.encode()).decode("utf-8")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid Base64: {exc}")
    else:
        res = base64.b64encode(payload.text.encode("utf-8")).decode()
    return B64Response(result=res, mode=payload.mode)

# 44. Hexadecimal String Encoder & Decoder
class HexRequest(BaseModel):
    text: str = Field(default="RapidAPI 100")
    mode: str = Field(default="encode", description="'encode' or 'decode'")

class HexResponse(BaseModel):
    result: str
    mode: str

@router.post("/hex-converter", response_model=HexResponse, summary="44. Hexadecimal String Encoder and Decoder")
async def convert_hex(payload: HexRequest):
    if payload.mode.lower() == "decode":
        try:
            res = bytes.fromhex(payload.text.replace(" ", "")).decode("utf-8")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid Hex: {exc}")
    else:
        res = payload.text.encode("utf-8").hex()
    return HexResponse(result=res, mode=payload.mode)

# 45. URL Encoder & Decoder (RFC 3986)
class UrlCodecRequest(BaseModel):
    text: str = Field(default="hello world & special/chars?q=1")
    mode: str = Field(default="encode", description="'encode' or 'decode'")

class UrlCodecResponse(BaseModel):
    result: str

@router.post("/url-encoder-decoder", response_model=UrlCodecResponse, summary="45. RFC 3986 Percent-Encoding URL Encoder and Decoder")
async def codec_url(payload: UrlCodecRequest):
    from urllib.parse import quote, unquote
    res = unquote(payload.text) if payload.mode.lower() == "decode" else quote(payload.text, safe="")
    return UrlCodecResponse(result=res)

# 46. ROT13 & Caesar Cipher Utility
class Rot13Request(BaseModel):
    text: str = Field(default="Uryyb Jbeyq!")

class Rot13Response(BaseModel):
    result: str

@router.post("/rot13-cipher", response_model=Rot13Response, summary="46. ROT13 Reversible Obfuscation Cipher")
async def cipher_rot13(payload: Rot13Request):
    import codecs
    return Rot13Response(result=codecs.encode(payload.text, "rot_13"))

# 47. Random Passphrase / Diceware Generator
class PassphraseRequest(BaseModel):
    word_count: int = Field(default=4, ge=3, le=8)
    separator: str = Field(default="-")

class PassphraseResponse(BaseModel):
    passphrase: str

@router.post("/passphrase-generator", response_model=PassphraseResponse, summary="47. Memorizable Diceware-Style Passphrase Generator")
async def generate_passphrase(payload: PassphraseRequest):
    WORDLIST = ["solar", "galaxy", "orbit", "quantum", "gravity", "matrix", "beacon", "crypto", "rocket", "falcon", "vector", "nebula", "plasma", "sensor", "shield"]
    words = [secrets.choice(WORDLIST) for _ in range(payload.word_count)]
    return PassphraseResponse(passphrase=payload.separator.join(words))

# 48. Security Headers Scanner
class SecHeaderRequest(BaseModel):
    url: str = Field(default="https://github.com")

class SecHeaderResponse(BaseModel):
    url: str
    grade: str
    csp: bool
    hsts: bool
    x_frame_options: bool
    x_content_type_options: bool

@router.post("/security-headers-scanner", response_model=SecHeaderResponse, summary="48. Web Application Security Headers Auditor (HSTS, CSP, etc.)")
async def scan_security_headers(payload: SecHeaderRequest):
    import httpx
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.head(payload.url)
            h = {k.lower(): v for k, v in resp.headers.items()}
            csp = "content-security-policy" in h
            hsts = "strict-transport-security" in h
            xfo = "x-frame-options" in h
            xcto = "x-content-type-options" in h
            score = sum([csp, hsts, xfo, xcto])
            grade = "A" if score == 4 else "B" if score == 3 else "C" if score == 2 else "D"
            return SecHeaderResponse(url=payload.url, grade=grade, csp=csp, hsts=hsts, x_frame_options=xfo, x_content_type_options=xcto)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

# 49. SQL Injection Pattern Detector
class SqliRequest(BaseModel):
    query_string: str = Field(default="SELECT * FROM users WHERE id = 1 OR '1'='1' --")

class SqliResponse(BaseModel):
    is_suspicious: bool
    risk_level: str
    patterns_detected: list[str]

@router.post("/sqli-detector", response_model=SqliResponse, summary="49. Heuristic SQL Injection Signature Detector")
async def detect_sqli(payload: SqliRequest):
    import re
    SQLI_PATTERNS = [
        (re.compile(r"(\bUNION\s+ALL\s+SELECT\b|\bUNION\s+SELECT\b)", re.I), "UNION_SELECT"),
        (re.compile(r"('|\")\s*(OR|AND)\s*('|\")?\s*([0-9]+|[a-z]+)\s*=\s*('|\")?\s*\4", re.I), "BOOLEAN_BYPASS"),
        (re.compile(r"(--|#|/\*)\s*$", re.M), "SQL_COMMENT_INJECTION"),
        (re.compile(r";\s*(DROP|DELETE|TRUNCATE|ALTER)\b", re.I), "DESTRUCTIVE_STACKED_QUERY"),
    ]
    detected = [name for pat, name in SQLI_PATTERNS if pat.search(payload.query_string)]
    return SqliResponse(is_suspicious=len(detected) > 0, risk_level="HIGH" if detected else "LOW", patterns_detected=detected)

# 50. XSS Script Payload Detector
class XssRequest(BaseModel):
    html_input: str = Field(default="<script>alert('xss')</script>")

class XssResponse(BaseModel):
    contains_xss: bool
    detected_tags_or_events: list[str]

@router.post("/xss-detector", response_model=XssResponse, summary="50. Cross-Site Scripting (XSS) Pattern and Payload Detector")
async def detect_xss(payload: XssRequest):
    import re
    XSS_PATTERNS = [
        re.compile(r"<\s*script\b[^>]*>[\s\S]*?<\s*/\s*script\s*>", re.I),
        re.compile(r"\bon\w+\s*=\s*[\"'][^\"']*[\"']", re.I),
        re.compile(r"javascript:\s*[^\"']+", re.I),
    ]
    found = []
    for pat in XSS_PATTERNS:
        matches = pat.findall(payload.html_input)
        if matches:
            found.extend(matches[:3])
    return XssResponse(contains_xss=len(found) > 0, detected_tags_or_events=[str(f) for f in found])
