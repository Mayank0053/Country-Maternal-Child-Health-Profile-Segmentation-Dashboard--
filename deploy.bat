@echo off
title Deploy Country Maternal-Child Health Profile Segmentation Dashboard
color 0B

echo ======================================================================
echo    DEPLOY COUNTRY MATERNAL-CHILD HEALTH SEGMENTATION DASHBOARD
echo ======================================================================
echo.
echo Your project is already prepared and pushed for deployment:
echo Repository: https://github.com/Mayank0053/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--
echo.
echo [1] Enable GitHub Pages (Recommended - 100% Free, Official GitHub URL)
echo [2] Deploy to Vercel (Instant live URL via Vercel CLI)
echo [3] Deploy to Netlify (Instant live URL via Netlify CLI)
echo [4] Start Local Web Server (http://localhost:8080)
echo [5] Exit
echo.
set /p choice="Select an option (1-5): "

if "%choice%"=="1" (
    echo.
    echo Opening GitHub Pages Settings in your browser...
    start https://github.com/Mayank0053/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--/settings/pages
    echo.
    echo INSTRUCTIONS TO ACTIVATE GITHUB PAGES:
    echo 1. Under "Build and deployment", set Source to "Deploy from a branch"
    echo 2. Under Branch, select "gh-pages" (or "main") and folder "/ (root)"
    echo 3. Click "Save"
    echo.
    echo In about 60 seconds, your site will be live at:
    echo https://mayank0053.github.io/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--/
    echo.
    pause
    exit
)

if "%choice%"=="2" (
    echo.
    echo Deploying to Vercel...
    npx -y vercel --prod
    pause
    exit
)

if "%choice%"=="3" (
    echo.
    echo Deploying to Netlify...
    npx -y netlify-cli deploy --prod --dir=.
    pause
    exit
)

if "%choice%"=="4" (
    echo.
    echo Starting local web server at http://localhost:8080 ...
    start http://localhost:8080
    .venv\Scripts\python.exe -m http.server 8080
    pause
    exit
)

if "%choice%"=="5" (
    exit
)

echo Invalid choice.
pause
