#!/usr/bin/env python3
"""
Enhanced Docker Setup Script for Luno Trading Bot
Sets up the enhanced trading strategy with Docker Compose
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🚀 Enhanced Luno Trading Bot Docker Setup")
    print("=" * 60)
    print()


def check_requirements():
    """Check if Docker and Docker Compose are installed"""
    print("📋 Checking requirements...")

    # Check Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker found: {result.stdout.strip()}")
        else:
            print("❌ Docker not found")
            return False
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker first.")
        return False

    # Check Docker Compose
    try:
        result = subprocess.run(
            ["docker", "compose", "version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ Docker Compose found: {result.stdout.strip()}")
        else:
            print("❌ Docker Compose not found")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose not found. Please install Docker Compose first.")
        return False

    print()
    return True


def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")

    directories = [
        "logs",
        "enhanced_reports",
        "monitoring/grafana",
        "monitoring/grafana/dashboards",
        "monitoring/grafana/datasources",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

    print()


def setup_env_file():
    """Setup enhanced .env file"""
    print("⚙️  Setting up environment configuration...")

    env_example_content = """# Enhanced Luno Trading Bot Configuration

# Luno API Credentials (REQUIRED)
LUNO_API_KEY=your_api_key_here
LUNO_API_SECRET=your_api_secret_here

# Trading Configuration
TRADING_PAIR=XBTMYR
TRADING_STRATEGY=enhanced

# Enhanced Strategy Settings
BOT_MODE=enhanced
DRY_RUN=true
CHECK_INTERVAL=30

# Risk Management
MAX_POSITION_SIZE_PERCENT=1.5
BASE_STOP_LOSS_PERCENT=3.0
BASE_TAKE_PROFIT_PERCENT=6.0
MIN_RISK_REWARD_RATIO=1.5
MAX_DAILY_TRADES=5

# Confidence Thresholds
MIN_CONFIDENCE_BUY=0.6
MIN_CONFIDENCE_SELL=0.6
STRONG_SIGNAL_THRESHOLD=0.8

# Technical Analysis
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
EMA_SHORT=9
EMA_MEDIUM=21
EMA_LONG=50

# Volume Analysis
VOLUME_CONFIRMATION_THRESHOLD=1.2
VOLUME_PERIOD=10

# Market Regime Filters
TREND_FILTER_ENABLED=true
VOLATILITY_FILTER_ENABLED=true

# Time Filters
MIN_TIME_BETWEEN_TRADES=1800

# Logging
LOG_LEVEL=INFO

# Dashboard Settings
DASHBOARD_PORT=5002
DASHBOARD_MODE=enhanced

# Optional: Redis Cache
REDIS_ENABLED=false
REDIS_HOST=redis
REDIS_PORT=6379

# Optional: Monitoring
MONITORING_ENABLED=false
GRAFANA_PASSWORD=admin123
"""

    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_example_content)
        print("✅ Created .env file with enhanced configuration")
        print("⚠️  Please update your LUNO_API_KEY and LUNO_API_SECRET in .env file")
    else:
        print("ℹ️  .env file already exists")

        # Check if enhanced settings are present
        with open(".env", "r") as f:
            content = f.read()

        if "TRADING_STRATEGY=enhanced" not in content:
            print("📝 Adding enhanced strategy settings to existing .env...")
            with open(".env", "a") as f:
                f.write("\n# Enhanced Strategy Settings\n")
                f.write("TRADING_STRATEGY=enhanced\n")
                f.write("BOT_MODE=enhanced\n")
                f.write("DASHBOARD_MODE=enhanced\n")
            print("✅ Enhanced settings added to .env")

    print()


def setup_monitoring():
    """Setup monitoring configuration"""
    print("📊 Setting up monitoring configuration...")

    # Grafana datasource configuration
    datasource_config = """apiVersion: 1

datasources:
  - name: Luno Bot Logs
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
"""

    with open("monitoring/grafana/datasources/datasource.yml", "w") as f:
        f.write(datasource_config)

    # Basic dashboard configuration
    dashboard_config = """apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
"""

    with open("monitoring/grafana/dashboards/dashboard.yml", "w") as f:
        f.write(dashboard_config)

    print("✅ Monitoring configuration created")
    print()


def display_usage_instructions():
    """Display usage instructions"""
    print("🎯 Usage Instructions:")
    print()

    print("1️⃣  Start Enhanced Bot (Recommended):")
    print("   docker compose -f docker-compose.enhanced.yml up -d")
    print()

    print("2️⃣  Start Enhanced Bot + Original Bot (for comparison):")
    print("   docker compose -f docker-compose.enhanced.yml --profile original up -d")
    print()

    print("3️⃣  Start with Redis caching:")
    print("   docker compose -f docker-compose.enhanced.yml --profile with-cache up -d")
    print()

    print("4️⃣  Start with monitoring:")
    print("   docker compose -f docker-compose.enhanced.yml --profile monitoring up -d")
    print()

    print("5️⃣  Start everything:")
    print(
        "   docker compose -f docker-compose.enhanced.yml --profile original --profile with-cache --profile monitoring up -d"
    )
    print()

    print("📱 Access Points:")
    print("   • Enhanced Bot Dashboard: http://localhost:5002")
    print("   • Original Bot Dashboard: http://localhost:5001")
    print("   • Enhanced Dashboard: http://localhost:5003")
    print("   • Grafana Monitoring: http://localhost:3000 (admin/admin123)")
    print()

    print("📋 Management Commands:")
    print("   • View logs: docker compose -f docker-compose.enhanced.yml logs -f")
    print("   • Stop all: docker compose -f docker-compose.enhanced.yml down")
    print("   • Restart: docker compose -f docker-compose.enhanced.yml restart")
    print("   • Check status: docker compose -f docker-compose.enhanced.yml ps")
    print()


def build_images():
    """Build Docker images"""
    print("🔨 Building Docker images...")

    try:
        # Build enhanced bot image
        print("Building enhanced bot image...")
        result = subprocess.run(
            [
                "docker",
                "build",
                "-f",
                "Dockerfile.enhanced",
                "-t",
                "luno-enhanced-bot:latest",
                ".",
            ],
            check=True,
        )
        print("✅ Enhanced bot image built successfully")

        print()
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build images: {e}")
        return False


def main():
    """Main setup function"""
    print_banner()

    if not check_requirements():
        print(
            "❌ Requirements not met. Please install Docker and Docker Compose first."
        )
        sys.exit(1)

    setup_directories()
    setup_env_file()
    setup_monitoring()

    print("🔧 Setup complete! Choose your next step:")
    print()
    print("A) Build and start enhanced bot immediately")
    print("B) Just setup (manual start later)")
    print()

    choice = input("Enter your choice (A/B): ").strip().upper()

    if choice == "A":
        if build_images():
            print("\n🚀 Starting enhanced bot...")
            try:
                subprocess.run(
                    [
                        "docker",
                        "compose",
                        "-f",
                        "docker-compose.enhanced.yml",
                        "up",
                        "-d",
                    ],
                    check=True,
                )
                print("✅ Enhanced bot started successfully!")
                print("\n📱 Access your bot at: http://localhost:5002")
                print("📊 Enhanced dashboard at: http://localhost:5003")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to start bot: {e}")
    else:
        display_usage_instructions()

    print("\n⚠️  Important:")
    print("   1. Update your API keys in .env file")
    print("   2. Bot starts in DRY_RUN mode for safety")
    print("   3. Monitor performance before enabling live trading")
    print("   4. Check logs regularly for any issues")
    print("\n🎉 Enhanced Luno Trading Bot setup complete!")


if __name__ == "__main__":
    main()
