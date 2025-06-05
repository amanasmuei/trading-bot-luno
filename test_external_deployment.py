#!/usr/bin/env python3
"""
Test script to verify external server deployment is working correctly
"""

import requests
import json
import time
import sys

def test_endpoint(url, description, expected_status=200):
    """Test an endpoint and return result"""
    try:
        print(f"Testing {description}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == expected_status:
            print(f"✅ {description} - OK (Status: {response.status_code})")
            return True
        else:
            print(f"❌ {description} - Failed (Status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {description} - Connection refused")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {description} - Timeout")
        return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def test_bot_status(base_url):
    """Test bot status endpoint"""
    try:
        print("Testing bot status endpoint...")
        response = requests.get(f"{base_url}:5002/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bot Status - OK")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ Bot Status - Failed (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Bot Status - Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing External Server Deployment")
    print("=" * 50)
    
    # Test localhost (for local testing)
    base_url = "http://localhost"
    
    tests = [
        (f"{base_url}:5002/health", "Bot Health Check"),
        (f"{base_url}:5003", "Dashboard Access"),
    ]
    
    results = []
    
    # Run basic connectivity tests
    for url, description in tests:
        result = test_endpoint(url, description)
        results.append(result)
    
    # Test bot status if health check passed
    if results[0]:  # If bot health check passed
        bot_status_result = test_bot_status(base_url)
        results.append(bot_status_result)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed! ({passed}/{total})")
        print("\n🎉 Your external server deployment is working correctly!")
        print("\n📋 Access URLs:")
        print(f"   Dashboard: {base_url}:5003")
        print(f"   Bot Health: {base_url}:5002/health")
        print(f"   Bot Status: {base_url}:5002/status")
        return 0
    else:
        print(f"❌ Some tests failed ({passed}/{total})")
        print("\n🔧 Troubleshooting:")
        print("1. Check if containers are running: docker-compose ps")
        print("2. Check container logs: docker logs luno-dashboard")
        print("3. Check firewall settings")
        print("4. Verify ports 5002 and 5003 are open")
        return 1

if __name__ == "__main__":
    sys.exit(main())
