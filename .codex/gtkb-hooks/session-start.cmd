@echo off
set "GTKB_HARNESS_NAME=codex"
for /f "usebackq delims=" %%I in (`python "E:\GT-KB\scripts\harness_identity.py" --project-root "E:\GT-KB" resolve --harness-name codex`) do set "GTKB_HARNESS_ID=%%I"
python "E:\GT-KB\scripts\session_self_initialization.py" --project-root "E:\GT-KB" --emit-startup-service-payload --fast-hook --harness-name codex --harness-id %GTKB_HARNESS_ID%
