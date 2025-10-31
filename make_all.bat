@echo off
:: =========================================================
:: make_all.bat  -  Windows automation for CPSC 4140 project
:: =========================================================

set PYTHON=python
set VENV=venv
set APP_DIR=app
set FRONT_DIR=frontend
set DATA_DIR=data
set DB_FILE=%APP_DIR%\database.db

:: ---------------------------------------------------------
:: Display help
:: ---------------------------------------------------------
if "%1"=="" (
    echo Usage:
    echo   make_all env         - Create venv and install dependencies
    echo   make_all run         - Run both backend and frontend
    echo   make_all backend     - Run Flask backend only
    echo   make_all frontend    - Run Tkinter frontend only
    echo   make_all analyze     - Run Fitts' Law results analysis
    echo   make_all clean       - Remove temporary and data files
    echo   make_all reset-db    - Delete and recreate the database
    exit /b 0
)

:: ---------------------------------------------------------
:: Environment setup
:: ---------------------------------------------------------
if "%1"=="env" (
    echo Creating virtual environment...
    %PYTHON% -m venv %VENV%
    call %VENV%\Scripts\activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    echo Environment ready.
    exit /b 0
)

:: ---------------------------------------------------------
:: Run full system (backend + frontend)
:: ---------------------------------------------------------
if "%1"=="run" (
    echo Starting backend and frontend...
    %PYTHON% run_all.py
    exit /b 0
)

:: ---------------------------------------------------------
:: Run only Flask backend
:: ---------------------------------------------------------
if "%1"=="backend" (
    echo Starting Flask backend...
    %PYTHON% run_server.py
    exit /b 0
)

:: ---------------------------------------------------------
:: Run only Tkinter frontend
:: ---------------------------------------------------------
if "%1"=="frontend" (
    echo Starting Tkinter frontend...
    %PYTHON% -m %FRONT_DIR%.main
    exit /b 0
)

:: ---------------------------------------------------------
:: Run analysis script
:: ---------------------------------------------------------
if "%1"=="analyze" (
    echo Running Fitts' Law analysis...
    %PYTHON% analyze_results.py
    exit /b 0
)

:: ---------------------------------------------------------
:: Clean build and data artifacts
:: ---------------------------------------------------------
if "%1"=="clean" (
    echo Cleaning temporary files...
    rmdir /S /Q __pycache__ 2>nul
    for /r %%f in (*.pyc *.pyo) do del "%%f" 2>nul
    del "%DATA_DIR%\*.csv" 2>nul
    del "%DATA_DIR%\*.png" 2>nul
    echo Clean complete.
    exit /b 0
)

:: ---------------------------------------------------------
:: Reset the database
:: ---------------------------------------------------------
if "%1"=="reset-db" (
    echo Resetting database...
    del "%DB_FILE%" 2>nul
    %PYTHON% -c "from app.routes import app; from app.models import db; app.app_context().push(); db.create_all(); print('Database recreated.')"
    exit /b 0
)

:: ---------------------------------------------------------
:: Unknown command
:: ---------------------------------------------------------
echo Unknown command: %1
echo Run without arguments for help.
exit /b 1
