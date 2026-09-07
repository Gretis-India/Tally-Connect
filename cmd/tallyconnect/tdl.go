package main

import "fmt"

func BuildEnvelope(bodyXML string) string {
	return fmt.Sprintf(`<ENVELOPE>
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
            %s
        </EXPORTDATA>
    </BODY>
</ENVELOPE>`, bodyXML)
}

func GetCompaniesXML() string {
	return `<ENVELOPE>
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
</ENVELOPE>`
}

func GetLedgersXML(companyName string) string {
	compVar := ""
	if companyName != "" {
		compVar = fmt.Sprintf("<SVCURRENTCOMPANY>%s</SVCURRENTCOMPANY>", companyName)
	}
	return fmt.Sprintf(`<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>All Masters</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    %s
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
                            <FIELDS>LedgerName, LedgerParent, LedgerOpeningBalance, LedgerClosingBalance, LedgerGSTIN, LedgerGuid</FIELDS>
                        </LINE>
                        <FIELD NAME="LedgerName">
                            <SET>$Name</SET>
                            <XMLTAG>NAME</XMLTAG>
                        </FIELD>
                        <FIELD NAME="LedgerParent">
                            <SET>$Parent</SET>
                            <XMLTAG>PARENT</XMLTAG>
                        </FIELD>
                        <FIELD NAME="LedgerOpeningBalance">
                            <SET>$OpeningBalance</SET>
                            <XMLTAG>OPENINGBALANCE</XMLTAG>
                        </FIELD>
                        <FIELD NAME="LedgerClosingBalance">
                            <SET>$ClosingBalance</SET>
                            <XMLTAG>CLOSINGBALANCE</XMLTAG>
                        </FIELD>
                        <FIELD NAME="LedgerGSTIN">
                            <SET>$PartyGSTIN</SET>
                            <XMLTAG>GSTIN</XMLTAG>
                        </FIELD>
                        <FIELD NAME="LedgerGuid">
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
</ENVELOPE>`, compVar)
}

func GetGroupsXML(companyName string) string {
	compVar := ""
	if companyName != "" {
		compVar = fmt.Sprintf("<SVCURRENTCOMPANY>%s</SVCURRENTCOMPANY>", companyName)
	}
	return fmt.Sprintf(`<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>List of Groups</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    %s
                </STATICVARIABLES>
                <TDL>
                    <TDLMESSAGE>
                        <REPORT NAME="List of Groups">
                            <FORMS>Group Forms</FORMS>
                        </REPORT>
                        <FORM NAME="Group Forms">
                            <PARTS>Group Part</PARTS>
                        </FORM>
                        <PART NAME="Group Part">
                            <LINES>Group Line</LINES>
                            <REPEAT>Group Line : Group Collection</REPEAT>
                            <SCROLLED>Vertical</SCROLLED>
                        </PART>
                        <LINE NAME="Group Line">
                            <FIELDS>GroupName, GroupParent, GroupGuid</FIELDS>
                        </LINE>
                        <FIELD NAME="GroupName">
                            <SET>$Name</SET>
                            <XMLTAG>NAME</XMLTAG>
                        </FIELD>
                        <FIELD NAME="GroupParent">
                            <SET>$Parent</SET>
                            <XMLTAG>PARENT</XMLTAG>
                        </FIELD>
                        <FIELD NAME="GroupGuid">
                            <SET>$GUID</SET>
                            <XMLTAG>GUID</XMLTAG>
                        </FIELD>
                        <COLLECTION NAME="Group Collection">
                            <TYPE>Group</TYPE>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>`, compVar)
}

func GetStockItemsXML(companyName string) string {
	compVar := ""
	if companyName != "" {
		compVar = fmt.Sprintf("<SVCURRENTCOMPANY>%s</SVCURRENTCOMPANY>", companyName)
	}
	return fmt.Sprintf(`<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Stock Items</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    %s
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
</ENVELOPE>`, compVar)
}

func GetDaybookXML(fromDate, toDate, companyName string) string {
	staticVars := ""
	if fromDate != "" {
		staticVars += fmt.Sprintf("<SVFROMDATE>%s</SVFROMDATE>\n", fromDate)
	}
	if toDate != "" {
		staticVars += fmt.Sprintf("<SVTODATE>%s</SVTODATE>\n", toDate)
	}
	if companyName != "" {
		staticVars += fmt.Sprintf("<SVCURRENTCOMPANY>%s</SVCURRENTCOMPANY>\n", companyName)
	}

	return fmt.Sprintf(`<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Day Book</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    %s
                </STATICVARIABLES>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>`, staticVars)
}

func GetVouchersByTypeXML(voucherType, fromDate, toDate, companyName string) string {
	staticVars := fmt.Sprintf("<VOUCHERTYPENAME>%s</VOUCHERTYPENAME>\n", voucherType)
	if fromDate != "" {
		staticVars += fmt.Sprintf("<SVFROMDATE>%s</SVFROMDATE>\n", fromDate)
	}
	if toDate != "" {
		staticVars += fmt.Sprintf("<SVTODATE>%s</SVTODATE>\n", toDate)
	}
	if companyName != "" {
		staticVars += fmt.Sprintf("<SVCURRENTCOMPANY>%s</SVCURRENTCOMPANY>\n", companyName)
	}

	return fmt.Sprintf(`<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Voucher Register</REPORTNAME>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    %s
                </STATICVARIABLES>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>`, staticVars)
}
