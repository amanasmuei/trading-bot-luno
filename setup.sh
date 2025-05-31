#!/bin/bash

# Luno Trading Bot - Unix Setup
# Easy setup for Linux/macOS users

echo
echo "========================================"
echo "  LUNO TRADING BOT - UNIX SETUP"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    echo
    echo "Installation instructions:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu: sudo apt install python3 python3-pip"
    echo "  CentOS: sudo yum install python3 python3-pip"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo

echo "🚀 Starting setup wizard..."
echo

# Run the setup wizard
python3 setup.py

echo
echo "🎉 Setup completed!"
echo
echo "To start the bot, run:"
echo "  python3 launcher.py"
echo
