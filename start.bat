@echo off
echo 🤖 Starting Intrabot-AI (Windows)...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Setting up virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo ⬇️  Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo 📝 Please edit .env file with your actual API keys before running the server.
    echo    Especially set your GEMINI_API_KEY
)

REM Initialize database if needed
if not exist "offline-org-chatbot\.chromadb" (
    echo 🗄️  Initializing database...
    python init_db.py
) else (
    echo ✅ Database already exists
)

REM Start the FastAPI server
echo 🚀 Starting FastAPI server...
echo    Server will be available at: http://127.0.0.1:8000
echo    API documentation at: http://127.0.0.1:8000/docs
echo    Frontend interface at: http://127.0.0.1:8000/static/
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn api:app --host 127.0.0.1 --port 8000 --reload
