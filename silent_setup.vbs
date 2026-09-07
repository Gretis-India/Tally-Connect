' Silent VBScript Launcher for Tally Connect
' Ensures 100% zero command prompt window popups on Windows
Option Explicit
Dim WshShell, fso, strCurDir, strPython, cmd

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strCurDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Check python executables in system PATH or common installation directories
Function FindPython()
    Dim paths, p, sysDrive
    sysDrive = WshShell.ExpandEnvironmentStrings("%SystemDrive%")
    
    ' Priority 1: Check environment PATH
    On Error Resume Next
    WshShell.Run "pythonw.exe --version", 0, True
    If Err.Number = 0 Then
        FindPython = "pythonw.exe"
        On Error GoTo 0
        Exit Function
    End If
    
    WshShell.Run "python.exe --version", 0, True
    If Err.Number = 0 Then
        FindPython = "python.exe"
        On Error GoTo 0
        Exit Function
    End If
    On Error GoTo 0

    ' Priority 2: Check common Windows install locations (User & Global)
    paths = Array(_
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python312\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python311\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python310\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python39\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python38\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Python312\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Python311\pythonw.exe", _
        WshShell.ExpandEnvironmentStrings("%ProgramFiles%") & "\Python310\pythonw.exe", _
        sysDrive & "\Python312\pythonw.exe", _
        sysDrive & "\Python311\pythonw.exe", _
        sysDrive & "\Python310\pythonw.exe" _
    )

    For Each p In paths
        If fso.FileExists(p) Then
            FindPython = """" & p & """"
            Exit Function
        End If
    Next

    ' Fallback to generic py launcher (standard on Windows 10/11)
    FindPython = "py.exe"
End Function

strPython = FindPython()

' Execute installer_gui.py completely hidden (window style 0 = hidden)
cmd = strPython & " """ & strCurDir & "\installer_gui.py"""
On Error Resume Next
WshShell.Run cmd, 0, False
If Err.Number <> 0 Then
    ' Fallback to visible launcher if hidden execution failed
    WshShell.Run "cmd /c python """ & strCurDir & "\installer_gui.py""", 1, False
End If
On Error GoTo 0

Set fso = Nothing
Set WshShell = Nothing
