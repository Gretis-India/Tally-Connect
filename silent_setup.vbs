' Silent VBScript Launcher for Tally Connect
' Ensures 100% zero command prompt window popups on Windows
Set WshShell = CreateObject("WScript.Shell")
strCurDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Check if pythonw exists, otherwise fallback to python
Set fso = CreateObject("Scripting.FileSystemObject")
strPythonw = "pythonw.exe"

' Launch installer_gui.py completely hidden (0 = hide window)
WshShell.Run strPythonw & " """ & strCurDir & "\installer_gui.py""", 0, False
Set WshShell = Nothing
