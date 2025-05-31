#!/usr/bin/env python3
"""
API Credentials Test Script
Tests Luno API authentication and environment variable loading
"""

import os
import sys
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth


def test_env_loading():
    """Test environment variable loading"""
    print("=== Environment Variable Test ===")

    # Load .env file explicitly
    load_dotenv()

    api_key = os.getenv("LUNO_API_KEY")
    api_secret = os.getenv("LUNO_API_SECRET")

    print(f"API Key found: {'Yes' if api_key else 'No'}")
    print(f"API Secret found: {'Yes' if api_secret else 'No'}")

    if api_key:
        print(f"API Key length: {len(api_key)}")
        print(
            f"API Key preview: {api_key[:3]}...{api_key[-3:] if len(api_key) > 6 else api_key}"
        )

    if api_secret:
        print(f"API Secret length: {len(api_secret)}")
        print(
            f"API Secret preview: {api_secret[:3]}...{api_secret[-3:] if len(api_secret) > 6 else api_secret}"
        )

    return api_key, api_secret


def test_api_authentication(api_key, api_secret):
    """Test Luno API authentication directly"""
    print("\n=== API Authentication Test ===")

    if not api_key or not api_secret:
        print("❌ Cannot test API - credentials missing")
        return False

    # Test with public endpoint first (no auth required)
    print("Testing public endpoint (ticker)...")
    try:
        response = requests.get(
            "https://api.luno.com/api/1/ticker?pair=XBTMYR", timeout=10
        )
        if response.status_code == 200:
            print("✅ Public API endpoint working")
            data = response.json()
            print(f"Current XBTMYR price: {data.get('last_trade', 'N/A')}")
        else:
            print(f"❌ Public API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Public API error: {e}")

    # Test authenticated endpoint
    print("\nTesting authenticated endpoint (balance)...")
    try:
        auth = HTTPBasicAuth(api_key, api_secret)
        response = requests.get(
            "https://api.luno.com/api/1/balance", auth=auth, timeout=10
        )

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ Authenticated API working")
            data = response.json()
            print(f"Balance data received: {len(data.get('balance', []))} currencies")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed (401 Unauthorized)")
            print(f"Response body: {response.text}")
            return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response body: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Authenticated API error: {e}")
        return False


def test_trading_bot_config():
    """Test trading bot config loading"""
    print("\n=== Trading Bot Config Test ===")

    try:
        # Load dotenv first
        load_dotenv()

        # Add the project root to the Python path
        project_root = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, project_root)
        from src.config.settings import TradingConfig

        config = TradingConfig()

        print(f"Config API Key: {'Set' if config.api_key else 'Not set'}")
        print(f"Config API Secret: {'Set' if config.api_secret else 'Not set'}")
        print(f"Trading Pair: {config.trading_pair}")
        print(f"Dry Run Mode: {config.dry_run}")

        return config.api_key and config.api_secret

    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False


def main():
    """Run all tests"""
    print("🔍 Luno Trading Bot Diagnostic Tests")
    print("=" * 50)

    # Test 1: Environment variables
    api_key, api_secret = test_env_loading()

    # Test 2: API Authentication
    api_working = test_api_authentication(api_key, api_secret)

    # Test 3: Trading bot config
    config_working = test_trading_bot_config()

    # Summary
    print("\n" + "=" * 50)
    print("🏁 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"Environment Loading: {'✅ PASS' if api_key and api_secret else '❌ FAIL'}")
    print(f"API Authentication: {'✅ PASS' if api_working else '❌ FAIL'}")
    print(f"Config Loading: {'✅ PASS' if config_working else '❌ FAIL'}")

    if not api_working:
        print("\n🚨 CRITICAL ISSUE DETECTED:")
        print(
            "API authentication is failing. This is preventing the trading bot from functioning."
        )
        print("\n💡 RECOMMENDED ACTIONS:")
        print("1. Verify API credentials are correct in .env file")
        print("2. Check if API key has required permissions (trading, balance)")
        print("3. Ensure API key is not expired or suspended")
        print("4. Try regenerating API credentials in Luno dashboard")

    return api_working and config_working


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
