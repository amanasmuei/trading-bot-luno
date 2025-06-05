#!/bin/bash
"""
Fix permissions for Docker containers
This script ensures that the Docker containers can write to log files and reports
"""

echo "🔧 Fixing permissions for Docker containers..."

# Create directories if they don't exist
mkdir -p logs
mkdir -p enhanced_reports

# Set proper permissions for logs directory
echo "📁 Setting permissions for logs directory..."
chmod 755 logs
touch logs/trading_bot.log
touch logs/enhanced_trading_bot.log
chmod 666 logs/trading_bot.log
chmod 666 logs/enhanced_trading_bot.log

# Set proper permissions for reports directory
echo "📁 Setting permissions for enhanced_reports directory..."
chmod 755 enhanced_reports

# Set ownership to match Docker container user (UID 1000)
echo "👤 Setting ownership for container user (UID 1000)..."
if command -v chown >/dev/null 2>&1; then
    # Try to set ownership to UID 1000 (trader user in container)
    sudo chown -R 1000:1000 logs enhanced_reports 2>/dev/null || {
        echo "⚠️  Could not change ownership. This is normal on some systems."
        echo "   The containers will still work with the current permissions."
    }
else
    echo "⚠️  chown command not available. Using alternative permissions..."
    chmod 777 logs enhanced_reports
fi

echo "✅ Permissions fixed!"
echo ""
echo "📋 Directory permissions:"
ls -la logs enhanced_reports 2>/dev/null || echo "Directories will be created when containers start"

echo ""
echo "🚀 You can now run: docker-compose up -d"
