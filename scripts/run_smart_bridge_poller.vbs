' Smart-poller daemon launcher (VBS) — primary daemon path for Task Scheduler.
'
' Per bridge/gtkb-bridge-poller-notify-activation-2026-04-29-006.md follow-up
' diagnosis: Windows 11 + Windows Terminal as default console host does NOT
' reliably honor `powershell.exe -WindowStyle Hidden` when launched directly
' by Task Scheduler — Terminal renders the hosted PowerShell window visibly
' anyway. The standard Windows fix is a VBS launcher invoked via wscript.exe
' (which has no console of its own) calling pythonw.exe directly.
'
' Operating modes (selected by command-line arguments):
'   (no args)           → daemon mode: launch pythonw.exe with the runner.
'                         Uses WshShell.Run intWindowStyle=0 bWaitOnReturn=True
'                         so Task Scheduler tracks the task as Running while
'                         pythonw runs. Default daemon path.
'   /Validate           → validate mode: resolve runnerPath, confirm it exists,
'                         echo "OK runner=<path>", quit 0. Used by the
'                         gt-project-doctor smart-poller check to verify the
'                         actual daemon launcher's effective path (not just
'                         the .ps1 helper). Per -008 Finding 1.
'   /Interval:N         → daemon mode with custom polling interval (default 15).
'                         Per -008 Finding 2: install_smart_poller_task.ps1
'                         passes -IntervalSeconds N here so the parameter is
'                         no longer ignored.

Option Explicit

Dim fso, scriptDir, projectRoot, runnerPath, shell, command, exitCode
Dim args, i, validateOnly, intervalSeconds, argLower, argValue

Set args = WScript.Arguments
validateOnly = False
intervalSeconds = 15

For i = 0 To args.Count - 1
  argLower = LCase(args(i))
  If argLower = "/validate" Then
    validateOnly = True
  ElseIf Left(argLower, 10) = "/interval:" Then
    argValue = Mid(args(i), 11)
    If IsNumeric(argValue) Then
      intervalSeconds = CInt(argValue)
    End If
  End If
Next

Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
projectRoot = fso.GetParentFolderName(scriptDir)

' Phase-1 path. Phase 2 rewrites this single line per the path-rebase
' checklist; same line MUST be updated in run_smart_bridge_poller.ps1
' which is retained for interactive use only.
runnerPath = projectRoot & "\groundtruth-kb\scripts\bridge_poller_runner.py"

If Not fso.FileExists(runnerPath) Then
  WScript.Echo "Smart-poller runner not found at " & runnerPath
  WScript.Quit 1
End If

If validateOnly Then
  ' Validate mode: doctor uses this to verify the EFFECTIVE runner path of
  ' the daemon launcher (per -008 Finding 1). Echoes the resolved path so
  ' the doctor can match it against expectation.
  WScript.Echo "OK runner=" & runnerPath
  WScript.Quit 0
End If

Set shell = CreateObject("WScript.Shell")

' WshShell.Run arguments:
'   intWindowStyle = 0 (hide the window — pythonw.exe has no console anyway)
'   bWaitOnReturn  = True (wait for pythonw.exe to exit so Task Scheduler
'                          tracks the task as Running while pythonw runs)
command = "pythonw.exe """ & runnerPath & """ --interval " & intervalSeconds & " --quiet"
exitCode = shell.Run(command, 0, True)
WScript.Quit exitCode
