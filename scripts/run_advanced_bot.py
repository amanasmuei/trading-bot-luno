#!/usr/bin/env python3
"""
Advanced Trading Bot Runner
Launch script for the next-generation multi-pair trading bot
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.bot.advanced_trading_bot import AdvancedTradingBot
from src.config.enhanced_settings import EnhancedTradingConfig
from src.config.strategy_templates import ConfigurationManager
from src.notifications.notification_manager import NotificationConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_logging(log_level="INFO", log_file=None):
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Default log file
    if log_file is None:
        log_file = logs_dir / f"advanced_trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


def create_trading_config(args):
    """Create trading configuration from arguments and templates"""
    
    config_manager = ConfigurationManager()
    
    # Determine strategy template
    if args.strategy:
        template_name = args.strategy
    elif args.risk_level:
        if args.risk_level == "low":
            template_name = "conservative"
        elif args.risk_level == "high":
            template_name = "aggressive"
        else:
            template_name = "moderate"
    else:
        template_name = "moderate"  # Default
    
    # Create configuration
    config = config_manager.create_trading_config(
        template_name=template_name,
        trading_pair=args.pair,
        custom_settings={
            "dry_run": args.dry_run,
            "check_interval": args.interval,
            "max_daily_trades": args.max_trades
        }
    )
    
    return config


def create_notification_config(args):
    """Create notification configuration"""
    
    notification_config = NotificationConfig()
    
    # Email configuration
    if args.email:
        notification_config.email_enabled = True
        notification_config.email_username = os.getenv("EMAIL_USERNAME", "")
        notification_config.email_password = os.getenv("EMAIL_PASSWORD", "")
        notification_config.recipient_emails = [args.email]
    
    # Discord webhook
    if args.discord_webhook:
        notification_config.discord_enabled = True
        notification_config.discord_webhook_url = args.discord_webhook
    
    # Slack webhook
    if args.slack_webhook:
        notification_config.slack_enabled = True
        notification_config.slack_webhook_url = args.slack_webhook
    
    return notification_config


def validate_environment():
    """Validate that required environment variables are set"""
    
    required_vars = ["LUNO_API_KEY", "LUNO_API_SECRET"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return False
    
    return True


def print_startup_info(config, notification_config):
    """Print startup information"""
    
    print("\n" + "="*60)
    print("🚀 ADVANCED LUNO TRADING BOT")
    print("="*60)
    print(f"Trading Pair: {config.trading_pair}")
    print(f"Mode: {'DRY RUN (Simulation)' if config.dry_run else 'LIVE TRADING'}")
    print(f"Max Position Size: {config.max_position_size_percent}%")
    print(f"Stop Loss: {config.base_stop_loss_percent}%")
    print(f"Take Profit: {config.base_take_profit_percent}%")
    print(f"Max Daily Trades: {config.max_daily_trades}")
    print(f"Check Interval: {config.check_interval} seconds")
    
    if notification_config:
        notifications = []
        if notification_config.email_enabled:
            notifications.append("Email")
        if notification_config.discord_enabled:
            notifications.append("Discord")
        if notification_config.slack_enabled:
            notifications.append("Slack")
        
        if notifications:
            print(f"Notifications: {', '.join(notifications)}")
        else:
            print("Notifications: Disabled")
    
    print("="*60)
    
    if not config.dry_run:
        print("⚠️  WARNING: LIVE TRADING MODE ENABLED")
        print("⚠️  This bot will place real orders with real money!")
        print("="*60)


def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(
        description="Advanced Multi-Pair Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in simulation mode with default settings
  python scripts/run_advanced_bot.py --dry-run
  
  # Run live trading with conservative strategy
  python scripts/run_advanced_bot.py --strategy conservative
  
  # Run with custom pair and notifications
  python scripts/run_advanced_bot.py --pair ETHMYR --email user@example.com
  
  # Run with high-risk strategy and Discord notifications
  python scripts/run_advanced_bot.py --strategy aggressive --discord-webhook https://discord.com/api/webhooks/...
        """
    )
    
    # Trading configuration
    parser.add_argument(
        "--pair", 
        default="XBTMYR",
        help="Trading pair (default: XBTMYR)"
    )
    
    parser.add_argument(
        "--strategy",
        choices=["conservative", "moderate", "aggressive", "scalping", "swing"],
        help="Trading strategy template"
    )
    
    parser.add_argument(
        "--risk-level",
        choices=["low", "medium", "high"],
        help="Risk level (alternative to --strategy)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in simulation mode (no real trades)"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)"
    )
    
    parser.add_argument(
        "--max-trades",
        type=int,
        default=5,
        help="Maximum daily trades (default: 5)"
    )
    
    # Notification configuration
    parser.add_argument(
        "--email",
        help="Email address for notifications"
    )
    
    parser.add_argument(
        "--discord-webhook",
        help="Discord webhook URL for notifications"
    )
    
    parser.add_argument(
        "--slack-webhook",
        help="Slack webhook URL for notifications"
    )
    
    # Logging configuration
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Custom log file path"
    )
    
    # Advanced options
    parser.add_argument(
        "--advanced",
        action="store_true",
        help="Enable advanced multi-pair mode"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level, args.log_file)
    
    try:
        # Validate environment
        if not validate_environment():
            sys.exit(1)
        
        # Create configurations
        trading_config = create_trading_config(args)
        notification_config = create_notification_config(args)
        
        # Print startup information
        print_startup_info(trading_config, notification_config)
        
        # Confirm live trading
        if not trading_config.dry_run:
            response = input("\nDo you want to continue with LIVE TRADING? (yes/no): ")
            if response.lower() != "yes":
                print("Trading cancelled for safety.")
                sys.exit(0)
        
        # Create and start the bot
        logger.info("Initializing Advanced Trading Bot...")
        
        bot = AdvancedTradingBot(trading_config, notification_config)
        
        logger.info("Starting trading bot...")
        print(f"\n🚀 Starting Advanced Trading Bot...")
        print(f"📊 Monitor your trades and performance in real-time")
        print(f"🛑 Press Ctrl+C to stop the bot safely")
        print(f"📝 Logs are being written to: {args.log_file or 'logs/'}")
        
        # Start the bot
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print(f"\n🛑 Bot stopped by user")
        
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        print(f"\n❌ Critical error: {e}")
        print(f"📝 Check the log file for detailed error information")
        sys.exit(1)
    
    finally:
        print(f"\n👋 Advanced Trading Bot shutdown complete")


if __name__ == "__main__":
    main()
