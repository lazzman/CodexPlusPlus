@echo off
setlocal
cd /d "%~dp0"

set "VENV_DIR=%~dp0.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo Creating Python virtual environment at "%VENV_DIR%"...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 goto error
)

echo Installing Codex++ into venv...
"%VENV_PY%" -m pip install -e .
if errorlevel 1 goto error

echo Starting Codex++ graphical console...
"%VENV_PY%" "%~dp0codex_plus_gui.py"
if errorlevel 1 goto error

goto end

:error
echo.
echo Operation failed. Please check the error output above.
pause
exit /b 1

:end
endlocal
