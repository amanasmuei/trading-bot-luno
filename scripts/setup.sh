#!/bin/bash

# Luno Trading Bot Setup Script
# This script helps set up the trading bot environment

echo "🚀 Luno Trading Bot Setup"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment (optional but recommended)
read -p "🤔 Do you want to create a virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv trading_bot_env
    
    echo "🔧 Activating virtual environment..."
    source trading_bot_env/bin/activate
    
    echo "✅ Virtual environment created and activated"
    echo "💡 To activate later: source trading_bot_env/bin/activate"
fi

# Install required packages
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All packages installed successfully"
else
    echo "❌ Failed to install some packages"
    echo "Please check the error messages above"
    exit 1
fi

# Setup environment file
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    
    echo ""
    echo "🔧 IMPORTANT: Please edit the .env file with your Luno API credentials"
    echo "   1. Get API credentials from: https://www.luno.com/wallet/security/api_keys"
    echo "   2. Edit .env file: nano .env"
    echo "   3. Set LUNO_API_KEY and LUNO_API_SECRET"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
chmod +x scripts/run_bot.py
chmod +x tests/test_bot.py
echo "✅ Scripts made executable"

# Create logs directory
mkdir -p logs
echo "✅ Logs directory created"

# Test the installation
echo ""
echo "🧪 Testing installation..."
python3 tests/test_bot.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Luno API credentials"
echo "2. Test the bot: python3 scripts/run_bot.py --dry-run"
echo "3. Open dashboard: http://localhost:5000"
echo ""
echo "📖 For detailed instructions, see README.md"
echo ""
echo "⚠️  REMEMBER: Always start with dry-run mode!"
echo "⚠️  Only use live trading after thorough testing!"