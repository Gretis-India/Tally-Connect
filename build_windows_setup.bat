@echo off
title Build Tally Connect Windows Setup & Executable
cd /d %~dp0

echo ============================================================
echo      Step 1: Installing Required Windows Build Tools
echo ============================================================
pip install -r requirements.txt
pip install pystray pillow pyinstaller

echo.
echo ============================================================
echo      Step 2: Compiling Standalone TallyConnect.exe
echo ============================================================
python build_exe.py

echo.
echo ============================================================
echo      Step 3: Building Setup Wizard Installer (If Inno Setup Installed)
echo ============================================================
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
    echo Setup Wizard successfully created in setup_output\ folder!
) else (
    echo Note: Inno Setup 6 not found in default path.
    echo Standalone executable is available in dist\TallyConnect.exe
    echo To compile Setup Wizard .exe, install Inno Setup 6 and run this script again.
)

pause
