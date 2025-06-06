"""
User Management API Endpoints
"""

from flask import Blueprint, request, jsonify, g
import logging

from src.auth.decorators import login_required, admin_required
from src.models.user import User, UserProfile
from src.models.base import db

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile"""
    try:
        user = g.current_user
        
        return jsonify({
            'user': user.to_dict(),
            'profile': user.profile.to_dict() if user.profile else None
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500


@users_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        user = g.current_user
        data = request.get_json()
        
        # Update user basic info
        user_fields = ['first_name', 'last_name']
        for field in user_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Update or create profile
        if not user.profile:
            user.profile = UserProfile(user_id=user.id)
        
        profile_fields = [
            'phone', 'timezone', 'country', 'language', 'risk_tolerance',
            'preferred_pairs', 'notification_preferences', 'theme',
            'dashboard_layout', 'marketing_emails', 'newsletter'
        ]
        
        for field in profile_fields:
            if field in data:
                setattr(user.profile, field, data[field])
        
        user.save()
        user.profile.save()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict(),
            'profile': user.profile.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500


@users_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    """Get user settings"""
    try:
        user = g.current_user
        
        settings = {
            'notifications': {
                'email': user.profile.notification_preferences if user.profile else {},
                'marketing_emails': user.profile.marketing_emails if user.profile else True,
                'newsletter': user.profile.newsletter if user.profile else True
            },
            'preferences': {
                'timezone': user.profile.timezone if user.profile else 'UTC',
                'language': user.profile.language if user.profile else 'en',
                'theme': user.profile.theme if user.profile else 'light',
                'risk_tolerance': user.profile.risk_tolerance if user.profile else 'medium'
            },
            'api': {
                'api_key': user.api_key,
                'api_calls_count': user.api_calls_count,
                'api_calls_reset_at': user.api_calls_reset_at.isoformat() if user.api_calls_reset_at else None
            }
        }
        
        return jsonify({'settings': settings}), 200
        
    except Exception as e:
        logger.error(f"Get settings error: {e}")
        return jsonify({'error': 'Failed to get settings'}), 500


@users_bp.route('/settings', methods=['PUT'])
@login_required
def update_settings():
    """Update user settings"""
    try:
        user = g.current_user
        data = request.get_json()
        
        # Ensure profile exists
        if not user.profile:
            user.profile = UserProfile(user_id=user.id)
        
        # Update notification settings
        if 'notifications' in data:
            notifications = data['notifications']
            if 'email' in notifications:
                user.profile.notification_preferences = notifications['email']
            if 'marketing_emails' in notifications:
                user.profile.marketing_emails = notifications['marketing_emails']
            if 'newsletter' in notifications:
                user.profile.newsletter = notifications['newsletter']
        
        # Update preferences
        if 'preferences' in data:
            preferences = data['preferences']
            for key in ['timezone', 'language', 'theme', 'risk_tolerance']:
                if key in preferences:
                    setattr(user.profile, key, preferences[key])
        
        user.profile.save()
        
        return jsonify({'message': 'Settings updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Update settings error: {e}")
        return jsonify({'error': 'Failed to update settings'}), 500


@users_bp.route('/dashboard-layout', methods=['GET'])
@login_required
def get_dashboard_layout():
    """Get user dashboard layout"""
    try:
        user = g.current_user
        
        layout = {}
        if user.profile and user.profile.dashboard_layout:
            layout = user.profile.dashboard_layout
        
        return jsonify({'layout': layout}), 200
        
    except Exception as e:
        logger.error(f"Get dashboard layout error: {e}")
        return jsonify({'error': 'Failed to get dashboard layout'}), 500


@users_bp.route('/dashboard-layout', methods=['PUT'])
@login_required
def update_dashboard_layout():
    """Update user dashboard layout"""
    try:
        user = g.current_user
        data = request.get_json()
        
        layout = data.get('layout', {})
        
        # Ensure profile exists
        if not user.profile:
            user.profile = UserProfile(user_id=user.id)
        
        user.profile.dashboard_layout = layout
        user.profile.save()
        
        return jsonify({'message': 'Dashboard layout updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Update dashboard layout error: {e}")
        return jsonify({'error': 'Failed to update dashboard layout'}), 500


@users_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get user statistics"""
    try:
        user = g.current_user
        
        stats = {
            'account': {
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'login_count': user.login_count,
                'is_verified': user.is_verified
            },
            'subscription': {
                'plan': user.subscription.plan.name if user.subscription else 'Free',
                'status': user.subscription.status if user.subscription else 'inactive',
                'days_remaining': user.subscription.days_remaining() if user.subscription else 0
            },
            'trading': {
                'total_bots': len(user.bots),
                'active_bots': len([bot for bot in user.bots if bot.is_active]),
                'total_trades': sum(bot.total_trades for bot in user.bots),
                'total_pnl': float(sum(bot.total_pnl for bot in user.bots))
            },
            'api': {
                'api_calls_count': user.api_calls_count,
                'api_calls_limit': user.subscription.get_feature_value('api_calls_per_hour') if user.subscription else '100'
            }
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        logger.error(f"Get user stats error: {e}")
        return jsonify({'error': 'Failed to get user stats'}), 500


@users_bp.route('/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    """Deactivate user account"""
    try:
        user = g.current_user
        data = request.get_json()
        
        # Verify password for security
        password = data.get('password')
        if not password or not user.check_password(password):
            return jsonify({'error': 'Password verification required'}), 400
        
        # Deactivate account
        from src.auth.auth_manager import AuthManager
        success, message = AuthManager.deactivate_user(user.id)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': 'Account deactivated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Account deactivation error: {e}")
        return jsonify({'error': 'Failed to deactivate account'}), 500


# Admin endpoints
@users_bp.route('/', methods=['GET'])
@admin_required
def list_users():
    """List all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                User.email.contains(search) |
                User.first_name.contains(search) |
                User.last_name.contains(search)
            )
        
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"List users error: {e}")
        return jsonify({'error': 'Failed to list users'}), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get specific user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({'error': 'Failed to get user'}), 500


@users_bp.route('/<int:user_id>/reactivate', methods=['POST'])
@admin_required
def reactivate_user(user_id):
    """Reactivate user account (admin only)"""
    try:
        from src.auth.auth_manager import AuthManager
        success, message = AuthManager.reactivate_user(user_id)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        logger.error(f"User reactivation error: {e}")
        return jsonify({'error': 'Failed to reactivate user'}), 500
