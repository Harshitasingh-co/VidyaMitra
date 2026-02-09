@echo off
REM VidyaMitra Backend Startup Script for Windows

echo ╔══════════════════════════════════════════════════════════╗
echo ║         VidyaMitra Backend - Starting...                ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo ❗ IMPORTANT: Edit .env and add your API keys before continuing!
    echo    Required: OPENAI_API_KEY
    echo.
    pause
)

REM Install/update dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Start server
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║         Starting VidyaMitra API Server                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo API Server: http://localhost:8000
echo API Docs:   http://localhost:8000/docs
echo Health:     http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
