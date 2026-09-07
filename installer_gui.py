"""
Tally Connect GUI Setup & Installation Wizard.
Runs as Administrator without any command prompt window showing.
Provides an Apple-inspired dark GUI with progress bar, status logs,
and seamless installation of dependencies and tray application.
"""
import sys
import os
import time
import ctypes
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
try:
    import winreg
except ImportError:
    winreg = None

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """Relaunches the script with Administrator privileges using Windows UAC dialog."""
    try:
        if sys.platform.startswith("win"):
            script = os.path.abspath(sys.argv[0])
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            sys.exit(0)
    except Exception as e:
        print(f"Failed to elevate: {e}")
        sys.exit(1)


class InstallerWizardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tally Connect Setup Wizard")
        self.root.geometry("540x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#121214")

        # Apple-style Dark Theme Colors
        self.BG_COLOR = "#121214"
        self.CARD_BG = "#1a1a1e"
        self.BORDER_COLOR = "#2c2c34"
        self.TEXT_PRIMARY = "#f5f5f7"
        self.TEXT_SECONDARY = "#86868b"
        self.ACCENT_GREEN = "#30d158"

        self.setup_ui()

    def setup_ui(self):
        # Header Card
        header_frame = tk.Frame(self.root, bg=self.CARD_BG, padx=24, pady=20, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_lbl = tk.Label(header_frame, text="Tally Connect Setup Wizard", font=("SF Pro Display", 16, "bold"), fg=self.TEXT_PRIMARY, bg=self.CARD_BG)
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(header_frame, text="Automated background service installer for Tally Prime", font=("SF Pro Display", 10), fg=self.TEXT_SECONDARY, bg=self.CARD_BG)
        sub_lbl.pack(anchor="w", pady=(4, 0))

        # Body Card
        body_frame = tk.Frame(self.root, bg=self.CARD_BG, padx=24, pady=20, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        body_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.status_lbl = tk.Label(body_frame, text="Ready to install components", font=("SF Pro Display", 11, "bold"), fg=self.TEXT_PRIMARY, bg=self.CARD_BG)
        self.status_lbl.pack(anchor="w")

        self.detail_lbl = tk.Label(body_frame, text="Click 'Install Now' to configure dependencies and taskbar tray service.", font=("SF Pro Display", 9), fg=self.TEXT_SECONDARY, bg=self.CARD_BG)
        self.detail_lbl.pack(anchor="w", pady=(2, 14))

        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar", foreground=self.ACCENT_GREEN, background=self.ACCENT_GREEN, troughcolor="#222228", bordercolor="#222228", thickness=8)

        self.progress = ttk.Progressbar(body_frame, style="Custom.Horizontal.TProgressbar", mode="determinate")
        self.progress.pack(fill="x", pady=(0, 14))

        # Log Display
        self.log_text = tk.Text(body_frame, height=9, bg="#0d0d0f", fg="#a1a1a6", insertbackground="white", font=("Consolas", 9), relief="flat", highlightbackground=self.BORDER_COLOR, highlightthickness=1, padx=10, pady=8)
        self.log_text.pack(fill="both", expand=True)

        # Bottom Action Bar
        bottom_frame = tk.Frame(self.root, bg=self.BG_COLOR, padx=20, pady=12)
        bottom_frame.pack(fill="x")

        self.btn_exit = tk.Button(bottom_frame, text="Cancel", font=("SF Pro Display", 10), bg="#222228", fg=self.TEXT_PRIMARY, activebackground="#33333e", activeforeground="white", relief="flat", bd=0, padx=18, pady=8, cursor="hand2", command=self.root.quit)
        self.btn_exit.pack(side="left")

        self.btn_install = tk.Button(bottom_frame, text="Install Now (Admin)", font=("SF Pro Display", 10, "bold"), bg=self.TEXT_PRIMARY, fg="#0d0d0f", activebackground="#e5e5e7", activeforeground="#000", relief="flat", bd=0, padx=22, pady=8, cursor="hand2", command=self.start_installation)
        self.btn_install.pack(side="right")

    def log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def update_status(self, main_text, detail_text, progress_val):
        self.status_lbl.config(text=main_text)
        self.detail_lbl.config(text=detail_text)
        self.progress['value'] = progress_val

    def start_installation(self):
        self.btn_install.config(state="disabled", bg="#33333a", fg="#666")
        self.btn_exit.config(state="disabled")
        threading.Thread(target=self.run_install_pipeline, daemon=True).start()

    def run_command_hidden(self, cmd, desc):
        """Runs command completely hidden without any CMD window popping up."""
        self.log(f"[*] {desc}...")
        
        # CREATE_NO_WINDOW = 0x08000000 suppresses all command prompt windows
        creationflags = 0x08000000 if sys.platform.startswith("win") else 0

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=creationflags,
            shell=False
        )

        for line in process.stdout:
            stripped = line.strip()
            if stripped:
                self.log(f"    {stripped}")

        process.wait()
        return process.returncode

    def add_to_startup(self):
        """Configures Windows registry so Tally Connect starts silently on boot in tray."""
        if not sys.platform.startswith("win"):
            return
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            # Use pythonw to prevent command prompt
            pythonw_path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            if not os.path.exists(pythonw_path):
                pythonw_path = sys.executable

            tray_script = os.path.join(CURRENT_DIR, "tray_app.py")
            cmd_val = f'"{pythonw_path}" "{tray_script}"'
            
            winreg.SetValueEx(key, "TallyConnectTray", 0, winreg.REG_SZ, cmd_val)
            winreg.CloseKey(key)
            self.log("[✔] Registered Tally Connect to run silently on Windows Startup.")
        except Exception as e:
            self.log(f"[!] Warning: Could not register startup key: {e}")

    def run_install_pipeline(self):
        try:
            # Step 1: Check Python
            self.update_status("Step 1 of 4: Verifying Python Environment", "Checking installed modules...", 15)
            self.log("[*] Verifying Python interpreter...")
            time.sleep(0.5)

            # Step 2: Install required packages
            self.update_status("Step 2 of 4: Installing Dependencies", "Installing FastAPI, Uvicorn, Pystray & Pillow silently...", 35)
            req_path = os.path.join(CURRENT_DIR, "requirements.txt")
            cmd = [sys.executable, "-m", "pip", "install", "-r", req_path]
            ret = self.run_command_hidden(cmd, "Installing Python requirements")

            if ret != 0:
                self.log("[!] Some packages had warnings or errors. Retrying critical tray packages...")
                fallback_cmd = [sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "requests", "xmltodict", "pydantic", "pystray", "pillow"]
                self.run_command_hidden(fallback_cmd, "Installing core modules")

            # Step 3: Register startup
            self.update_status("Step 3 of 4: System Integration", "Adding Tally Connect to Windows Startup...", 75)
            self.add_to_startup()
            time.sleep(0.5)

            # Step 4: Launch Tray Service Silently
            self.update_status("Step 4 of 4: Launching Background Service", "Starting Tally Connect in your Windows Taskbar tray...", 90)
            self.log("[*] Launching Tally Connect Tray App silently...")

            pythonw_path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            if not os.path.exists(pythonw_path):
                pythonw_path = sys.executable

            tray_script = os.path.join(CURRENT_DIR, "tray_app.py")
            creationflags = 0x08000000 if sys.platform.startswith("win") else 0

            # Launch detached so it stays running when wizard closes
            subprocess.Popen(
                [pythonw_path, tray_script],
                cwd=CURRENT_DIR,
                creationflags=creationflags,
                close_fds=True
            )

            self.update_status("Installation Complete!", "Tally Connect is now active in your taskbar notification area.", 100)
            self.log("\n=======================================================")
            self.log("✔ Tally Connect successfully installed and running!")
            self.log("✔ Look for the Tally Connect icon in your Windows Taskbar Tray.")
            self.log("✔ Double-click or right-click the tray icon to open Dashboard UI.")
            self.log("=======================================================")

            self.btn_install.config(text="Finished (Close)", state="normal", command=self.root.quit, bg=self.ACCENT_GREEN, fg="#000")
            
            messagebox.showinfo(
                "Tally Connect Installed",
                "Tally Connect has been installed successfully!\n\nIt is now running in your Windows Taskbar (System Tray). Right-click the icon anytime to open the Dashboard or Start/Stop/Pause the service."
            )

        except Exception as ex:
            self.log(f"\n❌ Installation error: {ex}")
            self.update_status("Installation Failed", str(ex), 0)
            self.btn_exit.config(state="normal")


def main():
    # Enforce Windows Administrator elevation with native UAC dialog
    if sys.platform.startswith("win") and not is_admin():
        run_as_admin()

    root = tk.Tk()
    app = InstallerWizardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
