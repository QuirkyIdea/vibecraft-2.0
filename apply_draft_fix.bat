@echo off
REM ============================================
REM Apply Draft Refinement Fix
REM ============================================

echo.
echo ========================================
echo  APPLYING DRAFT REFINEMENT FIX
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/4] Stopping current services...
docker-compose down

echo.
echo [2/4] Rebuilding backend with fix...
docker-compose build backend

echo.
echo [3/4] Starting services...
docker-compose up -d

echo.
echo [4/4] Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo  FIX APPLIED SUCCESSFULLY!
echo ========================================
echo.
echo Services Status:
docker-compose ps

echo.
echo ========================================
echo  TESTING INSTRUCTIONS
echo ========================================
echo.
echo 1. Open http://localhost:3000 in your browser
echo 2. Navigate to Draft Refinement panel
echo 3. Try pasting text and clicking "Refine Draft"
echo 4. Try uploading a PDF/DOCX file and refining
echo.
echo Check logs if issues persist:
echo   docker-compose logs -f backend
echo.
echo Full documentation: DRAFT_REFINEMENT_FIX.md
echo.

pause
