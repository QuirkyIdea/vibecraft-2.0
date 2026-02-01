@echo off
REM ============================================
REM Fix Draft Refinement - COMPLETE SOLUTION
REM ============================================

echo.
echo ========================================
echo  FIXING DRAFT REFINEMENT
echo ========================================
echo.
echo Issue Found: Pydantic validation error in CrashLog schema
echo Fix Applied: Updated FailedStage and ErrorType enums
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/5] Stopping backend container...
docker-compose stop backend

echo.
echo [2/5] Removing old backend container...
docker-compose rm -f backend

echo.
echo [3/5] Rebuilding backend with fixes...
docker-compose build --no-cache backend

echo.
echo [4/5] Starting backend...
docker-compose up -d backend

echo.
echo [5/5] Waiting for backend to be healthy...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo  VERIFYING FIX
echo ========================================
echo.

REM Test backend health
echo Testing backend health...
curl -s http://localhost:8000/health
echo.

echo.
echo Testing draft-conference route...
curl -s http://localhost:8000/api/draft-conference/status
echo.

echo.
echo ========================================
echo  FIX COMPLETE!
echo ========================================
echo.
echo Services Status:
docker-compose ps
echo.
echo ========================================
echo  NOW TEST IN BROWSER
echo ========================================
echo.
echo 1. Open http://localhost:3000
echo 2. Go to Draft Refinement
echo 3. Try pasting text and clicking "Refine Draft"
echo 4. Try uploading a PDF and refining
echo.
echo If you see errors, check logs:
echo   docker-compose logs -f backend
echo.

pause
