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
        echo Creating .env from .env.example with UTF-8 encoding...
        powershell -Command "$content = Get-Content .env.example -Raw; [System.IO.File]::WriteAllText('.env', $content, [System.Text.UTF8Encoding]::new($false))"
        echo [CREATED] .env file created ^(UTF-8 without BOM^)
        echo.
        echo ========================================
        echo  IMPORTANT: Edit .env with UTF-8 Editor
        echo ========================================
        echo.
        echo Please add your GEMINI_API_KEY to the .env file
        echo.
        echo RECOMMENDED EDITORS:
        echo   - VS Code
        echo   - Notepad++ 
        echo   - Windows 11 Notepad ^(auto UTF-8^)
        echo.
        echo WARNING: Old Notepad may save as UTF-16!
        echo          This will cause Docker errors.
        echo.
        where code >nul 2>&1
        if not errorlevel 1 (
            echo Opening in VS Code...
            code .env
        ) else (
            echo Opening in Notepad...
            echo ^(If deployment fails, re-save .env as UTF-8^)
            notepad .env
        )
        echo.
        echo After saving, press any key to continue...
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
