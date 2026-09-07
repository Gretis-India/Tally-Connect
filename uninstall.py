"""
Tally Connect Uninstaller.
Terminates running tray and server processes, removes Windows Startup registry key,
and cleans up installed artifacts.
"""
import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
try:
    import winreg
except ImportError:
    winreg = None

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def stop_running_processes():
    """Kills running instances of TallyConnect and tray apps."""
    if not sys.platform.startswith("win"):
        return
    targets = ["TallyConnect.exe", "pythonw.exe", "TallyConnect_Setup.exe"]
    for proc in targets:
        try:
            subprocess.run(["taskkill", "/F", "/IM", proc, "/T"], capture_output=True)
        except Exception:
            pass


def remove_from_startup():
    """Removes Tally Connect from Windows Run registry key."""
    if not sys.platform.startswith("win") or not winreg:
        return
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "TallyConnectTray")
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error removing registry key: {e}")


def uninstall():
    root = tk.Tk()
    root.withdraw()

    confirm = messagebox.askyesno(
        "Uninstall Tally Connect",
        "Are you sure you want to completely uninstall Tally Connect and stop all background services?"
    )
    if not confirm:
        sys.exit(0)

    stop_running_processes()
    remove_from_startup()

    messagebox.showinfo(
        "Tally Connect Uninstalled",
        "Tally Connect services stopped and Windows Startup entries removed successfully."
    )
    sys.exit(0)


if __name__ == "__main__":
    uninstall()
