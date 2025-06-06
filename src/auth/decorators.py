"""
Authentication and Authorization Decorators
"""

from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import logging

from src.models.user import User
from src.auth.auth_manager import AuthManager

logger = logging.getLogger(__name__)


def login_required(f):
    """Decorator to require user authentication"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            current_user = AuthManager.get_current_user(current_user_id)
            
            if not current_user or not current_user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Store current user in Flask's g object
            g.current_user = current_user
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        try:
            if not g.current_user.is_admin:
                return jsonify({'error': 'Admin privileges required'}), 403
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Admin authorization error: {e}")
            return jsonify({'error': 'Authorization failed'}), 403
    
    return decorated_function


def subscription_required(required_plans=None):
    """Decorator to require specific subscription plans"""
    if required_plans is None:
        required_plans = ['Basic', 'Premium', 'Enterprise']
    
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            try:
                user = g.current_user
                
                if not user.subscription:
                    return jsonify({
                        'error': 'Subscription required',
                        'message': 'This feature requires a paid subscription'
                    }), 402
                
                if not user.subscription.is_active():
                    return jsonify({
                        'error': 'Subscription expired',
                        'message': 'Your subscription has expired. Please renew to continue.'
                    }), 402
                
                if user.subscription.plan.name not in required_plans:
                    return jsonify({
                        'error': 'Subscription upgrade required',
                        'message': f'This feature requires one of: {", ".join(required_plans)}',
                        'current_plan': user.subscription.plan.name,
                        'required_plans': required_plans
                    }), 402
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Subscription authorization error: {e}")
                return jsonify({'error': 'Authorization failed'}), 403
        
        return decorated_function
    return decorator


def api_key_required(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check for API key in headers
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                # Check for API key in query parameters
                api_key = request.args.get('api_key')
            
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            # Validate API key
            user, error = AuthManager.validate_api_key(api_key)
            
            if error:
                return jsonify({'error': error}), 401
            
            # Store current user in Flask's g object
            g.current_user = user
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"API key authentication error: {e}")
            return jsonify({'error': 'API authentication failed'}), 401
    
    return decorated_function


def rate_limit_required(feature_name, limit_type='api_calls_per_hour'):
    """Decorator to enforce rate limits based on subscription"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            try:
                user = g.current_user
                
                # Check if user has subscription
                if not user.subscription:
                    # Apply free tier limits
                    if limit_type == 'api_calls_per_hour' and user.api_calls_count >= 100:
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'message': 'Free tier API limit reached. Upgrade for higher limits.'
                        }), 429
                
                else:
                    # Check subscription limits
                    limit_value = user.subscription.get_feature_value(limit_type)
                    
                    if limit_value != 'unlimited':
                        current_usage = getattr(user, f'{limit_type.replace("_per_hour", "")}_count', 0)
                        
                        if current_usage >= int(limit_value):
                            return jsonify({
                                'error': 'Rate limit exceeded',
                                'message': f'Subscription limit reached for {feature_name}',
                                'limit': limit_value,
                                'current_usage': current_usage
                            }), 429
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Rate limit check error: {e}")
                return jsonify({'error': 'Rate limit check failed'}), 500
        
        return decorated_function
    return decorator


def feature_required(feature_name):
    """Decorator to require specific subscription features"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            try:
                user = g.current_user
                
                if not user.subscription:
                    return jsonify({
                        'error': 'Feature not available',
                        'message': f'{feature_name} requires a paid subscription'
                    }), 402
                
                if not user.subscription.has_feature(feature_name):
                    return jsonify({
                        'error': 'Feature not available',
                        'message': f'{feature_name} is not included in your current plan',
                        'current_plan': user.subscription.plan.name
                    }), 402
                
                feature_value = user.subscription.get_feature_value(feature_name)
                
                if feature_value == 'false':
                    return jsonify({
                        'error': 'Feature not available',
                        'message': f'{feature_name} is not enabled in your current plan'
                    }), 402
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Feature authorization error: {e}")
                return jsonify({'error': 'Feature authorization failed'}), 403
        
        return decorated_function
    return decorator


def verified_email_required(f):
    """Decorator to require verified email"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        try:
            if not g.current_user.is_verified:
                return jsonify({
                    'error': 'Email verification required',
                    'message': 'Please verify your email address to access this feature'
                }), 403
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Email verification check error: {e}")
            return jsonify({'error': 'Email verification check failed'}), 500
    
    return decorated_function
