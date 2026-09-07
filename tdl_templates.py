"""
TDL XML templates for querying Tally Prime / ERP 9 database.
Supports extracting Companies, Masters (Ledgers, Groups, Stock Items),
and Vouchers (Daybook, Voucher details) as well as raw envelope wrapping.
"""
from typing import Optional


def build_envelope(body_xml: str) -> str:
    """Wraps body XML inside standard Tally XML ENVELOPE."""
    return f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                </STATICVARIABLES>
            </REQUESTDESC>
            {body_xml}
        </EXPORTDATA>
    </BODY>
</ENVELOPE>"""


def get_companies_xml() -> str:
    """Generates TDL XML to retrieve list of currently open / active companies."""
    return """<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>List of Companies</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                </STATICVARIABLES>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>"""


def get_ledgers_xml(company_name: Optional[str] = None) -> str:
    """Generates TDL XML to export all Ledgers with detailed fields."""
    comp_var = f"<SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>" if company_name else ""
    return f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>All Masters</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {comp_var}
                </STATICVARIABLES>
                <TDL>
                    <TDLMESSAGE>
                        <REPORT NAME="All Masters">
                            <FORMS>All Masters</FORMS>
                        </REPORT>
                        <FORM NAME="All Masters">
                            <PARTS>Ledger Part</PARTS>
                        </FORM>
                        <PART NAME="Ledger Part">
                            <LINES>Ledger Line</LINES>
                            <REPEAT>Ledger Line : Ledger Collection</REPEAT>
                            <SCROLLED>Vertical</SCROLLED>
                        </PART>
                        <LINE NAME="Ledger Line">
                            <FIELDS>FldName, FldParent, FldOpeningBal, FldClosingBal, FldGSTIN, FldGuid</FIELDS>
                        </LINE>
                        <FIELD NAME="FldName">
                            <SET>$Name</SET>
                            <XMLTAG>NAME</XMLTAG>
                        </FIELD>
                        <FIELD NAME="FldParent">
                            <SET>$Parent</SET>
                            <XMLTAG>PARENT</XMLTAG>
                        </FIELD>
                        <FIELD NAME="FldOpeningBal">
                            <SET>$OpeningBalance</SET>
                            <XMLTAG>OPENINGBALANCE</XMLTAG>
                        </FIELD>
                        <FIELD NAME="FldClosingBal">
                            <SET>$ClosingBalance</SET>
                            <XMLTAG>CLOSINGBALANCE</XMLTAG>
                        </FIELD>
                        <FIELD NAME="FldGSTIN">
                            <SET>$PartyGSTIN</SET>
                            <XMLTAG>PARTYGSTIN</XMLTAG>
                        </FIELD>
                        <FIELD NAME="FldGuid">
                            <SET>$GUID</SET>
                            <XMLTAG>GUID</XMLTAG>
                        </FIELD>
                        <COLLECTION NAME="Ledger Collection">
                            <TYPE>Ledger</TYPE>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>"""


def get_groups_xml(company_name: Optional[str] = None) -> str:
    """Generates TDL XML to export all Ledger Groups."""
    comp_var = f"<SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>" if company_name else ""
    return f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>List of Groups</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {comp_var}
                </STATICVARIABLES>
                <TDL>
                    <TDLMESSAGE>
                        <COLLECTION NAME="Group Collection">
                            <TYPE>Group</TYPE>
                            <NATIVEMETHOD>Name, Parent, GUID</NATIVEMETHOD>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>"""


def get_stock_items_xml(company_name: Optional[str] = None) -> str:
    """Generates TDL XML to export Stock Items."""
    comp_var = f"<SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>" if company_name else ""
    return f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Stock Items</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {comp_var}
                </STATICVARIABLES>
                <TDL>
                    <TDLMESSAGE>
                        <REPORT NAME="Stock Items">
                            <FORMS>Stock Items</FORMS>
                        </REPORT>
                        <FORM NAME="Stock Items">
                            <PARTS>Stock Part</PARTS>
                        </FORM>
                        <PART NAME="Stock Part">
                            <LINES>Stock Line</LINES>
                            <REPEAT>Stock Line : Stock Collection</REPEAT>
                            <SCROLLED>Vertical</SCROLLED>
                        </PART>
                        <LINE NAME="Stock Line">
                            <FIELDS>StockName, StockBaseUnits, StockClosingBalance, StockClosingValue, StockClosingRate, StockGuid</FIELDS>
                        </LINE>
                        <FIELD NAME="StockName">
                            <SET>$Name</SET>
                            <XMLTAG>NAME</XMLTAG>
                        </FIELD>
                        <FIELD NAME="StockBaseUnits">
                            <SET>$BaseUnits</SET>
                            <XMLTAG>BASEUNITS</XMLTAG>
                        </FIELD>
                        <FIELD NAME="StockClosingBalance">
                            <SET>$ClosingBalance</SET>
                            <XMLTAG>CLOSINGBALANCE</XMLTAG>
                        </FIELD>
                        <FIELD NAME="StockClosingValue">
                            <SET>$ClosingValue</SET>
                            <XMLTAG>CLOSINGVALUE</XMLTAG>
                        </FIELD>
                        <FIELD NAME="StockClosingRate">
                            <SET>$ClosingRate</SET>
                            <XMLTAG>CLOSINGRATE</XMLTAG>
                        </FIELD>
                        <FIELD NAME="StockGuid">
                            <SET>$GUID</SET>
                            <XMLTAG>GUID</XMLTAG>
                        </FIELD>
                        <COLLECTION NAME="Stock Collection">
                            <TYPE>StockItem</TYPE>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>"""


def get_daybook_xml(from_date: Optional[str] = None, to_date: Optional[str] = None, company_name: Optional[str] = None) -> str:
    """
    Generates TDL XML to query Daybook vouchers.
    Dates should be formatted as YYYYMMDD (e.g. 20260401) or standard Tally dates.
    """
    date_filters = []
    if from_date:
        date_filters.append(f"<SVFROMDATE>{from_date}</SVFROMDATE>")
    if to_date:
        date_filters.append(f"<SVTODATE>{to_date}</SVTODATE>")
    if company_name:
        date_filters.append(f"<SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>")

    static_vars = "\n                    ".join(date_filters)

    return f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Day Book</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    {static_vars}
                </STATICVARIABLES>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>"""


def get_vouchers_by_type_xml(voucher_type: str, from_date: Optional[str] = None, to_date: Optional[str] = None, company_name: Optional[str] = None) -> str:
    """Generates TDL XML to retrieve vouchers filtered by voucher type (e.g. Sales, Purchase, Receipt, Payment)."""
    date_filters = []
    if from_date:
        date_filters.append(f"<SVFROMDATE>{from_date}</SVFROMDATE>")
    if to_date:
        date_filters.append(f"<SVTODATE>{to_date}</SVTODATE>")
    if company_name:
        date_filters.append(f"<SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>")

    static_vars = "\n                    ".join(date_filters)

    return f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Voucher Register</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    <VOUCHERTYPENAME>{voucher_type}</VOUCHERTYPENAME>
                    {static_vars}
                </STATICVARIABLES>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>"""
