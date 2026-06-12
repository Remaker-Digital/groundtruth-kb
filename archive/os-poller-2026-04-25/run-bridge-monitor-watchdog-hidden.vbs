Option Explicit

Dim fso, shell, scriptDir, workspace, watchdogPath, command, exitCode

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
workspace = fso.GetParentFolderName(fso.GetParentFolderName(scriptDir))
watchdogPath = fso.BuildPath(scriptDir, "bridge-monitor-watchdog.ps1")

shell.CurrentDirectory = workspace
command = "powershell.exe -NoLogo -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File " & QuoteArg(watchdogPath)

exitCode = shell.Run(command, 0, True)
WScript.Quit exitCode

Function QuoteArg(value)
    QuoteArg = Chr(34) & Replace(value, Chr(34), Chr(34) & Chr(34)) & Chr(34)
End Function
