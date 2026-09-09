@echo off
title Test LOA Bot Files
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or is not available in PATH.
    pause
    exit /b 1
)

echo Checking bot.py for Python syntax errors...
py -m py_compile bot.py

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: bot.py passed the syntax test.
) else (
    echo.
    echo ERROR: bot.py has a syntax problem.
)
echo.
pause
