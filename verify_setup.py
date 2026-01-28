#!/usr/bin/env python3
"""
Verify the Stock Agent setup and dependencies.
Run this to check if everything is configured correctly.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("✓ Checking Python version...", end=" ")
    required = (3, 11)
    current = sys.version_info[:2]
    if current >= required:
        print(f"✓ Python {current[0]}.{current[1]}")
        return True
    else:
        print(f"✗ Python {current[0]}.{current[1]} (need {required[0]}.{required[1]}+)")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("✓ Checking dependencies...", end=" ")
    required_packages = [
        "fastapi",
        "uvicorn",
        "google.generativeai",
        "requests",
        "pydantic",
        "dotenv",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if not missing:
        print("✓ All packages installed")
        return True
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        print("\n  Install with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists."""
    print("✓ Checking .env file...", end=" ")
    if Path(".env").exists():
        print("✓ .env file found")
        return True
    elif Path(".env.example").exists():
        print("✗ .env file not found (but .env.example exists)")
        print("\n  Run: cp .env.example .env")
        return False
    else:
        print("✗ Neither .env nor .env.example found")
        return False

def check_env_vars():
    """Check if required environment variables are set."""
    print("✓ Checking API keys in .env...", end=" ")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required = [
        "GEMINI_API_KEY",
        "ALPHA_VANTAGE_API_KEY",
    ]
    
    missing = [var for var in required if not os.getenv(var)]
    
    if not missing:
        print("✓ All required keys present")
        return True
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        print("\n  Edit .env and add:")
        for var in missing:
            print(f"    {var}=your_key_here")
        return False

def check_api_connectivity():
    """Test API connectivity."""
    print("✓ Checking API connectivity...")
    
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("  ✗ Gemini API key not configured")
            return False
        
        genai.configure(api_key=api_key)
        model_info = genai.list_models()
        print("  ✓ Gemini API accessible")
        return True
    except Exception as e:
        print(f"  ✗ Gemini API error: {e}")
        return False

def check_project_structure():
    """Check if project structure is correct."""
    print("✓ Checking project structure...", end=" ")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "src/config.py",
        "src/stock_fetcher.py",
        "src/gemini_agent.py",
        "src/storage.py",
    ]
    
    missing = [f for f in required_files if not Path(f).exists()]
    
    if not missing:
        print("✓ All required files present")
        return True
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        return False

def main():
    """Run all checks."""
    print("\n" + "="*50)
    print("Google Stock Agent - Setup Verification")
    print("="*50 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        (".env File", check_env_file),
        ("Environment Variables", check_env_vars),
        ("API Connectivity", check_api_connectivity),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            results.append(check_func())
        except Exception as e:
            print(f"✗ {name} check failed: {e}")
            results.append(False)
        print()
    
    # Summary
    print("="*50)
    passed = sum(results)
    total = len(results)
    print(f"Summary: {passed}/{total} checks passed\n")
    
    if all(results):
        print("✓ All checks passed! Ready to run:")
        print("\n  python main.py")
        print("\nThen visit: http://localhost:8000/docs")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nFor help, see QUICKSTART.md or README.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
