@echo off
title Build Tally Connect Windows Setup & Executable
cd /d %~dp0

echo ============================================================
echo      Step 1: Compiling Native Windows Executable (Go)
echo ============================================================
set CGO_ENABLED=0
set GOOS=windows
set GOARCH=amd64
go build -ldflags="-H=windowsgui -s -w" -o dist\TallyConnect.exe .\cmd\tallyconnect
go build -ldflags="-H=windowsgui -s -w" -o dist\Uninstaller.exe .\cmd\uninstall

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
