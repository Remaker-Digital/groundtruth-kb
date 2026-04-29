' Smart-poller daemon launcher (VBS) — invokes the .ps1 wrapper truly hidden.
'
' Per bridge/gtkb-bridge-poller-notify-activation-2026-04-29-006.md
' (reverification of activation), Windows 11 + Windows Terminal as default
' console host does NOT reliably honor `powershell.exe -WindowStyle Hidden`
' when launched directly by Task Scheduler — Terminal renders the hosted
' PowerShell window visibly anyway. The standard Windows fix is a VBS
' launcher invoked via wscript.exe (which has no console of its own) using
' `WshShell.Run intWindowStyle=0` to spawn the PowerShell hidden.
'
' This script does NO logic of its own beyond invoking the .ps1 wrapper.
' All path resolution, runner detection, and -ValidateOnly mode remain in
' run_smart_bridge_poller.ps1 (single source of truth for those).

Option Explicit

Dim fso, scriptDir, projectRoot, runnerPath, shell, command, exitCode

Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
projectRoot = fso.GetParentFolderName(scriptDir)

' Phase-1 path. Phase 2 rewrites this single line per the path-rebase
' checklist; same line MUST be updated in run_smart_bridge_poller.ps1
' which the doctor uses for its -ValidateOnly check.
runnerPath = projectRoot & "\groundtruth-kb\scripts\bridge_poller_runner.py"

If Not fso.FileExists(runnerPath) Then
  WScript.Echo "Smart-poller runner not found at " & runnerPath
  WScript.Quit 1
End If

Set shell = CreateObject("WScript.Shell")

' Invoke pythonw.exe (windowless Python variant) directly, skipping the .ps1
' wrapper from the daemon path. Per smart-poller-notify-activation -006 follow-up
' diagnosis: the wscript.exe -> powershell.exe -> pythonw.exe chain via .ps1
' had the powershell intermediary exit prematurely under WshShell.Run with
' intWindowStyle=0 + bWaitOnReturn=True, leaving pythonw orphaned and Task
' Scheduler tracking the wscript exit as task completion. Direct invocation
' of pythonw.exe from VBS produces a single-process chain that Task Scheduler
' tracks correctly through the poller's lifetime.
'
' WshShell.Run arguments:
'   intWindowStyle = 0 (hide the window — pythonw.exe has no console anyway)
'   bWaitOnReturn  = True (wait for pythonw.exe to exit so Task Scheduler
'                          tracks the task as Running while pythonw runs)
command = "pythonw.exe """ & runnerPath & """ --interval 15 --quiet"
exitCode = shell.Run(command, 0, True)
WScript.Quit exitCode
