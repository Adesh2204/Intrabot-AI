# Intrabot-AI Development Setup

## Prerequisites
- Python 3.8+
- pip

## Quick Start

### Method 1: Using the startup script (Recommended)
```bash
./start.sh
```

### Method 2: Manual setup
1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your API keys
```

4. Start the server:
```bash
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

### Method 3: Using npm-style commands
```bash
npm run setup    # Initial setup (same as ./start.sh)
npm start        # Start development server
npm run dev      # Start with debug logging
npm run production  # Start production server
```

## Access Points
- **Frontend Interface**: http://127.0.0.1:8000/static/
- **API Documentation**: http://127.0.0.1:8000/docs
- **API Base URL**: http://127.0.0.1:8000

## Required Environment Variables
Create a `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Project Structure
- `api.py` - FastAPI application with endpoints
- `retrieval.py` - Vector search functionality
- `gemini_client.py` - Gemini AI integration
- `rbac.py` - Role-based access control
- `frontend/` - Static web interface
- `offline-org-chatbot/data/` - Document data for ingestion

## Troubleshooting
1. **Virtual environment issues**: Delete `venv` folder and run `./start.sh` again
2. **Missing API key**: Edit `.env` file with your Gemini API key
3. **Port conflicts**: Change port in startup commands if 8000 is occupied
4. **Dependencies issues**: Run `pip install -r requirements.txt` manually

## Development
The server automatically reloads when you make changes to Python files.
