@echo off
REM Luno Trading Bot - Windows Setup
REM Easy setup for Windows users

echo.
echo ========================================
echo   LUNO TRADING BOT - WINDOWS SETUP
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
python --version

echo.
echo Starting setup wizard...
echo.

REM Run the setup wizard
python setup.py

echo.
echo Setup completed!
echo.
echo To start the bot, run:
echo   python launcher.py
echo.
pause
