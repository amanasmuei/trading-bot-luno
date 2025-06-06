"""
Admin Panel Web Interface
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from sqlalchemy import func
import logging

from src.auth.decorators import admin_required
from src.models.user import User
from src.models.subscription import Subscription, SubscriptionPlan
from src.models.trading import UserBot, UserTrade
from src.models.billing import Invoice, Payment
from src.models.base import db

logger = logging.getLogger(__name__)

# Create blueprint
admin_panel_bp = Blueprint('admin_panel', __name__, url_prefix='/admin', template_folder='templates/admin')


@admin_panel_bp.route('/')
@admin_required
def admin_dashboard():
    """Main admin dashboard"""
    try:
        # Get dashboard statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        verified_users = User.query.filter_by(is_verified=True).count()
        
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
            'stats': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'verified': verified_users
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
                }
            },
            'recent_activity': {
                'users': recent_users,
                'payments': recent_payments
            }
        }
        
        return render_template('admin/dashboard.html', **dashboard_data)
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        flash('Error loading admin dashboard', 'error')
        return render_template('admin/dashboard.html', stats={}, recent_activity={})


@admin_panel_bp.route('/users')
@admin_required
def users_management():
    """Users management page"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                User.email.contains(search) |
                User.first_name.contains(search) |
                User.last_name.contains(search)
            )
        
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        elif status == 'verified':
            query = query.filter_by(is_verified=True)
        elif status == 'unverified':
            query = query.filter_by(is_verified=False)
        
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('admin/users.html', users=users, search=search, status=status)
        
    except Exception as e:
        logger.error(f"Users management error: {e}")
        flash('Error loading users', 'error')
        return render_template('admin/users.html', users=None)


@admin_panel_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """User detail page"""
    try:
        user = User.query.get_or_404(user_id)
        
        return render_template('admin/user_detail.html', user=user)
        
    except Exception as e:
        logger.error(f"User detail error: {e}")
        flash('Error loading user details', 'error')
        return redirect(url_for('admin_panel.users_management'))


@admin_panel_bp.route('/subscriptions')
@admin_required
def subscriptions_management():
    """Subscriptions management page"""
    try:
        page = request.args.get('page', 1, type=int)
        plan_filter = request.args.get('plan', '')
        status_filter = request.args.get('status', '')
        
        query = Subscription.query.join(User).join(SubscriptionPlan)
        
        if plan_filter:
            query = query.filter(SubscriptionPlan.name == plan_filter)
        
        if status_filter:
            query = query.filter(Subscription.status == status_filter)
        
        subscriptions = query.order_by(Subscription.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        plans = SubscriptionPlan.query.all()
        
        return render_template('admin/subscriptions.html', 
                             subscriptions=subscriptions, 
                             plans=plans, 
                             plan_filter=plan_filter, 
                             status_filter=status_filter)
        
    except Exception as e:
        logger.error(f"Subscriptions management error: {e}")
        flash('Error loading subscriptions', 'error')
        return render_template('admin/subscriptions.html', subscriptions=None, plans=[])


@admin_panel_bp.route('/plans')
@admin_required
def plans_management():
    """Subscription plans management page"""
    try:
        plans = SubscriptionPlan.query.order_by(SubscriptionPlan.price).all()
        
        return render_template('admin/plans.html', plans=plans)
        
    except Exception as e:
        logger.error(f"Plans management error: {e}")
        flash('Error loading plans', 'error')
        return render_template('admin/plans.html', plans=[])


@admin_panel_bp.route('/bots')
@admin_required
def bots_management():
    """Trading bots management page"""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        user_filter = request.args.get('user', '')
        
        query = UserBot.query.join(User)
        
        if status_filter:
            query = query.filter(UserBot.status == status_filter)
        
        if user_filter:
            query = query.filter(User.email.contains(user_filter))
        
        bots = query.order_by(UserBot.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('admin/bots.html', 
                             bots=bots, 
                             status_filter=status_filter, 
                             user_filter=user_filter)
        
    except Exception as e:
        logger.error(f"Bots management error: {e}")
        flash('Error loading bots', 'error')
        return render_template('admin/bots.html', bots=None)


@admin_panel_bp.route('/billing')
@admin_required
def billing_management():
    """Billing management page"""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        
        # Invoices
        invoice_query = Invoice.query.join(User)
        if status_filter:
            invoice_query = invoice_query.filter(Invoice.status == status_filter)
        
        invoices = invoice_query.order_by(Invoice.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        # Payments
        payment_query = Payment.query.join(User)
        if status_filter:
            payment_query = payment_query.filter(Payment.status == status_filter)
        
        payments = payment_query.order_by(Payment.created_at.desc()).limit(10).all()
        
        return render_template('admin/billing.html', 
                             invoices=invoices, 
                             payments=payments, 
                             status_filter=status_filter)
        
    except Exception as e:
        logger.error(f"Billing management error: {e}")
        flash('Error loading billing data', 'error')
        return render_template('admin/billing.html', invoices=None, payments=[])


@admin_panel_bp.route('/analytics')
@admin_required
def analytics():
    """Analytics and reports page"""
    try:
        # User growth over time
        user_growth = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).group_by(func.date(User.created_at)).order_by('date').limit(30).all()
        
        # Revenue over time
        revenue_data = db.session.query(
            func.date(Payment.created_at).label('date'),
            func.sum(Payment.amount).label('total')
        ).filter_by(status='completed').group_by(
            func.date(Payment.created_at)
        ).order_by('date').limit(30).all()
        
        # Trading activity
        trading_activity = db.session.query(
            func.date(UserTrade.created_at).label('date'),
            func.count(UserTrade.id).label('count')
        ).group_by(func.date(UserTrade.created_at)).order_by('date').limit(30).all()
        
        analytics_data = {
            'user_growth': [
                {'date': stat[0].isoformat(), 'count': stat[1]} 
                for stat in user_growth
            ],
            'revenue': [
                {'date': stat[0].isoformat(), 'total': float(stat[1])} 
                for stat in revenue_data
            ],
            'trading_activity': [
                {'date': stat[0].isoformat(), 'count': stat[1]} 
                for stat in trading_activity
            ]
        }
        
        return render_template('admin/analytics.html', analytics=analytics_data)
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        flash('Error loading analytics', 'error')
        return render_template('admin/analytics.html', analytics={})


@admin_panel_bp.route('/settings')
@admin_required
def admin_settings():
    """Admin settings page"""
    try:
        # TODO: Implement admin settings storage
        settings = {
            'maintenance_mode': False,
            'new_registrations_enabled': True,
            'max_free_bots': 1,
            'max_free_pairs': 1,
            'default_api_rate_limit': 100
        }
        
        return render_template('admin/settings.html', settings=settings)
        
    except Exception as e:
        logger.error(f"Admin settings error: {e}")
        flash('Error loading settings', 'error')
        return render_template('admin/settings.html', settings={})


# AJAX endpoints for admin functionality
@admin_panel_bp.route('/api/user/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.is_admin:
            return jsonify({'success': False, 'error': 'Cannot modify admin user'})
        
        user.is_active = not user.is_active
        user.save()
        
        # Stop user bots if deactivating
        if not user.is_active:
            for bot in user.bots:
                if bot.is_active:
                    bot.stop()
        
        return jsonify({
            'success': True, 
            'message': f'User {"activated" if user.is_active else "deactivated"}',
            'is_active': user.is_active
        })
        
    except Exception as e:
        logger.error(f"Toggle user status error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@admin_panel_bp.route('/api/bot/<int:bot_id>/force-stop', methods=['POST'])
@admin_required
def force_stop_bot(bot_id):
    """Force stop a trading bot"""
    try:
        bot = UserBot.query.get_or_404(bot_id)
        
        # TODO: Implement actual bot stopping logic
        bot.stop()
        
        return jsonify({
            'success': True,
            'message': 'Bot stopped successfully'
        })
        
    except Exception as e:
        logger.error(f"Force stop bot error: {e}")
        return jsonify({'success': False, 'error': str(e)})
