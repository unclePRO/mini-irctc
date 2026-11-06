@echo off
setlocal
title Railway Reservation System (IRCTC Mini)
echo ========================================================
echo Starting Railway Reservation System
echo ========================================================

:: Check for Python 3.13 in Local Programs
set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe"

if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo Using Python: %PYTHON_EXE%
echo Checking database setup...
"%PYTHON_EXE%" db.py init

echo Starting web server on http://127.0.0.1:5000 ...
echo Press Ctrl+C to stop the server.
echo.
"%PYTHON_EXE%" app.py

pause
