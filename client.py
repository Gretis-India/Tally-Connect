"""
Tally Client for communicating directly with Tally Prime / ERP 9 XML Server.
Handles requests, encoding, timeout, and response parsing.
"""
import requests
import xmltodict
from typing import Dict, Any, Tuple


class TallyClient:
    def __init__(self, host_url: str = "http://localhost:9000", timeout: int = 15):
        self.host_url = host_url.rstrip("/")
        self.timeout = timeout

    def set_host_url(self, host_url: str):
        self.host_url = host_url.rstrip("/")

    def execute_xml(self, xml_payload: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Sends raw XML payload to Tally.
        Returns (success: bool, raw_xml: str, parsed_dict: dict).
        """
        headers = {"Content-Type": "text/xml; charset=utf-8"}
        try:
            response = requests.post(
                self.host_url,
                data=xml_payload.encode("utf-8"),
                headers=headers,
                timeout=self.timeout
            )
            raw_text = response.text
            
            # Check for empty response
            if not raw_text.strip():
                return False, "", {"error": "Empty response from Tally"}

            try:
                parsed = xmltodict.parse(raw_text)
            except Exception as pe:
                parsed = {"raw": raw_text, "parse_error": str(pe)}

            return True, raw_text, parsed

        except requests.exceptions.ConnectionError:
            return False, "", {"error": f"Cannot connect to Tally at {self.host_url}. Is Tally open and XML Server enabled?"}
        except requests.exceptions.Timeout:
            return False, "", {"error": f"Timeout after {self.timeout}s communicating with Tally at {self.host_url}"}
        except Exception as e:
            return False, "", {"error": str(e)}

    def check_health(self) -> Dict[str, Any]:
        """Verifies if Tally is reachable and checks the active company."""
        from tally_connect.tdl_templates import get_companies_xml
        success, raw, data = self.execute_xml(get_companies_xml())
        
        if not success:
            return {
                "status": "offline",
                "tally_url": self.host_url,
                "connected": False,
                "error": data.get("error", "Unknown error")
            }

        # Try to extract company name
        companies = []
        try:
            envelope = data.get("ENVELOPE", {})
            body = envelope.get("BODY", {})
            data_sec = body.get("DATA", {})
            col = data_sec.get("COLLECTION", {})
            company_list = col.get("COMPANY", [])
            
            if isinstance(company_list, dict):
                company_list = [company_list]
            elif isinstance(company_list, str):
                company_list = [{"NAME": company_list}]
                
            companies = company_list
        except Exception:
            pass

        return {
            "status": "online",
            "tally_url": self.host_url,
            "connected": True,
            "companies": companies,
            "raw_preview": raw[:200] if raw else ""
        }

    def post_voucher_xml(self, voucher_xml: str) -> Dict[str, Any]:
        """
        Posts voucher XML to Tally and parses the result.
        Detects CREATED, ALTERED, ERRORS, and GUID.
        """
        # Ensure it has ENVELOPE tags if not already wrapped
        payload = voucher_xml.strip()
        if not payload.startswith("<ENVELOPE"):
            payload = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>All Masters</REPORTNAME>
            </REQUESTDESC>
            <REQUESTDATA>
                {payload}
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""

        success, raw, parsed = self.execute_xml(payload)
        if not success:
            return {
                "status": "Failed",
                "guid": "",
                "error": parsed.get("error", "Failed to communicate with Tally"),
                "raw_response": ""
            }

        # Parse success or failure from Tally response
        guid = ""
        error_msg = ""
        is_success = False

        if "<CREATED>1</CREATED>" in raw or "<ALTERED>1</ALTERED>" in raw:
            is_success = True
            try:
                guid = parsed.get("RESPONSE", {}).get("GUID", "") or parsed.get("ENVELOPE", {}).get("BODY", {}).get("DATA", {}).get("IMPORTRESULT", {}).get("LASTVCHID", "")
            except Exception:
                pass
        else:
            # Check for error tags in Tally XML
            if "<LINEERROR>" in raw:
                try:
                    errors = parsed.get("RESPONSE", {}).get("LINEERROR", [])
                    if isinstance(errors, list):
                        error_msg = "; ".join([str(e) for e in errors])
                    else:
                        error_msg = str(errors)
                except Exception:
                    error_msg = raw[:400]
            else:
                error_msg = raw[:400]

        return {
            "status": "Success" if is_success else "Failed",
            "guid": guid,
            "error": error_msg,
            "raw_response": raw
        }
