@echo off
cd /d "%~dp0"
echo Starting NPD Processor GUI...
start "" "http://localhost:5001"

set SYS_PYTHON=
for /f "delims=" %%i in ('where python 2^>nul') do (
    echo %%i | findstr /i /v "WindowsApps" >nul
    if not errorlevel 1 (
        if not defined SYS_PYTHON set "SYS_PYTHON=%%i"
    )
)

if defined SYS_PYTHON (
    echo System Python found at: %SYS_PYTHON%
    "%SYS_PYTHON%" backend\app.py
) else if exist "C:\Python\python.exe" (
    echo System Python not found. Found custom Python environment at C:\Python.
    C:\Python\python.exe backend\app.py
) else if exist ".\python\python.exe" (
    echo System Python not found. Found portable Python environment.
    .\python\python.exe backend\app.py
) else (
    echo Python not found! Please install Python or place it in C:\Python.
)
pause
