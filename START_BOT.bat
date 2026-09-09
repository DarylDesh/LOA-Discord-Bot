@echo off
title Leave of Absence Discord Bot
cd /d "%~dp0"

echo ================================================
echo Leave of Absence Discord Bot
echo ================================================
echo.

where py >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python was not found.
    echo.
    echo Please install Python first, then run this file again.
    echo The setup guide explains exactly how to do that.
    echo.
    pause
    exit /b 1
)

if not exist ".env" (
    echo ERROR: The .env settings file does not exist.
    echo.
    echo Make a copy of .env.example and rename the copy to .env
    echo Then fill in your bot token and Discord IDs.
    echo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo First run detected.
    echo Creating the private Python environment...
    py -m venv .venv
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Could not create the Python environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

echo Checking required bot software...
python -m pip install --disable-pip-version-check -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Required Python packages could not be installed.
    echo Make sure your computer is connected to the internet.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Starting the LOA bot...
echo Do NOT close this window while you want the bot online.
echo Press CTRL+C if you want to stop the bot.
echo ================================================
echo.
python bot.py

echo.
echo The bot has stopped.
pause
