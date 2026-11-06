import csv
import io
import json
import xml.etree.ElementTree as ET
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import yaml

router = APIRouter(prefix="/api/v1/transformers", tags=["Data Transformers & Formats (APIs 66-80)"])

# 66. JSON to CSV Converter
class JsonCsvRequest(BaseModel):
    json_array: list[dict] = Field(default=[{"name": "Alice", "role": "Engineer", "level": 3}, {"name": "Bob", "role": "Designer", "level": 2}])

class JsonCsvResponse(BaseModel):
    csv_string: str
    rows_converted: int

@router.post("/json-to-csv", response_model=JsonCsvResponse, summary="66. JSON Array to Tabular CSV Converter")
async def json_to_csv(payload: JsonCsvRequest):
    if not payload.json_array:
        return JsonCsvResponse(csv_string="", rows_converted=0)
    output = io.StringIO()
    headers = list(payload.json_array[0].keys())
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(payload.json_array)
    return JsonCsvResponse(csv_string=output.getvalue(), rows_converted=len(payload.json_array))

# 67. CSV to JSON Converter
class CsvJsonRequest(BaseModel):
    csv_string: str = Field(default="name,role,level\nAlice,Engineer,3\nBob,Designer,2")

class CsvJsonResponse(BaseModel):
    json_data: list[dict]
    total_records: int

@router.post("/csv-to-json", response_model=CsvJsonResponse, summary="67. Tabular CSV to Structured JSON Array Parser")
async def csv_to_json(payload: CsvJsonRequest):
    try:
        reader = csv.DictReader(io.StringIO(payload.csv_string.strip()))
        data = [row for row in reader]
        return CsvJsonResponse(json_data=data, total_records=len(data))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

# 68. YAML to JSON Converter
class YamlJsonRequest(BaseModel):
    yaml_string: str = Field(default="server:\n  port: 8080\n  host: 0.0.0.0\nfeatures:\n  - auth\n  - rate_limit")

class YamlJsonResponse(BaseModel):
    json_string: str
    parsed_object: dict

@router.post("/yaml-to-json", response_model=YamlJsonResponse, summary="68. YAML Configuration to Formatted JSON Converter")
async def yaml_to_json(payload: YamlJsonRequest):
    try:
        parsed = yaml.safe_load(payload.yaml_string)
        return YamlJsonResponse(json_string=json.dumps(parsed, indent=2), parsed_object=parsed)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {exc}")

# 69. JSON to YAML Converter
class JsonYamlRequest(BaseModel):
    json_string: str = Field(default='{"server": {"port": 8080, "host": "0.0.0.0"}, "features": ["auth", "rate_limit"]}')

class JsonYamlResponse(BaseModel):
    yaml_string: str

@router.post("/json-to-yaml", response_model=JsonYamlResponse, summary="69. JSON Object to Clean YAML Converter")
async def json_to_yaml(payload: JsonYamlRequest):
    try:
        data = json.loads(payload.json_string)
        return JsonYamlResponse(yaml_string=yaml.dump(data, sort_keys=False))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}")

# 70. XML to JSON Converter
class XmlJsonRequest(BaseModel):
    xml_string: str = Field(default="<user><id>101</id><name>Lakshay</name><active>true</active></user>")

class XmlJsonResponse(BaseModel):
    json_object: dict

@router.post("/xml-to-json", response_model=XmlJsonResponse, summary="70. Simple XML to Structured JSON Converter")
async def xml_to_json(payload: XmlJsonRequest):
    def elem_to_dict(elem):
        d = {}
        for child in elem:
            d[child.tag] = elem_to_dict(child) if len(child) else child.text
        return d or elem.text
    try:
        root = ET.fromstring(payload.xml_string.strip())
        return XmlJsonResponse(json_object={root.tag: elem_to_dict(root)})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid XML: {exc}")

# 71. HTML Table to JSON Array Extractor
class HtmlTableRequest(BaseModel):
    html_snippet: str = Field(default="<table><thead><tr><th>Plan</th><th>Price</th></tr></thead><tbody><tr><td>Basic</td><td>$0</td></tr><tr><td>Pro</td><td>$9.99</td></tr></tbody></table>")

class HtmlTableResponse(BaseModel):
    headers: list[str]
    rows: list[dict[str, str]]

@router.post("/html-table-to-json", response_model=HtmlTableResponse, summary="71. HTML Table Scraper to Structured JSON Records")
async def table_to_json(payload: HtmlTableRequest):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(payload.html_snippet, "lxml")
    table = soup.find("table")
    if not table:
        return HtmlTableResponse(headers=[], rows=[])
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    rows_data = []
    for tr in table.find_all("tr"):
        tds = [td.get_text(strip=True) for td in tr.find_all("td")]
        if tds and len(tds) == len(headers):
            rows_data.append(dict(zip(headers, tds)))
    return HtmlTableResponse(headers=headers, rows=rows_data)

# 72. Text Case Converter (camelCase, snake_case, PascalCase, kebab-case)
class CaseRequest(BaseModel):
    text: str = Field(default="Rapid API 100 Suite")

class CaseResponse(BaseModel):
    camel_case: str
    snake_case: str
    pascal_case: str
    kebab_case: str
    constant_case: str

@router.post("/text-case-converter", response_model=CaseResponse, summary="72. Universal Programming Casing Converter (camel, snake, kebab, etc.)")
async def convert_case(payload: CaseRequest):
    import re
    words = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+", payload.text)
    lower_words = [w.lower() for w in words]
    camel = lower_words[0] + "".join(w.capitalize() for w in lower_words[1:]) if lower_words else ""
    pascal = "".join(w.capitalize() for w in lower_words)
    snake = "_".join(lower_words)
    kebab = "-".join(lower_words)
    constant = "_".join(w.upper() for w in lower_words)
    return CaseResponse(camel_case=camel, snake_case=snake, pascal_case=pascal, kebab_case=kebab, constant_case=constant)

# 73. JSON Minifier & Beautifier
class JsonFormatRequest(BaseModel):
    json_string: str = Field(default='{\n  "title": "API",\n  "count": 100\n}')
    indent: int = Field(default=2, ge=0, le=8)

class JsonFormatResponse(BaseModel):
    formatted_json: str
    minified_json: str
    byte_savings: int

@router.post("/json-formatter", response_model=JsonFormatResponse, summary="73. JSON Minifier and Formatted Beautifier")
async def format_json(payload: JsonFormatRequest):
    try:
        obj = json.loads(payload.json_string)
        minified = json.dumps(obj, separators=(",", ":"))
        formatted = json.dumps(obj, indent=payload.indent)
        savings = len(payload.json_string.encode()) - len(minified.encode())
        return JsonFormatResponse(formatted_json=formatted, minified_json=minified, byte_savings=max(0, savings))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

# 74. SQL Query Formatter & Indenter
class SqlFormatRequest(BaseModel):
    sql_query: str = Field(default="select id,name,email from users where active=1 and role='admin' order by id desc;")

class SqlFormatResponse(BaseModel):
    formatted_sql: str

@router.post("/sql-formatter", response_model=SqlFormatResponse, summary="74. SQL Query Keywords Uppercaser and Indenter")
async def format_sql(payload: SqlFormatRequest):
    import re
    KEYWORDS = ["SELECT", "FROM", "WHERE", "AND", "OR", "ORDER BY", "GROUP BY", "LIMIT", "JOIN", "LEFT JOIN", "INNER JOIN", "INSERT INTO", "UPDATE", "DELETE"]
    res = payload.sql_query
    for kw in sorted(KEYWORDS, key=len, reverse=True):
        res = re.sub(rf"\b{kw}\b", kw, res, flags=re.I)
    return SqlFormatResponse(formatted_sql=res)

# 75. Markdown to HTML Converter
class MdHtmlRequest(BaseModel):
    markdown: str = Field(default="# Title\n\n- Bullet **one**\n- Bullet two\n\nVisit [Link](https://example.com)")

class MdHtmlResponse(BaseModel):
    html: str

@router.post("/markdown-to-html", response_model=MdHtmlResponse, summary="75. Markdown to Sanitized Semantic HTML Converter")
async def markdown_to_html(payload: MdHtmlRequest):
    import re
    text = payload.markdown
    text = re.sub(r"^### (.*)$", r"<h3>\1</h3>", text, flags=re.M)
    text = re.sub(r"^## (.*)$", r"<h2>\1</h2>", text, flags=re.M)
    text = re.sub(r"^# (.*)$", r"<h1>\1</h1>", text, flags=re.M)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"^- (.*)$", r"<li>\1</li>", text, flags=re.M)
    return MdHtmlResponse(html=text)

# 76. Binary to Text & Text to Binary Converter
class BinaryRequest(BaseModel):
    input_data: str = Field(default="RapidAPI")
    mode: str = Field(default="text_to_binary", description="'text_to_binary' or 'binary_to_text'")

class BinaryResponse(BaseModel):
    output: str

@router.post("/binary-converter", response_model=BinaryResponse, summary="76. Raw 8-bit Binary Byte Array to Text Converter")
async def convert_binary(payload: BinaryRequest):
    if payload.mode == "binary_to_text":
        bytes_list = payload.input_data.strip().split()
        text = "".join(chr(int(b, 2)) for b in bytes_list if len(b) == 8 and set(b) <= {"0", "1"})
        return BinaryResponse(output=text)
    else:
        bits = " ".join(format(ord(c), "08b") for c in payload.input_data)
        return BinaryResponse(output=bits)

# 77. JSON Deep Flattener
class JsonFlattenRequest(BaseModel):
    nested_json: dict = Field(default={"app": {"server": {"port": 8000, "debug": True}}, "name": "suite"})

class JsonFlattenResponse(BaseModel):
    flattened_json: dict[str, str | int | float | bool]

@router.post("/json-flattener", response_model=JsonFlattenResponse, summary="77. Deeply Nested JSON Object to Dot-Notation Flattener")
async def flatten_json(payload: JsonFlattenRequest):
    out = {}
    def _flatten(val, prefix=""):
        if isinstance(val, dict):
            for k, v in val.items():
                _flatten(v, f"{prefix}{k}." if prefix else f"{k}.")
        else:
            out[prefix.rstrip(".")] = val
    _flatten(payload.nested_json)
    return JsonFlattenResponse(flattened_json=out)

# 78. Text Word & Frequency Sorter
class WordFreqRequest(BaseModel):
    text: str = Field(default="RapidAPI suite allows building APIs fast. Building APIs with Antigravity is faster.")
    top_n: int = Field(default=5, ge=1, le=25)

class WordFreqItem(BaseModel):
    word: str
    count: int

class WordFreqResponse(BaseModel):
    total_words: int
    frequencies: list[WordFreqItem]

@router.post("/word-frequency-counter", response_model=WordFreqResponse, summary="78. Lexical Word Count and Term Frequency Ranking")
async def count_word_freq(payload: WordFreqRequest):
    import re
    from collections import Counter
    words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", payload.text)]
    counts = Counter(words).most_common(payload.top_n)
    return WordFreqResponse(total_words=len(words), frequencies=[WordFreqItem(word=k, count=v) for k, v in counts])

# 79. Slugify Title & Unicode Cleaner
class SlugifyRequest(BaseModel):
    title: str = Field(default="The 100 Best Developer Tools of 2026!")

class SlugifyResponse(BaseModel):
    slug: str

@router.post("/slug-generator", response_model=SlugifyResponse, summary="79. SEO URL-Safe Slug Generator with Unicode Diacritics Removal")
async def generate_slug(payload: SlugifyRequest):
    from slugify import slugify
    return SlugifyResponse(slug=slugify(payload.title))

# 80. Simple Diff & Text Comparison Engine
class DiffRequest(BaseModel):
    original_text: str = Field(default="API v1.0.0 is live.")
    modified_text: str = Field(default="API v1.1.0 is live with 100 endpoints.")

class DiffResponse(BaseModel):
    is_identical: bool
    changes_detected: list[str]

@router.post("/text-diff", response_model=DiffResponse, summary="80. Unified Text & Code Difference Comparator")
async def compare_text_diff(payload: DiffRequest):
    import difflib
    lines1 = payload.original_text.splitlines()
    lines2 = payload.modified_text.splitlines()
    diff = list(difflib.unified_diff(lines1, lines2, lineterm=""))
    return DiffResponse(is_identical=(payload.original_text == payload.modified_text), changes_detected=diff)
