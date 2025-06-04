# Ubuntu Installation Troubleshooting Guide

## Permission Error Fix

If you encountered the error:
```
PermissionError: [Errno 13] Permission denied: '/app/logs/trading_bot.log'
```

This guide will help you resolve it.

## Quick Fix

### Option 1: Use the Ubuntu Setup Script (Recommended)

```bash
# Make sure you're in the project directory
cd /path/to/xbtmyr-trading-bot

# Run the Ubuntu setup script
./setup_ubuntu.sh

# Test the bot
./run_bot_ubuntu.sh --dry-run
```

### Option 2: Manual Fix

If you prefer to fix it manually:

```bash
# 1. Fix permissions for logs directory
mkdir -p logs
chmod 755 logs
touch logs/trading_bot.log
chmod 666 logs/trading_bot.log

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run the bot
python scripts/run_bot.py --dry-run
```

## What Was Fixed

1. **Improved Logging Setup**: The bot now gracefully handles permission errors and falls back to console-only logging if file logging fails.

2. **Proper Directory Permissions**: The setup script ensures the logs directory has the correct permissions (755) and the log file is writable (666).

3. **Docker Improvements**: Updated Dockerfile to create the log file with proper permissions during build.

4. **Virtual Environment**: Using a virtual environment prevents system-wide permission issues.

## Common Issues and Solutions

### Issue: Python Version Error
```
Python 3.8 found, but 3.11 or higher is required
```

**Solution**: Install Python 3.11+
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

### Issue: Permission Denied on System Directories
```
PermissionError: [Errno 13] Permission denied: '/usr/local/lib/...'
```

**Solution**: Use virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Log File Already Exists with Wrong Permissions
```bash
# Fix existing log file permissions
sudo chown $USER:$USER logs/trading_bot.log
chmod 666 logs/trading_bot.log
```

### Issue: Running as Root
Don't run the bot as root. If you need to:
```bash
# Change ownership back to your user
sudo chown -R $USER:$USER /path/to/trading-bot
```

## Docker Users

If you're using Docker, rebuild the container with the updated Dockerfile:

```bash
# Rebuild the container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f trading-bot
```

## Testing the Fix

1. **Test in Dry Run Mode** (Safe):
```bash
./run_bot_ubuntu.sh --dry-run
```

2. **Check Log Output**:
```bash
tail -f logs/trading_bot.log
```

3. **Verify Permissions**:
```bash
ls -la logs/
# Should show: -rw-rw-rw- 1 user user ... trading_bot.log
```

## System Service Setup (Optional)

To run the bot as a system service:

```bash
# Copy service file
sudo cp luno-trading-bot.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable luno-trading-bot
sudo systemctl start luno-trading-bot

# Check status
sudo systemctl status luno-trading-bot

# View logs
sudo journalctl -u luno-trading-bot -f
```

## Support

If you continue to have issues:

1. Check that you're not running as root
2. Ensure Python 3.11+ is installed
3. Use the virtual environment
4. Verify file permissions with `ls -la logs/`
5. Check the console output for detailed error messages

The bot now includes improved error handling and will display helpful messages if permission issues occur.
