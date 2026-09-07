"""
FastAPI application for Tally Connect.
Exposes REST endpoints that query the local or remote Tally instance.
"""
import os
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from client import TallyClient
    import tdl_templates
except ImportError:
    from tally_connect.client import TallyClient
    from tally_connect import tdl_templates

# Load Config
CONFIG_PATH = os.environ.get("TALLY_CONNECT_CONFIG", os.path.join(os.path.dirname(__file__), "config.json"))
config = {
    "service_name": "Tally Connect Agent",
    "service_host": "0.0.0.0",
    "service_port": 8001,
    "tally_url": "http://localhost:9000",
    "timeout": 20
}

if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config.update(json.load(f))
    except Exception as e:
        print(f"[!] Warning: Could not read config file ({e}), using defaults.")

tally_client = TallyClient(host_url=config["tally_url"], timeout=config.get("timeout", 20))

app = FastAPI(
    title="Tally Connect Service",
    description="Local Windows Agent exposing Tally Prime / ERP 9 database and operations via REST API.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class RawXmlRequest(BaseModel):
    xml: str

class PostVoucherRequest(BaseModel):
    voucher_xml: str

class SetTallyUrlRequest(BaseModel):
    tally_url: str

@app.get("/", response_class=HTMLResponse)
def index():
    """Serves the Apple-inspired Tally Connect Dashboard with Configuration Dialogs."""
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Tally Connect Agent</h1><p>Dashboard template not found. Visit <a href='/docs'>/docs</a> for API.</p>"

@app.get("/api/info")
def api_info():
    return {
        "service": config["service_name"],
        "status": "running",
        "tally_url": tally_client.host_url,
        "docs": "/docs"
    }

@app.get("/health")
def health():
    """Checks Tally connectivity status and active company info."""
    return tally_client.check_health()

@app.post("/api/settings/tally-url")
def update_tally_url(payload: SetTallyUrlRequest):
    """Dynamically switch the target Tally IP/Port/URL and persist to config.json."""
    tally_client.set_host_url(payload.tally_url)
    config["tally_url"] = payload.tally_url
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"[!] Warning: Could not persist config to disk: {e}")
    return {"message": f"Tally URL updated to {payload.tally_url}", "health": tally_client.check_health()}

@app.get("/api/companies")
def get_companies():
    """Extracts list of companies loaded in Tally."""
    success, raw, parsed = tally_client.execute_xml(tdl_templates.get_companies_xml())
    if not success:
        raise HTTPException(status_code=502, detail=parsed)
    return {"status": "success", "data": parsed}

@app.get("/api/masters/ledgers")
def get_ledgers(company: Optional[str] = Query(None, description="Optional target company name")):
    """Extracts all ledgers with balance, parent group, and GSTIN."""
    xml_req = tdl_templates.get_ledgers_xml(company_name=company)
    success, raw, parsed = tally_client.execute_xml(xml_req)
    if not success:
        raise HTTPException(status_code=502, detail=parsed)
    return {"status": "success", "data": parsed}

@app.get("/api/masters/groups")
def get_groups(company: Optional[str] = Query(None, description="Optional target company name")):
    """Extracts all ledger groups."""
    xml_req = tdl_templates.get_groups_xml(company_name=company)
    success, raw, parsed = tally_client.execute_xml(xml_req)
    if not success:
        raise HTTPException(status_code=502, detail=parsed)
    return {"status": "success", "data": parsed}

@app.get("/api/masters/stock-items")
def get_stock_items(company: Optional[str] = Query(None, description="Optional target company name")):
    """Extracts all stock items with closing balance, rate, and units."""
    xml_req = tdl_templates.get_stock_items_xml(company_name=company)
    success, raw, parsed = tally_client.execute_xml(xml_req)
    if not success:
        raise HTTPException(status_code=502, detail=parsed)
    return {"status": "success", "data": parsed}

@app.get("/api/vouchers/daybook")
def get_daybook(
    from_date: Optional[str] = Query(None, description="Start date (YYYYMMDD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYYMMDD)"),
    company: Optional[str] = Query(None, description="Optional target company name")
):
    """Extracts daybook vouchers."""
    xml_req = tdl_templates.get_daybook_xml(from_date=from_date, to_date=to_date, company_name=company)
    success, raw, parsed = tally_client.execute_xml(xml_req)
    if not success:
        raise HTTPException(status_code=502, detail=parsed)
    return {"status": "success", "data": parsed}

@app.get("/api/vouchers/by-type")
def get_vouchers_by_type(
    voucher_type: str = Query(..., description="Voucher type (e.g. Sales, Purchase, Payment, Receipt, Journal)"),
    from_date: Optional[str] = Query(None, description="Start date (YYYYMMDD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYYMMDD)"),
    company: Optional[str] = Query(None, description="Optional target company name")
):
    """Extracts vouchers filtered by type."""
    xml_req = tdl_templates.get_vouchers_by_type_xml(voucher_type=voucher_type, from_date=from_date, to_date=to_date, company_name=company)
    success, raw, parsed = tally_client.execute_xml(xml_req)
    if not success:
        raise HTTPException(status_code=502, detail=parsed)
    return {"status": "success", "data": parsed}

@app.post("/api/vouchers/post")
def post_voucher(payload: PostVoucherRequest):
    """
    Posts a voucher XML payload to Tally and returns status and GUID.
    """
    result = tally_client.post_voucher_xml(payload.voucher_xml)
    return result

@app.post("/api/query/raw-xml")
def execute_raw_xml(payload: RawXmlRequest):
    """
    Executes any raw TDL or XML query against Tally.
    Useful for custom reports, ODBC equivalent queries, and ad-hoc extraction.
    """
    success, raw, parsed = tally_client.execute_xml(payload.xml)
    return {
        "success": success,
        "raw_response": raw,
        "parsed_json": parsed
    }
