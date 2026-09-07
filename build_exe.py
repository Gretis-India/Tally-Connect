"""
Build script to generate a standalone Windows executable (.exe) for Tally Connect.
Uses PyInstaller to bundle Python, FastAPI, Uvicorn, Pystray, static templates,
and icons into a single distributable executable.
"""
import os
import sys
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

def build():
    print("==================================================")
    print("      Building Tally Connect Windows Executable   ")
    print("==================================================")

    static_path = os.path.join(CURRENT_DIR, "static")
    templates_path = os.path.join(CURRENT_DIR, "templates")
    config_path = os.path.join(CURRENT_DIR, "config.json")

    # Separator for PyInstaller --add-data: ';' on Windows, ':' on Unix
    sep = ";" if sys.platform.startswith("win") else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=TallyConnect",
        "--noconsole",
        "--onefile",
        f"--add-data={static_path}{sep}static",
        f"--add-data={templates_path}{sep}templates",
        f"--add-data={config_path}{sep}.",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.lifespans",
        "--hidden-import=uvicorn.lifespans.on",
        "--hidden-import=pystray._win32",
        os.path.join(CURRENT_DIR, "tray_app.py")
    ]

    print(f"Executing: {' '.join(cmd)}\n")
    res = subprocess.run(cmd, cwd=CURRENT_DIR)
    if res.returncode == 0:
        print("\n✔ Successfully built TallyConnect executable!")
        print(f"Location: {os.path.join(CURRENT_DIR, 'dist', 'TallyConnect.exe' if sys.platform.startswith('win') else 'TallyConnect')}")
    else:
        print(f"\n❌ Build failed with exit code {res.returncode}")

if __name__ == "__main__":
    build()
