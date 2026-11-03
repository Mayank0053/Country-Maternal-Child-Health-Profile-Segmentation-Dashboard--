@echo off
title Push to GitHub - Country Maternal-Child Health Segmentation
color 0A

echo ======================================================================
echo       PUSH PROJECT TO GITHUB (Mayank0053)
echo ======================================================================
echo.
echo Target Repository: https://github.com/Mayank0053/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--
echo Branch: main
echo.

echo [1] Adding all project files to Git...
git add .

echo [2] Committing changes...
git commit -m "feat: complete Country Maternal-Child Health Profile Segmentation project"

echo [3] Pushing to GitHub...
echo A browser window may open to authenticate with your GitHub account (Mayank0053).
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo  SUCCESS! Project pushed to GitHub successfully!
    echo ======================================================================
) else (
    echo.
    echo If authentication failed, you can push using a GitHub Personal Access Token:
    echo 1. Go to https://github.com/settings/tokens
    echo 2. Generate a token with 'repo' permissions
    echo 3. Run: git remote set-url origin https://YOUR_TOKEN@github.com/Mayank0053/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--.git
    echo 4. Run: git push -u origin main
)

echo.
pause
