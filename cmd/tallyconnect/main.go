package main

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"github.com/energye/systray"
)

//go:embed templates/*
var templatesFS embed.FS

//go:embed static/*
var staticFS embed.FS

type Config struct {
	ServiceName string `json:"service_name"`
	ServiceHost string `json:"service_host"`
	ServicePort int    `json:"service_port"`
	TallyURL    string `json:"tally_url"`
	Timeout     int    `json:"timeout"`
}

var (
	cfg     Config
	cfgMu   sync.RWMutex
	tClient *TallyClient
	cfgPath string

	isPaused   bool
	pausedMu   sync.RWMutex
	httpServer *http.Server
)

func loadConfig() {
	cfg = Config{
		ServiceName: "Tally Connect Agent",
		ServiceHost: "0.0.0.0",
		ServicePort: 9100,
		TallyURL:    "http://localhost:9000",
		Timeout:     20,
	}

	execPath, err := os.Executable()
	if err != nil {
		execPath = "."
	}
	execDir := filepath.Dir(execPath)
	cfgPath = filepath.Join(execDir, "config.json")

	if envCfg := os.Getenv("TALLY_CONNECT_CONFIG"); envCfg != "" {
		cfgPath = envCfg
	}

	if data, err := os.ReadFile(cfgPath); err == nil {
		_ = json.Unmarshal(data, &cfg)
	}
	tClient = NewTallyClient(cfg.TallyURL, cfg.Timeout)
}

func saveConfig() {
	cfgMu.RLock()
	data, err := json.MarshalIndent(cfg, "", "  ")
	cfgMu.RUnlock()
	if err == nil {
		_ = os.WriteFile(cfgPath, data, 0644)
	}
}

func openBrowser(url string) {
	var cmd string
	var args []string

	switch runtime.GOOS {
	case "windows":
		cmd = "rundll32"
		args = []string{"url.dll,FileProtocolHandler", url}
	case "darwin":
		cmd = "open"
		args = []string{url}
	default:
		cmd = "xdg-open"
		args = []string{url}
	}
	_ = exec.Command(cmd, args...).Start()
}

func jsonResponse(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(data)
}

func setupRoutes() *http.ServeMux {
	mux := http.NewServeMux()

	// Static files
	staticSub, _ := fs.Sub(staticFS, "static")
	mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.FS(staticSub))))

	// Index page
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		data, err := templatesFS.ReadFile("templates/index.html")
		if err != nil {
			http.Error(w, "Dashboard template not found", http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write(data)
	})

	// Health
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		jsonResponse(w, http.StatusOK, tClient.CheckHealth())
	})

	// Info
	mux.HandleFunc("/api/info", func(w http.ResponseWriter, r *http.Request) {
		cfgMu.RLock()
		defer cfgMu.RUnlock()
		jsonResponse(w, http.StatusOK, map[string]interface{}{
			"service":   cfg.ServiceName,
			"status":    "running",
			"tally_url": tClient.GetHostURL(),
			"docs":      "/docs",
		})
	})

	// Settings
	mux.HandleFunc("/api/settings/tally-url", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		var req struct {
			TallyURL string `json:"tally_url"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid JSON", http.StatusBadRequest)
			return
		}
		targetURL := strings.TrimSpace(req.TallyURL)
		if !strings.HasPrefix(targetURL, "http://") && !strings.HasPrefix(targetURL, "https://") {
			targetURL = "http://" + targetURL
		}
		tClient.SetHostURL(targetURL)
		cfgMu.Lock()
		cfg.TallyURL = targetURL
		cfgMu.Unlock()
		saveConfig()

		jsonResponse(w, http.StatusOK, map[string]interface{}{
			"message": fmt.Sprintf("Tally URL updated to %s", targetURL),
			"health":  tClient.CheckHealth(),
		})
	})

	// Companies
	mux.HandleFunc("/api/companies", func(w http.ResponseWriter, r *http.Request) {
		success, _, parsed := tClient.ExecuteXML(GetCompaniesXML())
		if !success {
			jsonResponse(w, http.StatusBadGateway, parsed)
			return
		}
		jsonResponse(w, http.StatusOK, map[string]interface{}{"status": "success", "data": parsed})
	})

	// Masters: Ledgers
	mux.HandleFunc("/api/masters/ledgers", func(w http.ResponseWriter, r *http.Request) {
		comp := r.URL.Query().Get("company")
		success, _, parsed := tClient.ExecuteXML(GetLedgersXML(comp))
		if !success {
			jsonResponse(w, http.StatusBadGateway, parsed)
			return
		}
		jsonResponse(w, http.StatusOK, map[string]interface{}{"status": "success", "data": parsed})
	})

	// Masters: Groups
	mux.HandleFunc("/api/masters/groups", func(w http.ResponseWriter, r *http.Request) {
		comp := r.URL.Query().Get("company")
		success, _, parsed := tClient.ExecuteXML(GetGroupsXML(comp))
		if !success {
			jsonResponse(w, http.StatusBadGateway, parsed)
			return
		}
		jsonResponse(w, http.StatusOK, map[string]interface{}{"status": "success", "data": parsed})
	})

	// Masters: Stock Items
	mux.HandleFunc("/api/masters/stock-items", func(w http.ResponseWriter, r *http.Request) {
		comp := r.URL.Query().Get("company")
		success, _, parsed := tClient.ExecuteXML(GetStockItemsXML(comp))
		if !success {
			jsonResponse(w, http.StatusBadGateway, parsed)
			return
		}
		jsonResponse(w, http.StatusOK, map[string]interface{}{"status": "success", "data": parsed})
	})

	// Daybook
	mux.HandleFunc("/api/vouchers/daybook", func(w http.ResponseWriter, r *http.Request) {
		from := r.URL.Query().Get("from_date")
		to := r.URL.Query().Get("to_date")
		comp := r.URL.Query().Get("company")
		success, _, parsed := tClient.ExecuteXML(GetDaybookXML(from, to, comp))
		if !success {
			jsonResponse(w, http.StatusBadGateway, parsed)
			return
		}
		jsonResponse(w, http.StatusOK, map[string]interface{}{"status": "success", "data": parsed})
	})

	// Vouchers by type
	mux.HandleFunc("/api/vouchers/by-type", func(w http.ResponseWriter, r *http.Request) {
		vType := r.URL.Query().Get("voucher_type")
		from := r.URL.Query().Get("from_date")
		to := r.URL.Query().Get("to_date")
		comp := r.URL.Query().Get("company")
		if vType == "" {
			http.Error(w, "voucher_type query parameter required", http.StatusBadRequest)
			return
		}
		success, _, parsed := tClient.ExecuteXML(GetVouchersByTypeXML(vType, from, to, comp))
		if !success {
			jsonResponse(w, http.StatusBadGateway, parsed)
			return
		}
		jsonResponse(w, http.StatusOK, map[string]interface{}{"status": "success", "data": parsed})
	})

	// Post voucher
	mux.HandleFunc("/api/vouchers/post", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		var req struct {
			VoucherXML string `json:"voucher_xml"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid JSON", http.StatusBadRequest)
			return
		}
		res := tClient.PostVoucherXML(req.VoucherXML)
		jsonResponse(w, http.StatusOK, res)
	})

	// Raw XML
	mux.HandleFunc("/api/query/raw-xml", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		var req struct {
			XML string `json:"xml"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid JSON", http.StatusBadRequest)
			return
		}
		success, raw, parsed := tClient.ExecuteXML(req.XML)
		jsonResponse(w, http.StatusOK, map[string]interface{}{
			"success": success,
			"raw":     raw,
			"data":    parsed,
		})
	})

	return mux
}

func startServer() {
	addr := fmt.Sprintf("%s:%d", cfg.ServiceHost, cfg.ServicePort)
	log.Printf("[*] Tally Connect native Go server starting on http://%s ...\n", addr)

	httpServer = &http.Server{
		Addr:    addr,
		Handler: setupRoutes(),
	}

	go func() {
		if err := httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Printf("[!] Server error: %v\n", err)
		}
	}()
}

func onReady() {
	// Set icon from embedded favicon.ico
	iconData, err := staticFS.ReadFile("static/favicon.ico")
	if err == nil {
		systray.SetIcon(iconData)
	}
	systray.SetTitle("Tally Connect")
	systray.SetTooltip(fmt.Sprintf("Tally Connect Agent (Port %d)", cfg.ServicePort))

	mTitle := systray.AddMenuItem("Tally Connect Agent", "Tally Connect Agent")
	mTitle.Disable()
	systray.AddSeparator()

	mOpen := systray.AddMenuItem("Open Dashboard UI", "Open Dashboard in browser")
	mDocs := systray.AddMenuItem("Open API Docs (/docs)", "Open API Documentation")
	systray.AddSeparator()

	mStatus := systray.AddMenuItem("Status: Running 🟢", "Current server status")
	mStatus.Disable()
	mPause := systray.AddMenuItem("Pause / Resume", "Toggle service pause")
	systray.AddSeparator()
	mExit := systray.AddMenuItem("Exit", "Quit Tally Connect")

	mOpen.Click(func() {
		openBrowser(fmt.Sprintf("http://localhost:%d", cfg.ServicePort))
	})
	mDocs.Click(func() {
		openBrowser(fmt.Sprintf("http://localhost:%d/docs", cfg.ServicePort))
	})
	mPause.Click(func() {
		pausedMu.Lock()
		isPaused = !isPaused
		if isPaused {
			mStatus.SetTitle("Status: Paused 🟡")
			mPause.Check()
		} else {
			mStatus.SetTitle("Status: Running 🟢")
			mPause.Uncheck()
		}
		pausedMu.Unlock()
	})
	mExit.Click(func() {
		systray.Quit()
	})

	startServer()
}

func onExit() {
	if httpServer != nil {
		_ = httpServer.Close()
	}
	os.Exit(0)
}

func main() {
	loadConfig()

	// If run with --server flag (headless/daemon) or non-GUI environment
	if len(os.Args) > 1 && os.Args[1] == "--server" {
		startServer()
		select {}
	}

	systray.Run(onReady, onExit)
}
