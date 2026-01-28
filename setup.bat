#!/bin/bash
# Local development setup script for Windows

echo "Tools Setting up development environment..."

# Create virtual environment
if not exist "venv" (
    echo "Creating virtual environment..."
    python -m venv venv
)

# Activate virtual environment
call venv\Scripts\activate.bat

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if not exist ".env" (
    echo "Creating .env file..."
    copy .env.example .env
    echo.
    echo "Please edit .env and add your API keys:"
    echo "   - GEMINI_API_KEY (from Google AI Studio)"
    echo "   - ALPHA_VANTAGE_API_KEY (from Alpha Vantage)"
)

# Create data directory
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo.
echo "Setup complete!"
echo.
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: python main.py"
echo "3. Visit: http://localhost:8000/docs"
echo.
echo "Or use Docker:"
echo "  docker-compose up --build"
