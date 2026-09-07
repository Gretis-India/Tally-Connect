"""
Builds the standalone GUI Setup Wizard Executable (SetupWizard.exe).
Runs with --noconsole and uac-admin so it prompts the native Windows
UAC Administrator popup and never opens a command prompt window.
"""
import os
import sys
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def build_installer():
    print("==================================================")
    print("  Compiling Tally Connect GUI Setup Executable   ")
    print("==================================================")

    static_path = os.path.join(CURRENT_DIR, "static")
    templates_path = os.path.join(CURRENT_DIR, "templates")
    config_path = os.path.join(CURRENT_DIR, "config.json")
    req_path = os.path.join(CURRENT_DIR, "requirements.txt")
    tray_path = os.path.join(CURRENT_DIR, "tray_app.py")
    main_path = os.path.join(CURRENT_DIR, "main.py")
    client_path = os.path.join(CURRENT_DIR, "client.py")
    tdl_path = os.path.join(CURRENT_DIR, "tdl_templates.py")

    sep = ";" if sys.platform.startswith("win") else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=TallyConnect_Setup",
        "--noconsole",
        "--onefile",
        "--uac-admin", # Triggers native Windows Administrator prompt
        f"--add-data={static_path}{sep}static",
        f"--add-data={templates_path}{sep}templates",
        f"--add-data={config_path}{sep}.",
        f"--add-data={req_path}{sep}.",
        f"--add-data={tray_path}{sep}.",
        f"--add-data={main_path}{sep}.",
        f"--add-data={client_path}{sep}.",
        f"--add-data={tdl_path}{sep}.",
        os.path.join(CURRENT_DIR, "installer_gui.py")
    ]

    print(f"Executing: {' '.join(cmd)}\n")
    res = subprocess.run(cmd, cwd=CURRENT_DIR)
    if res.returncode == 0:
        print("\n✔ Successfully compiled TallyConnect_Setup.exe!")
    else:
        print(f"\n❌ Build failed with exit code {res.returncode}")

if __name__ == "__main__":
    build_installer()
