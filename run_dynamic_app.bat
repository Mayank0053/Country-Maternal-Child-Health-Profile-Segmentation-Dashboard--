@echo off
title Country Maternal-Child Health Dynamic Full-Stack Launcher
color 0B

echo ======================================================================
echo    COUNTRY MATERNAL-CHILD HEALTH PROFILE SEGMENTATION
echo            DYNAMIC FULL-STACK APPLICATION LAUNCHER
echo ======================================================================
echo.
echo Problem Statement: Bill & Melinda Gates Foundation
echo Individual Contributor: Mayank (Registration Number: 12404505)
echo.
echo [1] Start Dynamic FastAPI Backend + Web Dashboard (http://127.0.0.1:8000)
echo [2] Open Interactive Swagger API Documentation (http://127.0.0.1:8000/docs)
echo [3] Run Machine Learning Python Pipeline CLI
echo [4] Launch Jupyter Notebook Environment
echo [5] Exit
echo.
set /p choice="Select an option (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting FastAPI Dynamic Server on http://127.0.0.1:8000 ...
    echo Opening Dashboard in your default browser...
    start http://127.0.0.1:8000
    .venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
    pause
    exit
)

if "%choice%"=="2" (
    echo.
    echo Opening Swagger API documentation...
    start http://127.0.0.1:8000/docs
    .venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
    pause
    exit
)

if "%choice%"=="3" (
    echo.
    echo Executing end-to-end Python ML Pipeline...
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
