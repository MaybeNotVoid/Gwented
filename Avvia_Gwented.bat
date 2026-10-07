@echo off
title Gwented - The Witcher 3 Console Assistant
cd /d "%~dp0"
echo ========================================================
echo   GWENTED - The Witcher 3 Console Assistant
echo   Fix Tastiera Italiana ^& Auto-Spawn
echo ========================================================
echo.
python run_app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Si e' verificato un errore durante l'esecuzione.
    pause
)
