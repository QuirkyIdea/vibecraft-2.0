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
    echo Creating .env file...
    (
        echo # Inventix AI - Environment Configuration
        echo # =======================================
        echo.
        echo # REQUIRED: Google Gemini API Key
        echo # Get your key from: https://aistudio.google.com/app/apikey
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # Optional configurations
        echo GEMINI_MODEL=gemini-1.5-flash
        echo DEBUG=false
        echo SECRET_KEY=change-this-to-a-secure-random-string
        echo.
        echo # Backend Configuration
        echo BACKEND_HOST=0.0.0.0
        echo BACKEND_PORT=8000
        echo.
        echo # JWT Configuration
        echo JWT_ALGORITHM=HS256
        echo JWT_EXPIRE_MINUTES=10080
        echo.
        echo # Google OAuth ^(Optional^)
        echo GOOGLE_CLIENT_ID=
        echo GOOGLE_CLIENT_SECRET=
        echo GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback
        echo.
        echo # Frontend Configuration
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
        echo NEXT_PUBLIC_APP_NAME=Inventix AI
    ) > .env
    echo [CREATED] .env file created
    echo.
    echo ========================================
    echo  IMPORTANT: Add your GEMINI_API_KEY!
    echo ========================================
    echo.
    echo Opening .env file for editing...
    echo.
    echo Please replace "your_gemini_api_key_here" with your actual API key
    echo Get your key from: https://aistudio.google.com/app/apikey
    echo.
    where code >nul 2>&1
    if not errorlevel 1 (
        echo Opening in VS Code...
        code .env
    ) else (
        echo Opening in Notepad...
        notepad .env
    )
    echo.
    echo After saving your API key, press any key to continue...
    pause >nul
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
