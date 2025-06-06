#!/usr/bin/env python3
"""
SaaS Platform Test Suite
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta

# Set up test environment
os.environ['TESTING'] = 'true'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from src.saas_app import create_app
from src.models.base import db, init_db
from src.auth.auth_manager import AuthManager
from src.models.user import User
from src.models.subscription import SubscriptionPlan, Subscription


class SaaSPlatformTestCase(unittest.TestCase):
    """Base test case for SaaS platform"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize database
        init_db(self.app)
        
        # Create test user
        self.test_user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        self.test_user, _ = AuthManager.register_user(**self.test_user_data)
        self.test_user.is_verified = True
        self.test_user.save()
        
        # Create admin user
        self.admin_user_data = {
            'email': 'admin@example.com',
            'password': 'adminpassword123',
            'first_name': 'Admin',
            'last_name': 'User'
        }
        
        self.admin_user, _ = AuthManager.register_user(**self.admin_user_data)
        self.admin_user.is_admin = True
        self.admin_user.is_verified = True
        self.admin_user.save()
    
    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def get_auth_headers(self, user=None):
        """Get authentication headers for API requests"""
        if user is None:
            user = self.test_user
        
        access_token, _, _ = AuthManager.generate_tokens(user)
        return {'Authorization': f'Bearer {access_token}'}


class AuthenticationTestCase(SaaSPlatformTestCase):
    """Test authentication functionality"""
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post('/api/v1/auth/register', 
            data=json.dumps({
                'email': 'newuser@example.com',
                'password': 'newpassword123',
                'first_name': 'New',
                'last_name': 'User'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'newuser@example.com')
    
    def test_user_login(self):
        """Test user login"""
        response = self.client.post('/api/v1/auth/login',
            data=json.dumps({
                'email': self.test_user_data['email'],
                'password': self.test_user_data['password']
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/v1/auth/login',
            data=json.dumps({
                'email': self.test_user_data['email'],
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get('/api/v1/auth/me')
        self.assertEqual(response.status_code, 401)
    
    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token"""
        headers = self.get_auth_headers()
        response = self.client.get('/api/v1/auth/me', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('user', data)


class SubscriptionTestCase(SaaSPlatformTestCase):
    """Test subscription functionality"""
    
    def test_get_subscription_plans(self):
        """Test getting subscription plans"""
        response = self.client.get('/api/v1/subscriptions/plans')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('plans', data)
        self.assertGreater(len(data['plans']), 0)
    
    def test_get_current_subscription(self):
        """Test getting current user subscription"""
        headers = self.get_auth_headers()
        response = self.client.get('/api/v1/subscriptions/current', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('subscription', data)
    
    def test_upgrade_subscription(self):
        """Test subscription upgrade"""
        # Get a plan to upgrade to
        basic_plan = SubscriptionPlan.query.filter_by(name='Basic').first()
        
        headers = self.get_auth_headers()
        response = self.client.post('/api/v1/subscriptions/upgrade',
            data=json.dumps({'plan_id': basic_plan.id}),
            content_type='application/json',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('subscription', data)
        self.assertEqual(data['subscription']['plan']['name'], 'Basic')


class TradingTestCase(SaaSPlatformTestCase):
    """Test trading functionality"""
    
    def test_create_trading_config(self):
        """Test creating trading configuration"""
        headers = self.get_auth_headers()
        response = self.client.post('/api/v1/trading/configs',
            data=json.dumps({
                'name': 'Test Config',
                'trading_pair': 'XBTMYR',
                'luno_api_key': 'test_key',
                'luno_api_secret': 'test_secret',
                'strategy_type': 'basic'
            }),
            content_type='application/json',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('config', data)
        self.assertEqual(data['config']['name'], 'Test Config')
    
    def test_get_trading_configs(self):
        """Test getting trading configurations"""
        headers = self.get_auth_headers()
        response = self.client.get('/api/v1/trading/configs', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('configs', data)
    
    def test_create_trading_bot(self):
        """Test creating trading bot"""
        # First create a config
        headers = self.get_auth_headers()
        config_response = self.client.post('/api/v1/trading/configs',
            data=json.dumps({
                'name': 'Test Config',
                'trading_pair': 'XBTMYR',
                'luno_api_key': 'test_key',
                'luno_api_secret': 'test_secret'
            }),
            content_type='application/json',
            headers=headers
        )
        
        config_data = json.loads(config_response.data)
        config_id = config_data['config']['id']
        
        # Now create a bot
        response = self.client.post('/api/v1/trading/bots',
            data=json.dumps({
                'config_id': config_id,
                'name': 'Test Bot'
            }),
            content_type='application/json',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('bot', data)
        self.assertEqual(data['bot']['name'], 'Test Bot')


class AdminTestCase(SaaSPlatformTestCase):
    """Test admin functionality"""
    
    def test_admin_dashboard_access(self):
        """Test admin dashboard access"""
        headers = self.get_auth_headers(self.admin_user)
        response = self.client.get('/api/v1/admin/dashboard', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('dashboard', data)
    
    def test_non_admin_dashboard_access(self):
        """Test non-admin user cannot access admin dashboard"""
        headers = self.get_auth_headers(self.test_user)
        response = self.client.get('/api/v1/admin/dashboard', headers=headers)
        
        self.assertEqual(response.status_code, 403)
    
    def test_admin_user_management(self):
        """Test admin user management"""
        headers = self.get_auth_headers(self.admin_user)
        response = self.client.get('/api/v1/users/', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('users', data)


class WebInterfaceTestCase(SaaSPlatformTestCase):
    """Test web interface"""
    
    def test_landing_page(self):
        """Test landing page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        """Test login page loads"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_register_page(self):
        """Test register page loads"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
    
    def test_pricing_page(self):
        """Test pricing page loads"""
        response = self.client.get('/pricing')
        self.assertEqual(response.status_code, 200)


class HealthCheckTestCase(SaaSPlatformTestCase):
    """Test health check endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_api_info_endpoint(self):
        """Test API info endpoint"""
        response = self.client.get('/api/info')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('name', data)
        self.assertIn('version', data)


def run_tests():
    """Run all tests"""
    print("🧪 Running SaaS Platform Test Suite...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [
        AuthenticationTestCase,
        SubscriptionTestCase,
        TradingTestCase,
        AdminTestCase,
        WebInterfaceTestCase,
        HealthCheckTestCase
    ]
    
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n✅ All tests passed!")
        return True
    else:
        print(f"\n❌ Some tests failed!")
        return False


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
