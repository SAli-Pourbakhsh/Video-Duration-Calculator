@echo off
TITLE Video Duration Calculator - Launcher
COLOR 0B
CLS

ECHO ========================================================
ECHO       VIDEO DURATION CALCULATOR LAUNCHER
ECHO ========================================================
ECHO.

REM --- STEP 1: Check Python ---
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO NoPython

REM --- STEP 2: Check Dependencies ---
ECHO [*] Checking dependencies...
python -c "import moviepy, colorama" >nul 2>&1
IF %ERRORLEVEL% EQU 0 GOTO RunApp

REM --- STEP 3: Install Dependencies (If missing) ---
ECHO [*] Installing required libraries (moviepy, colorama)...
ECHO     This may take a minute...
python -m pip install --upgrade moviepy colorama

IF %ERRORLEVEL% NEQ 0 GOTO InstallFail
ECHO [*] Installation successful.
GOTO RunApp

REM --- ERROR HANDLERS ---

:NoPython
COLOR 0C
ECHO.
ECHO [ERROR] Python is not installed or not found in PATH.
ECHO Please install Python from https://www.python.org/
ECHO.
PAUSE
EXIT

:InstallFail
COLOR 0C
ECHO.
ECHO [ERROR] Failed to install libraries.
ECHO Please check your internet connection.
PAUSE
EXIT

REM --- MAIN APPLICATION ---

:RunApp
ECHO.
ECHO [*] Launching application...
ECHO.
python video_calculator.py

REM Keep window open if python crashes
PAUSE