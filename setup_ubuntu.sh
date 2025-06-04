#!/bin/bash
# Ubuntu Setup Script for Luno Trading Bot
# This script handles permission issues and proper setup on Ubuntu systems

set -e  # Exit on any error

echo "🚀 Luno Trading Bot - Ubuntu Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Please don't run this script as root (sudo)${NC}"
    echo "Run it as a regular user, we'll ask for sudo when needed"
    exit 1
fi

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python 3.11+ is available
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    echo "Please install Python 3.11 or higher:"
    echo "sudo apt update && sudo apt install python3.11 python3.11-pip python3.11-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $PYTHON_VERSION found, but $REQUIRED_VERSION or higher is required"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

print_status "Python $PYTHON_VERSION is available"

# Create and setup logs directory with proper permissions
echo "Setting up logs directory..."
if [ ! -d "logs" ]; then
    mkdir -p logs
    print_status "Created logs directory"
else
    print_status "Logs directory already exists"
fi

# Set proper permissions for logs directory
chmod 755 logs
if [ -f "logs/trading_bot.log" ]; then
    chmod 666 logs/trading_bot.log
    print_status "Set permissions for existing log file"
fi

# Create log file if it doesn't exist
if [ ! -f "logs/trading_bot.log" ]; then
    touch logs/trading_bot.log
    chmod 666 logs/trading_bot.log
    print_status "Created log file with proper permissions"
fi

# Create virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Created virtual environment"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Installed Python dependencies"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create .env file if it doesn't exist
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Created .env file from template"
        print_warning "Please edit .env file with your Luno API credentials"
    else
        print_error ".env.example template not found"
        exit 1
    fi
else
    print_status ".env file already exists"
fi

# Create a run script for easier execution
echo "Creating run script..."
cat > run_bot_ubuntu.sh << 'EOF'
#!/bin/bash
# Run script for Luno Trading Bot on Ubuntu

# Activate virtual environment
source venv/bin/activate

# Run the bot with provided arguments
python scripts/run_bot.py "$@"
EOF

chmod +x run_bot_ubuntu.sh
print_status "Created run_bot_ubuntu.sh script"

# Create systemd service file (optional)
echo "Creating systemd service template..."
cat > luno-trading-bot.service << EOF
[Unit]
Description=Luno Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python $(pwd)/scripts/run_bot.py --dry-run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_status "Created systemd service template: luno-trading-bot.service"

# Final instructions
echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Luno API credentials:"
echo "   nano .env"
echo ""
echo "2. Test the bot in dry-run mode:"
echo "   ./run_bot_ubuntu.sh --dry-run"
echo ""
echo "3. Run the bot with dashboard:"
echo "   ./run_bot_ubuntu.sh --dry-run"
echo ""
echo "4. (Optional) Install as system service:"
echo "   sudo cp luno-trading-bot.service /etc/systemd/system/"
echo "   sudo systemctl enable luno-trading-bot"
echo "   sudo systemctl start luno-trading-bot"
echo ""
echo "For more options:"
echo "   ./run_bot_ubuntu.sh --help"
echo ""
print_warning "Remember to test in dry-run mode first!"
