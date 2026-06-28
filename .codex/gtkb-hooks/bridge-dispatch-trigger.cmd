@echo off
setlocal EnableExtensions

set "HOOK_DIR=%~dp0"
for %%I in ("%HOOK_DIR%..\..") do set "PROJECT_ROOT=%%~fI"
set "PYTHONW=%PROJECT_ROOT%\groundtruth-kb\.venv\Scripts\pythonw.exe"
set "TRIGGER=%PROJECT_ROOT%\scripts\cross_harness_bridge_trigger.py"
set "IS_STOP_HOOK="

for %%A in (%*) do (
  if /I "%%~A"=="--stop-hook" set "IS_STOP_HOOK=1"
)

if not exist "%PYTHONW%" (
  set "PYTHONW="
  for /f "usebackq delims=" %%P in (`where pythonw.exe 2^>nul`) do (
    if not defined PYTHONW set "PYTHONW=%%P"
  )
)

if not exist "%PYTHONW%" (
  if defined IS_STOP_HOOK echo {}
  exit /b 0
)

"%PYTHONW%" "%TRIGGER%" %*

exit /b 0
