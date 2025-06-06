"""
Authentication API Endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from src.auth.auth_manager import AuthManager
from src.auth.decorators import login_required
from src.models.user import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Register user
        user, error = AuthManager.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            timezone=data.get('timezone', 'UTC'),
            country=data.get('country'),
            language=data.get('language', 'en')
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        # Generate tokens
        access_token, refresh_token, token_error = AuthManager.generate_tokens(user)
        
        if token_error:
            return jsonify({'error': token_error}), 500
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'email_verification_required': not user.is_verified
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Authenticate user
        user, error = AuthManager.authenticate_user(email, password)
        
        if error:
            return jsonify({'error': error}), 401
        
        # Generate tokens
        access_token, refresh_token, token_error = AuthManager.generate_tokens(user)
        
        if token_error:
            return jsonify({'error': token_error}), 500
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        access_token, error = AuthManager.refresh_access_token()
        
        if error:
            return jsonify({'error': error}), 401
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Token refresh failed'}), 500


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Verification token is required'}), 400
        
        success, message = AuthManager.verify_email(token)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        return jsonify({'error': 'Email verification failed'}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        success, message = AuthManager.request_password_reset(email)
        
        # Always return success to prevent email enumeration
        return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        return jsonify({'error': 'Password reset request failed'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        success, message = AuthManager.reset_password(token, new_password)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({'error': 'Password reset failed'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        from flask import g
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        success, message = AuthManager.change_password(
            g.current_user.id, current_password, new_password
        )
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        logger.error(f"Password change error: {e}")
        return jsonify({'error': 'Password change failed'}), 500


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        from flask import g
        return jsonify({
            'user': g.current_user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({'error': 'Failed to get user information'}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user (client-side token removal)"""
    try:
        # In a JWT-based system, logout is typically handled client-side
        # by removing the tokens. Server-side token blacklisting could be
        # implemented here if needed.
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500


@auth_bp.route('/api-key/regenerate', methods=['POST'])
@login_required
def regenerate_api_key():
    """Regenerate user API credentials"""
    try:
        from flask import g
        user = g.current_user
        user.regenerate_api_credentials()
        
        return jsonify({
            'message': 'API credentials regenerated successfully',
            'api_key': user.api_key
        }), 200
        
    except Exception as e:
        logger.error(f"API key regeneration error: {e}")
        return jsonify({'error': 'API key regeneration failed'}), 500


@auth_bp.route('/api-key', methods=['GET'])
@login_required
def get_api_key():
    """Get user API key"""
    try:
        from flask import g
        user = g.current_user
        
        return jsonify({
            'api_key': user.api_key,
            'api_calls_count': user.api_calls_count,
            'api_calls_reset_at': user.api_calls_reset_at.isoformat() if user.api_calls_reset_at else None
        }), 200
        
    except Exception as e:
        logger.error(f"Get API key error: {e}")
        return jsonify({'error': 'Failed to get API key'}), 500
