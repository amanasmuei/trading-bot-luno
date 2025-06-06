"""
SaaS Platform Web Dashboard
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import logging

from src.auth.decorators import login_required
from src.models.user import User
from src.models.subscription import SubscriptionPlan
from src.models.trading import UserBot, UserTradingConfig
from src.models.base import db

logger = logging.getLogger(__name__)

# Create blueprint
saas_dashboard_bp = Blueprint('saas_dashboard', __name__, url_prefix='/', template_folder='templates/saas')


@saas_dashboard_bp.route('/')
def landing_page():
    """Landing page for the SaaS platform"""
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    return render_template('landing.html', plans=plans)


@saas_dashboard_bp.route('/pricing')
def pricing():
    """Pricing page"""
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    return render_template('pricing.html', plans=plans)


@saas_dashboard_bp.route('/features')
def features():
    """Features page"""
    return render_template('features.html')


@saas_dashboard_bp.route('/docs')
def documentation():
    """API documentation page"""
    return render_template('docs.html')


@saas_dashboard_bp.route('/login')
def login_page():
    """Login page"""
    return render_template('auth/login.html')


@saas_dashboard_bp.route('/register')
def register_page():
    """Registration page"""
    return render_template('auth/register.html')


@saas_dashboard_bp.route('/forgot-password')
def forgot_password_page():
    """Forgot password page"""
    return render_template('auth/forgot_password.html')


@saas_dashboard_bp.route('/reset-password')
def reset_password_page():
    """Reset password page"""
    token = request.args.get('token')
    return render_template('auth/reset_password.html', token=token)


@saas_dashboard_bp.route('/verify-email')
def verify_email_page():
    """Email verification page"""
    token = request.args.get('token')
    return render_template('auth/verify_email.html', token=token)


@saas_dashboard_bp.route('/dashboard')
@login_required
def user_dashboard():
    """Main user dashboard"""
    try:
        # Get current user from JWT token
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return redirect(url_for('saas_dashboard.login_page'))
        
        # Get user statistics
        total_bots = len(user.bots)
        active_bots = len([bot for bot in user.bots if bot.is_active])
        total_trades = sum(bot.total_trades for bot in user.bots)
        total_pnl = sum(bot.total_pnl for bot in user.bots)
        
        # Get recent trades
        recent_trades = []
        for bot in user.bots:
            recent_trades.extend(bot.trades[-5:])  # Last 5 trades per bot
        recent_trades.sort(key=lambda x: x.created_at, reverse=True)
        recent_trades = recent_trades[:10]  # Top 10 most recent
        
        dashboard_data = {
            'user': user,
            'stats': {
                'total_bots': total_bots,
                'active_bots': active_bots,
                'total_trades': total_trades,
                'total_pnl': float(total_pnl),
                'subscription_plan': user.subscription.plan.name if user.subscription else 'Free',
                'subscription_status': user.subscription.status if user.subscription else 'inactive'
            },
            'recent_trades': recent_trades,
            'bots': user.bots
        }
        
        return render_template('dashboard/main.html', **dashboard_data)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('saas_dashboard.login_page'))


@saas_dashboard_bp.route('/dashboard/bots')
@login_required
def bots_page():
    """Trading bots management page"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        return render_template('dashboard/bots.html', user=user, bots=user.bots)
        
    except Exception as e:
        logger.error(f"Bots page error: {e}")
        flash('Error loading bots page', 'error')
        return redirect(url_for('saas_dashboard.user_dashboard'))


@saas_dashboard_bp.route('/dashboard/configs')
@login_required
def configs_page():
    """Trading configurations page"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        return render_template('dashboard/configs.html', user=user, configs=user.trading_configs)
        
    except Exception as e:
        logger.error(f"Configs page error: {e}")
        flash('Error loading configs page', 'error')
        return redirect(url_for('saas_dashboard.user_dashboard'))


@saas_dashboard_bp.route('/dashboard/trades')
@login_required
def trades_page():
    """Trading history page"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Get all trades for user
        all_trades = []
        for bot in user.bots:
            all_trades.extend(bot.trades)
        
        # Sort by date
        all_trades.sort(key=lambda x: x.created_at, reverse=True)
        
        return render_template('dashboard/trades.html', user=user, trades=all_trades)
        
    except Exception as e:
        logger.error(f"Trades page error: {e}")
        flash('Error loading trades page', 'error')
        return redirect(url_for('saas_dashboard.user_dashboard'))


@saas_dashboard_bp.route('/dashboard/subscription')
@login_required
def subscription_page():
    """Subscription management page"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()
        
        return render_template('dashboard/subscription.html', user=user, plans=plans)
        
    except Exception as e:
        logger.error(f"Subscription page error: {e}")
        flash('Error loading subscription page', 'error')
        return redirect(url_for('saas_dashboard.user_dashboard'))


@saas_dashboard_bp.route('/dashboard/billing')
@login_required
def billing_page():
    """Billing and invoices page"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        return render_template('dashboard/billing.html', user=user, invoices=user.invoices, payments=user.payments)
        
    except Exception as e:
        logger.error(f"Billing page error: {e}")
        flash('Error loading billing page', 'error')
        return redirect(url_for('saas_dashboard.user_dashboard'))


@saas_dashboard_bp.route('/dashboard/settings')
@login_required
def settings_page():
    """User settings page"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        return render_template('dashboard/settings.html', user=user)
        
    except Exception as e:
        logger.error(f"Settings page error: {e}")
        flash('Error loading settings page', 'error')
        return redirect(url_for('saas_dashboard.user_dashboard'))


@saas_dashboard_bp.route('/dashboard/api-keys')
@login_required
def api_keys_page():
    """API keys management page"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        return render_template('dashboard/api_keys.html', user=user)
        
    except Exception as e:
        logger.error(f"API keys page error: {e}")
        flash('Error loading API keys page', 'error')
        return redirect(url_for('saas_dashboard.user_dashboard'))


# AJAX endpoints for dashboard functionality
@saas_dashboard_bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        stats = {
            'total_bots': len(user.bots),
            'active_bots': len([bot for bot in user.bots if bot.is_active]),
            'total_trades': sum(bot.total_trades for bot in user.bots),
            'total_pnl': float(sum(bot.total_pnl for bot in user.bots)),
            'api_calls_count': user.api_calls_count,
            'api_calls_limit': user.subscription.get_feature_value('api_calls_per_hour') if user.subscription else '100'
        }
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@saas_dashboard_bp.route('/api/dashboard/bot-status/<int:bot_id>')
@login_required
def bot_status(bot_id):
    """Get bot status"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        bot = next((b for b in user.bots if b.id == bot_id), None)
        if not bot:
            return jsonify({'success': False, 'error': 'Bot not found'})
        
        return jsonify({'success': True, 'bot': bot.to_dict()})
        
    except Exception as e:
        logger.error(f"Bot status error: {e}")
        return jsonify({'success': False, 'error': str(e)})


# Error handlers
@saas_dashboard_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404


@saas_dashboard_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500
