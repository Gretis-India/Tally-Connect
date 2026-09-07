' Silent VBScript Launcher & Python Auto-Installer for Tally Connect
' Ensures 100% zero manual prerequisites on Windows machines
Option Explicit
Dim WshShell, fso, strCurDir, strPython, cmd

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strCurDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Check if Python or pythonw exists in system PATH or common directories
Function CheckPython()
    Dim paths, p, sysDrive, ret
    sysDrive = WshShell.ExpandEnvironmentStrings("%SystemDrive%")
    CheckPython = ""

    ' Priority 1: Check environment PATH
    On Error Resume Next
    ret = WshShell.Run("pythonw.exe --version", 0, True)
    If ret = 0 Then
        CheckPython = "pythonw.exe"
        On Error GoTo 0
        Exit Function
    End If
    
    ret = WshShell.Run("python.exe --version", 0, True)
    If ret = 0 Then
        CheckPython = "python.exe"
        On Error GoTo 0
        Exit Function
    End If
    
    ret = WshShell.Run("py.exe --version", 0, True)
    If ret = 0 Then
        CheckPython = "py.exe"
        On Error GoTo 0
        Exit Function
    End If
    On Error GoTo 0

    ' Priority 2: Check common Windows installation locations
    paths = Array(_
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python312\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python311\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python310\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python39\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python312\python.exe", _
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python311\python.exe", _
        WshShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Python312\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Python311\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Python310\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Python312\python.exe", _
        sysDrive & "\Python312\pythonw.exe", _
        sysDrive & "\Python311\pythonw.exe", _
        sysDrive & "\Python310\pythonw.exe" _
    )

    For Each p In paths
        If fso.FileExists(p) Then
            CheckPython = """" & p & """"
            Exit Function
        End If
    Next
End Function

' Downloads and silently installs official Python 64-bit for Windows
Sub InstallPythonSilently()
    Dim tempFolder, installerPath, downloadUrl, psCmd, runRes, ans
    tempFolder = WshShell.ExpandEnvironmentStrings("%TEMP%")
    installerPath = tempFolder & "\python_installer.exe"
    downloadUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"

    ans = MsgBox("Python is not detected on this Windows PC." & vbCrLf & vbCrLf & _
                 "Would you like Tally Connect Setup to automatically download and install Python 3.11 silently in the background?", _
                 vbYesNo + vbInformation, "Tally Connect - Python Setup Required")
    
    If ans <> vbYes Then
        MsgBox "Installation cancelled. Please install Python 3.10+ and re-run Setup.", vbExclamation, "Tally Connect"
        WScript.Quit 1
    End If

    ' Download Python silently using PowerShell (built-in on all Windows 7/10/11)
    psCmd = "powershell -Command ""[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " & _
            "(New-Object System.Net.WebClient).DownloadFile('" & downloadUrl & "', '" & installerPath & "')"""
    
    runRes = WshShell.Run(psCmd, 0, True)

    ' Execute Python installer silently with PATH and pip enabled
    If fso.FileExists(installerPath) Then
        ' InstallAllUsers=1 PrependPath=1 Include_pip=1 /quiet
        runRes = WshShell.Run("""" & installerPath & """ /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_tcltk=1", 0, True)
        
        ' Clean up installer
        On Error Resume Next
        fso.DeleteFile installerPath, True
        On Error GoTo 0
    Else
        MsgBox "Failed to download Python installer automatically. Please check your internet connection.", vbCritical, "Download Error"
        WScript.Quit 1
    End If
End Sub

' 1. Locate Python or Auto-Install
strPython = CheckPython()

If strPython = "" Then
    InstallPythonSilently()
    ' Re-check after installation
    strPython = CheckPython()
    If strPython = "" Then
        ' If registry PATH has not refreshed yet in current session, check the standard install target
        Dim standardPath
        standardPath = WshShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Python311\pythonw.exe"
        If fso.FileExists(standardPath) Then
            strPython = """" & standardPath & """"
        Else
            strPython = "python.exe"
        End If
    End If
End If

' 2. Launch installer_gui.py completely hidden (window style 0 = hidden)
cmd = strPython & " """ & strCurDir & "\installer_gui.py"""

On Error Resume Next
WshShell.Run cmd, 0, False

If Err.Number <> 0 Then
    ' Fallback to command line launcher if windowless launch fails
    WshShell.Run "cmd /c python """ & strCurDir & "\installer_gui.py""", 1, False
End If
On Error GoTo 0

Set fso = Nothing
Set WshShell = Nothing
