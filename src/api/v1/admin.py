"""
Admin API Endpoints
"""

from flask import Blueprint, request, jsonify, g
from sqlalchemy import func
import logging

from src.auth.decorators import admin_required
from src.models.user import User
from src.models.subscription import Subscription, SubscriptionPlan
from src.models.trading import UserBot, UserTrade
from src.models.billing import Invoice, Payment
from src.models.base import db

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        verified_users = User.query.filter_by(is_verified=True).count()
        new_users_today = User.query.filter(
            func.date(User.created_at) == func.current_date()
        ).count()
        
        # Subscription statistics
        subscription_stats = db.session.query(
            SubscriptionPlan.name,
            func.count(Subscription.id).label('count')
        ).join(Subscription).group_by(SubscriptionPlan.name).all()
        
        # Trading statistics
        total_bots = UserBot.query.count()
        active_bots = UserBot.query.filter_by(is_active=True).count()
        total_trades = UserTrade.query.count()
        
        # Revenue statistics
        total_revenue = db.session.query(
            func.sum(Payment.amount)
        ).filter_by(status='completed').scalar() or 0
        
        monthly_revenue = db.session.query(
            func.sum(Payment.amount)
        ).filter(
            Payment.status == 'completed',
            func.extract('month', Payment.created_at) == func.extract('month', func.current_date()),
            func.extract('year', Payment.created_at) == func.extract('year', func.current_date())
        ).scalar() or 0
        
        # Recent activity
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()
        
        dashboard_data = {
            'users': {
                'total': total_users,
                'active': active_users,
                'verified': verified_users,
                'new_today': new_users_today
            },
            'subscriptions': {
                'by_plan': [{'plan': stat[0], 'count': stat[1]} for stat in subscription_stats]
            },
            'trading': {
                'total_bots': total_bots,
                'active_bots': active_bots,
                'total_trades': total_trades
            },
            'revenue': {
                'total': float(total_revenue),
                'monthly': float(monthly_revenue)
            },
            'recent_activity': {
                'users': [user.to_dict() for user in recent_users],
                'payments': [payment.to_dict() for payment in recent_payments]
            }
        }
        
        return jsonify({'dashboard': dashboard_data}), 200
        
    except Exception as e:
        logger.error(f"Get admin dashboard error: {e}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500


@admin_bp.route('/users/stats', methods=['GET'])
@admin_required
def get_user_stats():
    """Get detailed user statistics"""
    try:
        # User registration over time
        user_registrations = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).group_by(func.date(User.created_at)).order_by('date').limit(30).all()
        
        # User activity
        login_stats = db.session.query(
            func.date(User.last_login).label('date'),
            func.count(User.id).label('count')
        ).filter(User.last_login.isnot(None)).group_by(
            func.date(User.last_login)
        ).order_by('date').limit(30).all()
        
        stats = {
            'registrations': [
                {'date': stat[0].isoformat(), 'count': stat[1]} 
                for stat in user_registrations
            ],
            'logins': [
                {'date': stat[0].isoformat(), 'count': stat[1]} 
                for stat in login_stats
            ]
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        logger.error(f"Get user stats error: {e}")
        return jsonify({'error': 'Failed to get user stats'}), 500


@admin_bp.route('/revenue/stats', methods=['GET'])
@admin_required
def get_revenue_stats():
    """Get revenue statistics"""
    try:
        # Monthly revenue
        monthly_revenue = db.session.query(
            func.extract('year', Payment.created_at).label('year'),
            func.extract('month', Payment.created_at).label('month'),
            func.sum(Payment.amount).label('total')
        ).filter_by(status='completed').group_by(
            func.extract('year', Payment.created_at),
            func.extract('month', Payment.created_at)
        ).order_by('year', 'month').limit(12).all()
        
        # Revenue by plan
        plan_revenue = db.session.query(
            SubscriptionPlan.name,
            func.sum(Payment.amount).label('total')
        ).join(Invoice).join(Payment).filter(
            Payment.status == 'completed'
        ).group_by(SubscriptionPlan.name).all()
        
        stats = {
            'monthly': [
                {
                    'year': int(stat[0]),
                    'month': int(stat[1]),
                    'total': float(stat[2])
                } for stat in monthly_revenue
            ],
            'by_plan': [
                {'plan': stat[0], 'total': float(stat[1])} 
                for stat in plan_revenue
            ]
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        logger.error(f"Get revenue stats error: {e}")
        return jsonify({'error': 'Failed to get revenue stats'}), 500


@admin_bp.route('/system/health', methods=['GET'])
@admin_required
def get_system_health():
    """Get system health status"""
    try:
        # Database health
        try:
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception:
            db_status = 'unhealthy'
        
        # Bot health
        total_bots = UserBot.query.count()
        active_bots = UserBot.query.filter_by(is_active=True).count()
        error_bots = UserBot.query.filter_by(status='error').count()
        
        # Recent errors
        recent_error_bots = UserBot.query.filter_by(status='error').order_by(
            UserBot.updated_at.desc()
        ).limit(10).all()
        
        health_data = {
            'database': {
                'status': db_status
            },
            'bots': {
                'total': total_bots,
                'active': active_bots,
                'errors': error_bots,
                'recent_errors': [
                    {
                        'id': bot.id,
                        'name': bot.name,
                        'error': bot.error_message,
                        'updated_at': bot.updated_at.isoformat()
                    } for bot in recent_error_bots
                ]
            }
        }
        
        return jsonify({'health': health_data}), 200
        
    except Exception as e:
        logger.error(f"Get system health error: {e}")
        return jsonify({'error': 'Failed to get system health'}), 500


@admin_bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@admin_required
def suspend_user(user_id):
    """Suspend user account"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.is_admin:
            return jsonify({'error': 'Cannot suspend admin user'}), 400
        
        user.is_active = False
        user.save()
        
        # Stop all user bots
        for bot in user.bots:
            if bot.is_active:
                bot.stop()
        
        # Suspend subscription
        if user.subscription:
            user.subscription.suspend()
        
        return jsonify({'message': 'User suspended successfully'}), 200
        
    except Exception as e:
        logger.error(f"Suspend user error: {e}")
        return jsonify({'error': 'Failed to suspend user'}), 500


@admin_bp.route('/users/<int:user_id>/unsuspend', methods=['POST'])
@admin_required
def unsuspend_user(user_id):
    """Unsuspend user account"""
    try:
        user = User.query.get_or_404(user_id)
        
        user.is_active = True
        user.save()
        
        # Reactivate subscription
        if user.subscription:
            user.subscription.reactivate()
        
        return jsonify({'message': 'User unsuspended successfully'}), 200
        
    except Exception as e:
        logger.error(f"Unsuspend user error: {e}")
        return jsonify({'error': 'Failed to unsuspend user'}), 500


@admin_bp.route('/bots/<int:bot_id>/force-stop', methods=['POST'])
@admin_required
def force_stop_bot(bot_id):
    """Force stop a trading bot"""
    try:
        bot = UserBot.query.get_or_404(bot_id)
        
        # TODO: Implement actual bot stopping logic
        bot.stop()
        
        return jsonify({
            'message': 'Bot stopped successfully',
            'bot': bot.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Force stop bot error: {e}")
        return jsonify({'error': 'Failed to stop bot'}), 500


@admin_bp.route('/settings', methods=['GET'])
@admin_required
def get_admin_settings():
    """Get admin settings"""
    try:
        # TODO: Implement admin settings storage
        settings = {
            'maintenance_mode': False,
            'new_registrations_enabled': True,
            'max_free_bots': 1,
            'max_free_pairs': 1,
            'default_api_rate_limit': 100
        }
        
        return jsonify({'settings': settings}), 200
        
    except Exception as e:
        logger.error(f"Get admin settings error: {e}")
        return jsonify({'error': 'Failed to get settings'}), 500


@admin_bp.route('/settings', methods=['PUT'])
@admin_required
def update_admin_settings():
    """Update admin settings"""
    try:
        data = request.get_json()
        
        # TODO: Implement admin settings storage
        # For now, just return success
        
        return jsonify({'message': 'Settings updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Update admin settings error: {e}")
        return jsonify({'error': 'Failed to update settings'}), 500
