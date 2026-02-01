@echo off
REM Inventix AI - Docker Deployment Script for Windows
REM ===================================================

echo.
echo ========================================
echo  Inventix AI - Docker Deployment
echo ========================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo.
    if exist .env.example (
        echo Creating .env from .env.example...
        copy .env.example .env >nul
        echo [CREATED] .env file created
        echo.
        echo IMPORTANT: Please edit .env file and add your GEMINI_API_KEY
        echo.
        notepad .env
        echo.
        echo Press any key after saving the .env file...
        pause >nul
    ) else (
        echo [ERROR] .env.example file not found!
        echo Please create a .env file with your configuration.
        pause
        exit /b 1
    )
)

echo [OK] .env file found
echo.

REM Build and start services
echo ========================================
echo  Building and Starting Services...
echo ========================================
echo.

docker-compose up -d --build

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start services!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Deployment Successful!
echo ========================================
echo.
echo Services are now running:
echo.
echo  Frontend:  http://localhost:3000
echo  Backend:   http://localhost:8000
echo  API Docs:  http://localhost:8000/docs
echo.
echo ========================================
echo  Useful Commands:
echo ========================================
echo.
echo  View logs:     docker-compose logs -f
echo  Stop services: docker-compose down
echo  Check status:  docker-compose ps
echo.
echo ========================================
echo.

REM Wait a moment for services to start
timeout /t 5 /nobreak >nul

REM Check service status
echo Checking service status...
echo.
docker-compose ps

echo.
echo Press any key to open frontend in browser...
pause >nul

REM Open browser
start http://localhost:3000

echo.
echo Done! Services are running in the background.
echo.
pause
