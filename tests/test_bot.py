#!/usr/bin/env python3
"""
Trading Bot Test Suite
Tests the bot components without making real trades
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)


def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")

    try:
        from src.config.settings import TradingConfig
        from src.bot.technical_analysis import TechnicalAnalyzer, TechnicalIndicators
        from src.api.luno_client import LunoAPIClient, TradingPortfolio
        from src.bot.trading_bot import TradingBot
        from src.web.dashboard import TradingDashboard

        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    print("Testing configuration...")

    try:
        from src.config.settings import TradingConfig

        config = TradingConfig()

        print(f"✅ Trading pair: {config.trading_pair}")
        print(f"✅ Max position size: {config.max_position_size_percent}%")
        print(f"✅ Dry run mode: {config.dry_run}")
        print(f"✅ Support levels: {config.support_levels}")
        print(f"✅ Resistance levels: {config.resistance_levels}")

        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_technical_analysis():
    """Test technical analysis with sample data"""
    print("Testing technical analysis...")

    try:
        from src.config.settings import TradingConfig
        from src.bot.technical_analysis import TechnicalAnalyzer

        config = TradingConfig()
        analyzer = TechnicalAnalyzer(config)

        # Sample price data
        sample_prices = [
            450000,
            455000,
            460000,
            458000,
            462000,
            465000,
            463000,
            461000,
            459000,
            460641,
        ]

        # Test RSI calculation
        rsi = analyzer.calculate_rsi(sample_prices)
        print(f"✅ RSI calculation: {rsi}")

        # Test EMA calculation
        ema_9 = analyzer.calculate_ema(sample_prices, 9)
        ema_21 = analyzer.calculate_ema(sample_prices, 21)
        print(f"✅ EMA 9/21: {ema_9}/{ema_21}")

        # Test Bollinger Bands
        bb_upper, bb_middle, bb_lower = analyzer.calculate_bollinger_bands(
            sample_prices
        )
        print(f"✅ Bollinger Bands: {bb_upper}/{bb_middle}/{bb_lower}")

        return True
    except Exception as e:
        print(f"❌ Technical analysis error: {e}")
        return False


def test_api_client():
    """Test Luno API client (without authentication)"""
    print("Testing API client...")

    try:
        from src.api.luno_client import LunoAPIClient

        # Test with dummy credentials (won't work but shouldn't crash)
        client = LunoAPIClient("dummy_key", "dummy_secret")

        # Test signature generation
        timestamp, signature = client._generate_signature(
            "GET", "/api/1/ticker", {"pair": "XBTMYR"}
        )
        print(f"✅ Signature generation works")

        print("⚠️  Note: Actual API calls require valid credentials")

        return True
    except Exception as e:
        print(f"❌ API client error: {e}")
        return False


def test_environment():
    """Test environment setup"""
    print("Testing environment...")

    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found (using defaults)")

    # Check API credentials
    api_key = os.getenv("LUNO_API_KEY")
    api_secret = os.getenv("LUNO_API_SECRET")

    if api_key and api_secret:
        print("✅ API credentials configured")
        print(f"   API Key: {api_key[:8]}...")
    else:
        print("⚠️  API credentials not configured")
        print("   Set LUNO_API_KEY and LUNO_API_SECRET in .env file")

    return True


def test_dashboard_files():
    """Test dashboard file creation"""
    print("Testing dashboard setup...")

    try:
        from src.web.dashboard import create_dashboard_files

        # Create dashboard files
        create_dashboard_files()

        # Check if files were created
        if os.path.exists("templates/dashboard.html"):
            print("✅ Dashboard template created")
        else:
            print("❌ Dashboard template not created")
            return False

        return True
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False


def test_bot_creation():
    """Test bot creation without starting"""
    print("Testing bot creation...")

    try:
        from src.config.settings import TradingConfig
        from src.bot.trading_bot import TradingBot

        config = TradingConfig()
        config.dry_run = True  # Ensure dry run

        # Create bot instance
        bot = TradingBot(config)
        print("✅ Bot instance created successfully")

        # Test portfolio calculations
        volume, volume_str = bot.portfolio.calculate_position_size(460000, "BUY")
        print(f"✅ Position size calculation: {volume_str}")

        return True
    except Exception as e:
        print(f"❌ Bot creation error: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Trading Bot Test Suite")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Technical Analysis Test", test_technical_analysis),
        ("API Client Test", test_api_client),
        ("Environment Test", test_environment),
        ("Dashboard Test", test_dashboard_files),
        ("Bot Creation Test", test_bot_creation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Bot is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Configure your .env file with Luno API credentials")
        print("2. Run: python run_bot.py --dry-run")
        print("3. Open dashboard at http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please fix issues before running the bot.")

        if not os.getenv("LUNO_API_KEY"):
            print("\n💡 Tip: Create .env file with your Luno API credentials")
            print("   Copy .env.example to .env and fill in your details")


if __name__ == "__main__":
    main()
