@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo.
echo =================================================
echo    Inventix AI - Docker Deployment Script
echo =================================================
echo.

REM Check if .env exists and read GEMINI_API_KEY from it
set "GEMINI_API_KEY="
if exist .env (
    echo Checking existing .env file...
    for /f "tokens=1* delims==" %%A in ('findstr /B "GEMINI_API_KEY=" .env 2^>nul') do (
        set "GEMINI_API_KEY=%%B"
    )
)

REM If no key found, prompt the user
if "%GEMINI_API_KEY%"=="" (
    echo.
    echo GEMINI API KEY required to continue.
    echo Get your key from: https://aistudio.google.com/app/apikey
    echo.
    set /p "USER_KEY=Paste your GEMINI_API_KEY here: "
    if "!USER_KEY!"=="" (
        echo.
        echo ERROR: No key provided.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Creating .env file...
    (
        echo # Inventix AI - Environment Configuration
        echo GEMINI_API_KEY=!USER_KEY!
        echo GEMINI_MODEL=gemini-1.5-flash
        echo.
        echo BACKEND_HOST=0.0.0.0
        echo BACKEND_PORT=8000
        echo DEBUG=false
        echo.
        echo SECRET_KEY=change-this-to-a-secure-random-string
        echo JWT_ALGORITHM=HS256
        echo JWT_EXPIRATION_MINUTES=120
        echo.
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
        echo NEXT_PUBLIC_APP_NAME=Inventix AI
    ) > .env
    echo.
    echo .env created successfully!
    echo Now run deploy.bat again to start Docker.
    echo.
    pause
    exit /b 0
)

REM If key is empty
if "%GEMINI_API_KEY%"=="" (
    echo.
    echo ERROR: GEMINI_API_KEY in .env is empty.
    echo Please edit .env and add your API key.
    echo.
    pause
    exit /b 1
)

REM Start Docker
echo.
echo =================================================
echo Starting Docker services...
echo =================================================
echo.
docker-compose up -d --build
if errorlevel 1 (
    echo.
    echo ERROR: Docker failed to start.
    echo Make sure Docker Desktop is running.
    echo.
    pause
    exit /b 1
)

echo.
echo =================================================
echo Deployment successful!
echo =================================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo =================================================
echo.
pause
