@echo off
cd /d "%~dp0"
echo Starting NPD Processor GUI...
start "" "http://localhost:5001"

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    echo System Python found.
    python backend\app.py
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
