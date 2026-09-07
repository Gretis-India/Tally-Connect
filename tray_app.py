"""
Tally Connect System Tray Application.
Runs in the Windows Taskbar Notification Area (Tray) with Start, Stop, Pause,
Open Dashboard, Configure, and Exit capabilities.
"""
import os
import sys
import time
import json
import threading
import webbrowser
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import uvicorn

# Add current and parent dir to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

CONFIG_PATH = os.path.join(CURRENT_DIR, "config.json")

class TallyTrayApp:
    def __init__(self):
        self.load_config()
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.is_paused = False
        self.tray_icon = None

    def load_config(self):
        self.host = "0.0.0.0"
        self.port = 9100
        self.tally_url = "http://localhost:9000"
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.host = cfg.get("service_host", self.host)
                    self.port = cfg.get("service_port", self.port)
                    self.tally_url = cfg.get("tally_url", self.tally_url)
            except Exception:
                pass

    def create_icon_image(self, status="running"):
        """Generates dynamic crisp circle tray icon."""
        width = 64
        height = 64
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Outer dark ring
        draw.ellipse((4, 4, 60, 60), fill=(24, 24, 28, 255), outline=(255, 255, 255, 60), width=2)

        # Inner status circle
        if status == "running":
            color = (48, 209, 88, 255) # iOS Green
        elif status == "paused":
            color = (255, 214, 10, 255) # Yellow
        else:
            color = (255, 69, 58, 255) # Red

        draw.ellipse((20, 20, 44, 44), fill=color)
        return image

    def start_service(self, icon=None, item=None):
        if self.is_running:
            return
        
        self.load_config()
        print(f"[*] Starting Tally Connect Server on {self.host}:{self.port} ...")
        
        from tally_connect.main import app
        config = uvicorn.Config(app=app, host=self.host, port=self.port, log_level="info")
        self.server = uvicorn.Server(config)
        
        def run():
            self.is_running = True
            self.is_paused = False
            self.update_tray_state("running")
            self.server.run()
            self.is_running = False
            self.update_tray_state("stopped")

        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()

    def stop_service(self, icon=None, item=None):
        if not self.is_running or not self.server:
            return
        print("[*] Stopping Tally Connect Server ...")
        self.server.should_exit = True
        self.is_running = False
        self.is_paused = False
        self.update_tray_state("stopped")

    def toggle_pause(self, icon=None, item=None):
        if not self.is_running:
            return
        self.is_paused = not self.is_paused
        status = "paused" if self.is_paused else "running"
        self.update_tray_state(status)
        print(f"[*] Tally Connect is now {'PAUSED' if self.is_paused else 'RESUMED'}")

    def update_tray_state(self, status):
        if self.tray_icon:
            self.tray_icon.icon = self.create_icon_image(status)
            title_map = {
                "running": f"Tally Connect: Running (Port {self.port})",
                "paused": "Tally Connect: Paused",
                "stopped": "Tally Connect: Stopped"
            }
            self.tray_icon.title = title_map.get(status, "Tally Connect")

    def open_dashboard(self, icon=None, item=None):
        webbrowser.open(f"http://localhost:{self.port}")

    def open_api_docs(self, icon=None, item=None):
        webbrowser.open(f"http://localhost:{self.port}/docs")

    def exit_app(self, icon=None, item=None):
        print("[*] Exiting Tally Connect Tray App...")
        self.stop_service()
        if self.tray_icon:
            self.tray_icon.stop()
        sys.exit(0)

    def build_menu(self):
        return pystray.Menu(
            item("Tally Connect Agent", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item("Open Dashboard UI", self.open_dashboard, default=True),
            item("Open API Docs (/docs)", self.open_api_docs),
            pystray.Menu.SEPARATOR,
            item("Start Service", self.start_service, checked=lambda item: self.is_running and not self.is_paused),
            item("Pause / Resume", self.toggle_pause, checked=lambda item: self.is_paused, enabled=lambda item: self.is_running),
            item("Stop Service", self.stop_service, enabled=lambda item: self.is_running),
            pystray.Menu.SEPARATOR,
            item("Exit", self.exit_app)
        )

    def run(self):
        # Start the background service automatically
        self.start_service()

        # Create system tray icon
        self.tray_icon = pystray.Icon(
            name="TallyConnect",
            icon=self.create_icon_image("running"),
            title=f"Tally Connect: Running (Port {self.port})",
            menu=self.build_menu()
        )
        self.tray_icon.run()

if __name__ == "__main__":
    app = TallyTrayApp()
    app.run()
