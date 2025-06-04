#!/usr/bin/env python3
"""
Launch the Trading Bot Dashboard
"""

import sys
import os
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Load environment variables
load_dotenv()

from src.config.settings import TradingConfig
from src.web.dashboard import TradingDashboard


def main():
    """Launch the dashboard"""
    print("🚀 Starting XBTMYR Trading Bot Dashboard...")

    try:
        # Load configuration
        config = TradingConfig()

        # Create and run dashboard
        dashboard = TradingDashboard(config)

        print(
            f"📊 Dashboard running at: http://{config.dashboard_host}:{config.dashboard_port}"
        )
        print("✨ Features available:")
        print("   • Live price monitoring")
        print("   • Technical analysis charts (RSI, EMA, MACD, Bollinger Bands)")
        print("   • Portfolio tracking")
        print("   • Trading history")
        print("   • Bot status monitoring")
        print("\n⏯️  Press Ctrl+C to stop the dashboard")

        # Run the dashboard
        dashboard.run(
            host=config.dashboard_host, port=config.dashboard_port, debug=False
        )

    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        print("💡 Make sure your .env file is properly configured")
        sys.exit(1)


if __name__ == "__main__":
    main()
