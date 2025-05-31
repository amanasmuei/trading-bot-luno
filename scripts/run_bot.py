#!/usr/bin/env python3
"""
Trading Bot Launcher
Provides multiple ways to run the trading bot with different configurations
"""
import os
import sys
import argparse
from threading import Thread
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Change to the project root directory to ensure relative imports work
os.chdir(project_root)

from src.config.settings import TradingConfig
from src.bot.trading_bot import TradingBot
from src.web.dashboard import TradingDashboard, create_dashboard_files


def create_config_from_args(args) -> TradingConfig:
    """Create trading configuration from command line arguments"""

    config = TradingConfig()

    # Override with command line arguments
    if args.dry_run is not None:
        config.dry_run = args.dry_run

    if args.max_position_size:
        config.max_position_size_percent = args.max_position_size

    if args.stop_loss:
        config.stop_loss_percent = args.stop_loss

    if args.take_profit:
        config.take_profit_percent = args.take_profit

    if args.check_interval:
        config.check_interval = args.check_interval

    if args.trading_pair:
        config.trading_pair = args.trading_pair

    # Validate API credentials
    if not config.api_key or not config.api_secret:
        print("❌ Error: Luno API credentials not found!")
        print("Please set LUNO_API_KEY and LUNO_API_SECRET environment variables")
        print("or create a .env file based on .env.example")
        sys.exit(1)

    return config


def run_bot_only(config: TradingConfig):
    """Run only the trading bot"""
    print("🚀 Starting Trading Bot...")
    print(f"📊 Trading Pair: {config.trading_pair}")
    print(f"🎭 Mode: {'DRY RUN' if config.dry_run else 'LIVE TRADING'}")
    print(f"💰 Max Position Size: {config.max_position_size_percent}%")
    print("-" * 50)

    bot = TradingBot(config)

    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
        bot.stop()
    except Exception as e:
        print(f"💥 Bot crashed: {e}")
        bot.stop()
        sys.exit(1)


def run_dashboard_only(config: TradingConfig, host: str, port: int):
    """Run only the web dashboard"""
    print("🌐 Starting Web Dashboard...")
    print(f"📊 Dashboard URL: http://{host}:{port}")
    print("-" * 50)

    # Create dashboard files
    create_dashboard_files()

    dashboard = TradingDashboard(config)
    dashboard.run(host=host, port=port, debug=False)


def run_bot_with_dashboard(
    config: TradingConfig, dashboard_host: str, dashboard_port: int
):
    """Run both bot and dashboard"""
    print("🚀 Starting Trading Bot with Web Dashboard...")
    print(f"📊 Trading Pair: {config.trading_pair}")
    print(f"🎭 Mode: {'DRY RUN' if config.dry_run else 'LIVE TRADING'}")
    print(f"🌐 Dashboard URL: http://{dashboard_host}:{dashboard_port}")
    print("-" * 50)

    # Create dashboard files
    create_dashboard_files()

    # Start dashboard in a separate thread
    dashboard = TradingDashboard(config)
    dashboard_thread = Thread(
        target=dashboard.run,
        kwargs={"host": dashboard_host, "port": dashboard_port, "debug": False},
        daemon=True,
    )
    dashboard_thread.start()

    # Give dashboard time to start
    time.sleep(2)
    print(f"✅ Dashboard started at http://{dashboard_host}:{dashboard_port}")

    # Start trading bot
    bot = TradingBot(config)

    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
        bot.stop()
    except Exception as e:
        print(f"💥 Bot crashed: {e}")
        bot.stop()
        sys.exit(1)


def setup_environment():
    """Setup environment and check requirements"""

    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  No .env file found. Creating from template...")

        if os.path.exists(".env.example"):
            import shutil

            shutil.copy(".env.example", ".env")
            print("📄 Created .env file from .env.example")
            print("🔧 Please edit .env file with your Luno API credentials")
            return False
        else:
            print("❌ No .env.example template found!")
            return False

    return True


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="XBTMYR Trading Bot - Advanced cryptocurrency trading automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_bot.py --bot-only --dry-run        # Run bot in simulation mode
  python run_bot.py --dashboard-only             # Run only web dashboard
  python run_bot.py --dry-run                    # Run bot + dashboard in simulation
  python run_bot.py --live                       # Run bot + dashboard in live mode
  python run_bot.py --setup                      # Setup environment files
        """,
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--bot-only",
        action="store_true",
        help="Run only the trading bot (no dashboard)",
    )
    mode_group.add_argument(
        "--dashboard-only",
        action="store_true",
        help="Run only the web dashboard (no trading)",
    )
    mode_group.add_argument(
        "--setup", action="store_true", help="Setup environment and configuration files"
    )

    # Trading configuration
    parser.add_argument(
        "--dry-run", action="store_true", help="Run in simulation mode (no real trades)"
    )
    parser.add_argument(
        "--live", action="store_true", help="Run in live trading mode (real money!)"
    )
    parser.add_argument(
        "--trading-pair", default="XBTMYR", help="Trading pair (default: XBTMYR)"
    )
    parser.add_argument(
        "--max-position-size",
        type=float,
        help="Maximum position size as percentage of portfolio",
    )
    parser.add_argument("--stop-loss", type=float, help="Stop loss percentage")
    parser.add_argument("--take-profit", type=float, help="Take profit percentage")
    parser.add_argument("--check-interval", type=int, help="Check interval in seconds")

    # Dashboard configuration
    parser.add_argument(
        "--dashboard-host",
        default="127.0.0.1",
        help="Dashboard host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=5000,
        help="Dashboard port (default: 5000)",
    )

    args = parser.parse_args()

    # Handle setup mode
    if args.setup:
        if setup_environment():
            print("✅ Environment already configured")
        return

    # Check environment setup
    if not setup_environment():
        print("❌ Please configure your environment first:")
        print("   python run_bot.py --setup")
        return

    # Set dry run mode
    if args.live and args.dry_run:
        print("❌ Cannot specify both --live and --dry-run")
        sys.exit(1)

    if args.live:
        args.dry_run = False
    elif not args.live and not args.dry_run:
        args.dry_run = True  # Default to dry run for safety

    # Create configuration
    config = create_config_from_args(args)

    # Show warning for live trading
    if not config.dry_run:
        print("⚠️  " + "=" * 50)
        print("⚠️  LIVE TRADING MODE ENABLED")
        print("⚠️  This will use REAL MONEY!")
        print("⚠️  " + "=" * 50)

        confirm = input("Type 'YES' to confirm live trading: ")
        if confirm != "YES":
            print("❌ Live trading cancelled")
            sys.exit(1)

    # Run based on mode
    if args.bot_only:
        run_bot_only(config)
    elif args.dashboard_only:
        run_dashboard_only(config, args.dashboard_host, args.dashboard_port)
    else:
        run_bot_with_dashboard(config, args.dashboard_host, args.dashboard_port)


if __name__ == "__main__":
    main()
