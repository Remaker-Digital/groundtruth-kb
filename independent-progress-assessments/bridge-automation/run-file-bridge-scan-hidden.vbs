Option Explicit

Dim fso, shell, scriptDir, workspace, scanPath, command, exitCode

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
workspace = fso.GetParentFolderName(fso.GetParentFolderName(scriptDir))
scanPath = fso.BuildPath(scriptDir, "codex-file-bridge-scan.ps1")

shell.CurrentDirectory = workspace
command = "powershell.exe -NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File " & QuoteArg(scanPath)

exitCode = shell.Run(command, 0, True)
WScript.Quit exitCode

Function QuoteArg(value)
    QuoteArg = Chr(34) & Replace(value, Chr(34), Chr(34) & Chr(34)) & Chr(34)
End Function
