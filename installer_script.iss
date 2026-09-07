; Inno Setup Script for Tally Connect
; Creates a professional Windows Setup Wizard (.exe)
; http://www.jrsoftware.org/isinfo.php

[Setup]
AppId={{D37E84B1-21B5-4D62-A8A9-9FE7B014F94C}
AppName=Tally Connect
AppVersion=1.0.0
AppPublisher=Gretis India
AppPublisherURL=https://gretis.com
DefaultDirName={autopf}\TallyConnect
DefaultGroupName=Tally Connect
AllowNoIcons=yes
OutputDir=setup_output
OutputBaseFilename=TallyConnect_Setup_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=static\favicon.ico
UninstallDisplayIcon={app}\TallyConnect.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Automatically launch Tally Connect on Windows Startup"; GroupDescription: "Windows Integration:"

[Files]
Source: "dist\TallyConnect.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Uninstaller.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\Tally Connect"; Filename: "{app}\TallyConnect.exe"
Name: "{group}\Uninstall Tally Connect"; Filename: "{app}\Uninstaller.exe"
Name: "{autodesktop}\Tally Connect"; Filename: "{app}\TallyConnect.exe"; Tasks: desktopicon
Name: "{userstartup}\Tally Connect"; Filename: "{app}\TallyConnect.exe"; Tasks: startupicon

[Run]
Filename: "{app}\TallyConnect.exe"; Description: "{cm:LaunchProgram,Tally Connect}"; Flags: nowait postinstall skipifsilent
