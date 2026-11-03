@echo off
title Country Maternal-Child Health Profile Segmentation Launcher
color 0A

echo ======================================================================
echo    COUNTRY MATERNAL-CHILD HEALTH PROFILE SEGMENTATION LAUNCHER
echo ======================================================================
echo.
echo [1] Open Interactive Web Dashboard (Instant browser launch!)
echo [2] Run Full Machine Learning Pipeline (Python CLI + Visualizations)
echo [3] Launch Jupyter Notebook Environment
echo [4] Exit
echo.
set /p choice="Select an option (1-4): "

if "%choice%"=="1" (
    echo.
    echo Launching Interactive Dashboard in your default web browser...
    start dashboard\index.html
    pause
    exit
)

if "%choice%"=="2" (
    echo.
    echo Running end-to-end Python pipeline...
    .venv\Scripts\python.exe run_pipeline.py
    pause
    exit
)

if "%choice%"=="3" (
    echo.
    echo Launching Jupyter Notebook...
    .venv\Scripts\jupyter.exe notebook notebooks\Country_MCH_Segmentation.ipynb
    pause
    exit
)

if "%choice%"=="4" (
    exit
)

echo Invalid choice.
pause
