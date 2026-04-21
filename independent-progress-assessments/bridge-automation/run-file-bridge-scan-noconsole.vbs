Option Explicit

Dim fso, shell, scriptDir, workspace, wrapperPath, command, exitCode

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
workspace = fso.GetParentFolderName(fso.GetParentFolderName(scriptDir))
wrapperPath = fso.BuildPath(scriptDir, "run-bridge-scan-noconsole.ps1")

shell.CurrentDirectory = workspace
command = "powershell.exe -NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File " & QuoteArg(wrapperPath) & " -Scanner Codex"

exitCode = shell.Run(command, 0, True)
WScript.Quit exitCode

Function QuoteArg(value)
    QuoteArg = Chr(34) & Replace(value, Chr(34), Chr(34) & Chr(34)) & Chr(34)
End Function
