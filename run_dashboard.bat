@echo off
title Country Maternal-Child Health Profile Segmentation Launcher
color 0A

echo ======================================================================
echo    COUNTRY MATERNAL-CHILD HEALTH PROFILE SEGMENTATION LAUNCHER
echo ======================================================================
echo Individual Project by: Mayank (Registration Number: 12404505)
echo Target Foundation: Bill & Melinda Gates Foundation
echo.
echo [1] Launch Dynamic Full-Stack App (FastAPI Backend + Light Dashboard on :8000)
echo [2] Open Standalone Client Dashboard (Instant direct browser launch)
echo [3] Run Master Python ML Pipeline CLI
echo [4] Launch Jupyter Notebook Environment
echo [5] Exit
echo.
set /p choice="Select an option (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting FastAPI Dynamic Server on http://127.0.0.1:8000 ...
    start http://127.0.0.1:8000
    .venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
    pause
    exit
)

if "%choice%"=="2" (
    echo.
    echo Launching Standalone Dashboard in your default web browser...
    start dashboard\index.html
    pause
    exit
)

if "%choice%"=="3" (
    echo.
    echo Running end-to-end Python pipeline...
    .venv\Scripts\python.exe run_pipeline.py
    pause
    exit
)

if "%choice%"=="4" (
    echo.
    echo Launching Jupyter Notebook...
    .venv\Scripts\jupyter.exe notebook notebooks\Country_MCH_Segmentation.ipynb
    pause
    exit
)

if "%choice%"=="5" (
    exit
)

echo Invalid choice.
pause
