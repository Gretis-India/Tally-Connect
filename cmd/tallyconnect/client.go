package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"

	xj "github.com/basgys/goxml2json"
)

type TallyClient struct {
	mu      sync.RWMutex
	HostURL string
	Timeout time.Duration
	client  *http.Client
}

func NewTallyClient(hostURL string, timeoutSec int) *TallyClient {
	return &TallyClient{
		HostURL: strings.TrimRight(hostURL, "/"),
		Timeout: time.Duration(timeoutSec) * time.Second,
		client: &http.Client{
			Timeout: time.Duration(timeoutSec) * time.Second,
		},
	}
}

func (c *TallyClient) SetHostURL(u string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.HostURL = strings.TrimRight(u, "/")
}

func (c *TallyClient) GetHostURL() string {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.HostURL
}

func (c *TallyClient) ExecuteXML(xmlPayload string) (bool, string, interface{}) {
	req, err := http.NewRequest("POST", c.GetHostURL(), bytes.NewBufferString(xmlPayload))
	if err != nil {
		return false, "", map[string]string{"error": err.Error()}
	}
	req.Header.Set("Content-Type", "text/xml; charset=utf-8")

	resp, err := c.client.Do(req)
	if err != nil {
		if strings.Contains(err.Error(), "connection refused") || strings.Contains(err.Error(), "no such host") {
			return false, "", map[string]string{"error": fmt.Sprintf("Cannot connect to Tally at %s. Is Tally open and XML Server enabled?", c.GetHostURL())}
		}
		return false, "", map[string]string{"error": err.Error()}
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return false, "", map[string]string{"error": "Failed reading response from Tally"}
	}
	rawText := string(bodyBytes)
	if strings.TrimSpace(rawText) == "" {
		return false, "", map[string]string{"error": "Empty response from Tally"}
	}

	// Convert XML to JSON
	jsonBuf, err := xj.Convert(strings.NewReader(rawText))
	if err != nil {
		return true, rawText, map[string]interface{}{"raw": rawText, "parse_error": err.Error()}
	}

	var parsed interface{}
	if err := json.Unmarshal(jsonBuf.Bytes(), &parsed); err != nil {
		return true, rawText, map[string]interface{}{"raw": rawText, "parse_error": err.Error()}
	}

	return true, rawText, parsed
}

func (c *TallyClient) CheckHealth() map[string]interface{} {
	success, raw, data := c.ExecuteXML(GetCompaniesXML())
	if !success {
		errMsg := "Unknown error"
		if m, ok := data.(map[string]string); ok {
			errMsg = m["error"]
		}
		return map[string]interface{}{
			"status":    "offline",
			"tally_url": c.GetHostURL(),
			"connected": false,
			"error":     errMsg,
		}
	}

	preview := raw
	if len(preview) > 200 {
		preview = preview[:200]
	}

	return map[string]interface{}{
		"status":      "online",
		"tally_url":   c.GetHostURL(),
		"connected":   true,
		"raw_preview": preview,
	}
}

func (c *TallyClient) PostVoucherXML(voucherXML string) map[string]interface{} {
	payload := strings.TrimSpace(voucherXML)
	if !strings.HasPrefix(payload, "<ENVELOPE") {
		payload = fmt.Sprintf(`<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>All Masters</REPORTNAME>
            </REQUESTDESC>
            <REQUESTDATA>
                %s
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>`, payload)
	}

	success, raw, data := c.ExecuteXML(payload)
	if !success {
		errMsg := "Failed to communicate with Tally"
		if m, ok := data.(map[string]string); ok {
			errMsg = m["error"]
		}
		return map[string]interface{}{
			"status": "Failed",
			"guid":   "",
			"error":  errMsg,
		}
	}

	isSuccess := strings.Contains(raw, "<CREATED>1</CREATED>") || strings.Contains(raw, "<ALTERED>1</ALTERED>")
	guid := ""
	errorMsg := ""

	if isSuccess {
		// Attempt to extract GUID
		if idx := strings.Index(raw, "<LASTVCHID>"); idx != -1 {
			end := strings.Index(raw[idx:], "</LASTVCHID>")
			if end != -1 {
				guid = raw[idx+11 : idx+end]
			}
		}
		if guid == "" {
			if idx := strings.Index(raw, "<GUID>"); idx != -1 {
				end := strings.Index(raw[idx:], "</GUID>")
				if end != -1 {
					guid = raw[idx+6 : idx+end]
				}
			}
		}
	} else {
		if strings.Contains(raw, "<LINEERROR>") {
			idx := strings.Index(raw, "<LINEERROR>")
			end := strings.Index(raw[idx:], "</LINEERROR>")
			if end != -1 {
				errorMsg = raw[idx+11 : idx+end]
			}
		}
		if errorMsg == "" {
			if len(raw) > 400 {
				errorMsg = raw[:400]
			} else {
				errorMsg = raw
			}
		}
	}

	statusStr := "Failed"
	if isSuccess {
		statusStr = "Success"
	}

	return map[string]interface{}{
		"status":       statusStr,
		"guid":         guid,
		"error":        errorMsg,
		"raw_response": raw,
	}
}
