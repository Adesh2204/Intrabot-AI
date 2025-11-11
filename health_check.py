#!/usr/bin/env python3
"""
Diagnostic and troubleshooting script for Intrabot-AI
Run this script to check the health of your setup.
"""

import os
import sys
import subprocess
from pathlib import Path
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (Compatible)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Requires Python 3.8+)")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n📦 Checking dependencies...")
    required_packages = [
        'fastapi', 'uvicorn', 'sentence_transformers', 
        'chromadb', 'google.generativeai', 'python_multipart'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'google.generativeai':
                import google.generativeai
            elif package == 'python_multipart':
                import multipart
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (Missing)")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_environment():
    """Check environment variables and configuration"""
    print("\n🔧 Checking environment configuration...")
    
    # Check .env file
    env_path = Path('.env')
    if env_path.exists():
        print("   ✅ .env file exists")
        with open(env_path, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content and 'your_gemini_api_key_here' not in content:
                print("   ✅ GEMINI_API_KEY is configured")
                return True
            else:
                print("   ⚠️  GEMINI_API_KEY not properly set in .env file")
                return False
    else:
        print("   ❌ .env file missing")
        return False

def check_data_files():
    """Check if data files exist"""
    print("\n📁 Checking data files...")
    data_dir = Path('offline-org-chatbot/data')
    
    if not data_dir.exists():
        print("   ❌ Data directory missing")
        return False
    
    required_files = ['hr_faq.md', 'employee_handbook.md', 'onboarding_guide.md']
    existing_files = list(data_dir.glob('*.md'))
    
    if len(existing_files) == 0:
        print("   ❌ No data files found")
        return False
    
    print(f"   ✅ Found {len(existing_files)} data files")
    for file in existing_files:
        print(f"      - {file.name}")
    
    return True

def check_database():
    """Check ChromaDB setup"""
    print("\n🗄️  Checking database...")
    chroma_dir = Path('offline-org-chatbot/.chromadb')
    
    if not chroma_dir.exists():
        print("   ⚠️  ChromaDB not initialized")
        return False
    
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(chroma_dir))
        collections = client.list_collections()
        
        if len(collections) > 0:
            print(f"   ✅ ChromaDB initialized with {len(collections)} collection(s)")
            for collection in collections:
                print(f"      - {collection.name}")
            return True
        else:
            print("   ⚠️  ChromaDB exists but no collections found")
            return False
    except Exception as e:
        print(f"   ❌ ChromaDB error: {e}")
        return False

def check_api_endpoints():
    """Test API endpoints (if server is running)"""
    print("\n🌐 Checking API endpoints...")
    try:
        import requests
        
        # Test basic endpoint
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        if response.status_code == 200:
            print("   ✅ Main API endpoint responding")
            
            # Test static files
            static_response = requests.get('http://127.0.0.1:8000/static/', timeout=5)
            if static_response.status_code == 200:
                print("   ✅ Frontend static files accessible")
            else:
                print("   ⚠️  Frontend static files not accessible")
                
            return True
        else:
            print(f"   ❌ API not responding (Status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ℹ️  API server not running (start with './start.sh' or 'npm start')")
        return None
    except ImportError:
        print("   ⚠️  requests package not available for API testing")
        return None
    except Exception as e:
        print(f"   ❌ API test error: {e}")
        return False

def provide_solutions(issues):
    """Provide solutions for detected issues"""
    if not issues:
        print("\n🎉 All checks passed! Your Intrabot-AI setup is ready.")
        print("\n🚀 To start the application:")
        print("   ./start.sh")
        print("   or")
        print("   npm start")
        print("\n🌐 Access points:")
        print("   Frontend: http://127.0.0.1:8000/static/")
        print("   API Docs: http://127.0.0.1:8000/docs")
        return

    print("\n🔧 Solutions for detected issues:")
    
    if 'python_version' in issues:
        print("\n   🐍 Python Version Issue:")
        print("      - Install Python 3.8 or higher")
        print("      - Use pyenv or conda to manage Python versions")
    
    if 'dependencies' in issues:
        print("\n   📦 Missing Dependencies:")
        print("      - Run: pip install -r requirements.txt")
        print("      - Or: npm run install")
    
    if 'environment' in issues:
        print("\n   🔧 Environment Configuration:")
        print("      - Copy .env.example to .env")
        print("      - Get a Gemini API key from Google AI Studio")
        print("      - Set GEMINI_API_KEY in .env file")
    
    if 'data_files' in issues:
        print("\n   📁 Data Files Missing:")
        print("      - Run: python init_db.py")
        print("      - Or add your own .md/.txt files to offline-org-chatbot/data/")
    
    if 'database' in issues:
        print("\n   🗄️  Database Issues:")
        print("      - Run: python init_db.py")
        print("      - Or: python src/ingest.py")
        print("      - Make sure data files exist first")

def main():
    print("🔍 Intrabot-AI Health Check\n" + "="*40)
    
    issues = []
    
    # Run all checks
    if not check_python_version():
        issues.append('python_version')
    
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        issues.append('dependencies')
    
    if not check_environment():
        issues.append('environment')
    
    if not check_data_files():
        issues.append('data_files')
    
    if not check_database():
        issues.append('database')
    
    # API check is optional (server might not be running)
    check_api_endpoints()
    
    print("\n" + "="*40)
    provide_solutions(issues)

if __name__ == "__main__":
    main()
