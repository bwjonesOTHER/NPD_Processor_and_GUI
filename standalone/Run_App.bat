@echo off
cd /d "%~dp0"
echo Starting NPD Processor GUI...
start "" "http://localhost:5001"
if exist "C:\Python\python.exe" (
    echo Found custom Python environment at C:\Python.
    C:\Python\python.exe app.py
) else if exist ".\python\python.exe" (
    echo Found portable Python environment.
    .\python\python.exe app.py
) else (
    echo Portable Python not found. Falling back to system Python...
    python app.py
)
pause
