@echo off
setlocal

for /f "usebackq delims=" %%R in (`git rev-parse --show-toplevel 2^>nul`) do set "REPO_ROOT=%%R"
if "%REPO_ROOT%"=="" exit /b 1

if exist "%REPO_ROOT%\groundtruth-kb\.venv\Scripts\python.exe" (
  set "PYTHON_BIN=%REPO_ROOT%\groundtruth-kb\.venv\Scripts\python.exe"
) else if not "%PYTHON%"=="" (
  set "PYTHON_BIN=%PYTHON%"
) else (
  set "PYTHON_BIN=python"
)

set "PYTHONPATH=%REPO_ROOT%\groundtruth-kb\src;%PYTHONPATH%"
pushd "%REPO_ROOT%" >nul
"%PYTHON_BIN%" -m groundtruth_kb.cli push preflight
set "STATUS=%ERRORLEVEL%"
popd >nul
exit /b %STATUS%
