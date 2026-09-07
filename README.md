# Tally Connect

Tally Connect is a Windows Desktop Agent & System Tray utility that interfaces directly with local or remote Tally Prime / ERP 9 XML servers.

## Features
- **Taskbar System Tray Controller**: Runs unobtrusively in the Windows notification area with Start, Stop, Pause/Resume, and Dashboard controls.
- **Apple-Inspired Configuration UI**: Web UI on port `9100` (`http://localhost:9100`) with dialogs to configure Tally XML port/host and inspect loaded companies.
- **TDL Query & Extraction Engine**: Extract Ledgers, Groups, Stock Items, Daybook, and arbitrary XML reports.
- **Silent Windows Setup Wizard**: UAC Administrator setup (`silent_setup.vbs` / `installer_gui.py`) with zero console window popups and automatic Python installation.

## Running on Windows
- Double-click `silent_setup.vbs` to install and launch directly into your taskbar.
- Or run `start_tray.bat` for debug console mode.
