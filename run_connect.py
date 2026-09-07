"""
Launcher for Tally Connect Service
"""
import sys
import os
import uvicorn
import json

# Ensure parent directory is in sys.path so tally_connect can be imported anywhere
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

CONFIG_PATH = os.environ.get("TALLY_CONNECT_CONFIG", os.path.join(CURRENT_DIR, "config.json"))
host = "0.0.0.0"
port = 8001

if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            host = cfg.get("service_host", host)
            port = cfg.get("service_port", port)
    except Exception:
        pass

if __name__ == "__main__":
    print(f"[*] Starting Tally Connect Service on {host}:{port} ...")
    uvicorn.run("tally_connect.main:app", host=host, port=port, reload=False, app_dir=PARENT_DIR)
