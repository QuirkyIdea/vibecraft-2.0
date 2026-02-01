@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo.
echo =================================================
echo Safe deploy.bat - Inventix AI Deployment
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

REM If no key found, prompt the user (interactive)
if "%GEMINI_API_KEY%"=="" (
    echo =============================================================
    echo GEMINI API KEY required to continue.
    echo Option A (recommended): Open your browser to https://console.google.com (or your key provider) and copy your key.
    echo Option B: Paste your existing key when prompted below.
    echo NOTE: This key will be written to a local .env file only and NOT committed (repo .gitignore should list .env).
    echo =============================================================
    echo.
    set /p "USER_KEY=Please paste your GEMINI_API_KEY and press Enter: "
    if "%USER_KEY%"=="" (
        echo ERROR: No key provided. .env will not be created. Re-run deploy.bat when you have the key.
        pause
        exit /b 1
    )
    set "GEMINI_API_KEY=%USER_KEY%"
    echo.
    echo Creating .env with provided key...
    > .env (
        echo # Inventix AI - Environment Configuration
        echo GEMINI_API_KEY=%GEMINI_API_KEY%
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
    )
    echo .env created successfully (ASCII/UTF-8 compatible).
    echo DRY-RUN OK: GEMINI_API_KEY set in .env.
    echo First line of .env:
    set "first_line_shown="
    for /f "delims=" %%L in (.env) do (
        if not defined first_line_shown (
            echo    %%L
            set "first_line_shown=1"
        )
    )
    pause
    exit /b 0
)

REM If key exists in .env, confirm not empty
if "%GEMINI_API_KEY%"=="" (
    echo ERROR: GEMINI_API_KEY in .env is empty.
    echo Please open .env and set GEMINI_API_KEY, then re-run deploy.bat.
    pause
    exit /b 1
)

echo.
echo =================================================
echo GEMINI_API_KEY detected in .env!
echo =================================================
echo.
echo Starting Docker services...
echo.
docker-compose up -d --build
if errorlevel 1 (
    echo.
    echo ERROR: Docker failed to start. Check Docker Desktop is running.
    pause
    exit /b 1
)
echo.
echo =================================================
echo Deployment successful!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo =================================================
echo.
pause
