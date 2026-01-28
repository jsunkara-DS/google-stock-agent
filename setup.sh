#!/bin/bash
# Local development setup script

echo "🛠️  Setting up development environment..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📚 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - GEMINI_API_KEY (from Google AI Studio)"
    echo "   - ALPHA_VANTAGE_API_KEY (from Alpha Vantage)"
fi

# Create data directory
mkdir -p data logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: python main.py"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "Or use Docker:"
echo "  docker-compose up --build"
