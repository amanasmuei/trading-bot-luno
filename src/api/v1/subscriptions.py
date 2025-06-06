"""
Subscription Management API Endpoints
"""

from flask import Blueprint, request, jsonify, g
import logging

from src.auth.decorators import login_required, admin_required
from src.models.subscription import Subscription, SubscriptionPlan, PlanFeature
from src.models.base import db

logger = logging.getLogger(__name__)

subscriptions_bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')


@subscriptions_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get all available subscription plans"""
    try:
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        logger.error(f"Get plans error: {e}")
        return jsonify({'error': 'Failed to get plans'}), 500


@subscriptions_bp.route('/current', methods=['GET'])
@login_required
def get_current_subscription():
    """Get current user subscription"""
    try:
        user = g.current_user
        
        if not user.subscription:
            # Create free subscription if none exists
            free_plan = SubscriptionPlan.query.filter_by(name='Free').first()
            if free_plan:
                subscription = Subscription(
                    user_id=user.id,
                    plan_id=free_plan.id
                )
                subscription.save()
                user.subscription = subscription
        
        return jsonify({
            'subscription': user.subscription.to_dict() if user.subscription else None
        }), 200
        
    except Exception as e:
        logger.error(f"Get current subscription error: {e}")
        return jsonify({'error': 'Failed to get subscription'}), 500


@subscriptions_bp.route('/upgrade', methods=['POST'])
@login_required
def upgrade_subscription():
    """Upgrade user subscription"""
    try:
        user = g.current_user
        data = request.get_json()
        
        plan_id = data.get('plan_id')
        if not plan_id:
            return jsonify({'error': 'Plan ID is required'}), 400
        
        # Get the new plan
        new_plan = SubscriptionPlan.query.get(plan_id)
        if not new_plan or not new_plan.is_active:
            return jsonify({'error': 'Invalid plan'}), 400
        
        # Check if user already has this plan
        if user.subscription and user.subscription.plan_id == plan_id:
            return jsonify({'error': 'Already subscribed to this plan'}), 400
        
        # For now, just update the subscription
        # In production, this would integrate with Stripe
        if user.subscription:
            user.subscription.plan_id = plan_id
            user.subscription.calculate_end_date()
            user.subscription.status = 'active'
            user.subscription.save()
        else:
            subscription = Subscription(
                user_id=user.id,
                plan_id=plan_id
            )
            subscription.save()
        
        return jsonify({
            'message': 'Subscription upgraded successfully',
            'subscription': user.subscription.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Upgrade subscription error: {e}")
        return jsonify({'error': 'Failed to upgrade subscription'}), 500


@subscriptions_bp.route('/cancel', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel user subscription"""
    try:
        user = g.current_user
        
        if not user.subscription:
            return jsonify({'error': 'No active subscription'}), 400
        
        if user.subscription.plan.name == 'Free':
            return jsonify({'error': 'Cannot cancel free plan'}), 400
        
        # Cancel subscription
        user.subscription.cancel()
        
        # Stop all user bots
        for bot in user.bots:
            if bot.is_active:
                bot.stop()
        
        return jsonify({
            'message': 'Subscription cancelled successfully',
            'subscription': user.subscription.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Cancel subscription error: {e}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500


@subscriptions_bp.route('/reactivate', methods=['POST'])
@login_required
def reactivate_subscription():
    """Reactivate cancelled subscription"""
    try:
        user = g.current_user
        
        if not user.subscription:
            return jsonify({'error': 'No subscription found'}), 400
        
        if user.subscription.status != 'cancelled':
            return jsonify({'error': 'Subscription is not cancelled'}), 400
        
        # Reactivate subscription
        user.subscription.reactivate()
        
        return jsonify({
            'message': 'Subscription reactivated successfully',
            'subscription': user.subscription.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Reactivate subscription error: {e}")
        return jsonify({'error': 'Failed to reactivate subscription'}), 500


@subscriptions_bp.route('/usage', methods=['GET'])
@login_required
def get_usage():
    """Get subscription usage statistics"""
    try:
        user = g.current_user
        
        if not user.subscription:
            return jsonify({'error': 'No subscription found'}), 400
        
        usage = {
            'bots': {
                'current': user.subscription.current_bots,
                'limit': user.subscription.get_feature_value('max_bots')
            },
            'pairs': {
                'current': user.subscription.current_pairs,
                'limit': user.subscription.get_feature_value('max_pairs')
            },
            'api_calls': {
                'current': user.api_calls_count,
                'limit': user.subscription.get_feature_value('api_calls_per_hour'),
                'reset_at': user.api_calls_reset_at.isoformat() if user.api_calls_reset_at else None
            },
            'features': {
                'backtesting': user.subscription.get_feature_value('backtesting') == 'true',
                'advanced_strategies': user.subscription.get_feature_value('advanced_strategies'),
                'notifications': user.subscription.get_feature_value('notifications'),
                'support': user.subscription.get_feature_value('support')
            }
        }
        
        return jsonify({'usage': usage}), 200
        
    except Exception as e:
        logger.error(f"Get usage error: {e}")
        return jsonify({'error': 'Failed to get usage'}), 500


# Admin endpoints
@subscriptions_bp.route('/admin/plans', methods=['POST'])
@admin_required
def create_plan():
    """Create new subscription plan (admin only)"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'price', 'billing_cycle', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if plan already exists
        existing_plan = SubscriptionPlan.query.filter_by(name=data['name']).first()
        if existing_plan:
            return jsonify({'error': 'Plan with this name already exists'}), 400
        
        # Create plan
        plan = SubscriptionPlan(
            name=data['name'],
            price=data['price'],
            billing_cycle=data['billing_cycle'],
            description=data['description'],
            max_bots=data.get('max_bots', 1),
            max_pairs=data.get('max_pairs', 1),
            api_calls_per_hour=data.get('api_calls_per_hour', 100)
        )
        plan.save()
        
        # Create features
        features = data.get('features', [])
        for feature_data in features:
            feature = PlanFeature(
                plan_id=plan.id,
                name=feature_data['name'],
                value=feature_data['value'],
                description=feature_data.get('description', '')
            )
            feature.save()
        
        return jsonify({
            'message': 'Plan created successfully',
            'plan': plan.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create plan error: {e}")
        return jsonify({'error': 'Failed to create plan'}), 500


@subscriptions_bp.route('/admin/plans/<int:plan_id>', methods=['PUT'])
@admin_required
def update_plan(plan_id):
    """Update subscription plan (admin only)"""
    try:
        plan = SubscriptionPlan.query.get_or_404(plan_id)
        data = request.get_json()
        
        # Update plan fields
        updatable_fields = ['name', 'price', 'billing_cycle', 'description', 'is_active', 'max_bots', 'max_pairs', 'api_calls_per_hour']
        for field in updatable_fields:
            if field in data:
                setattr(plan, field, data[field])
        
        plan.save()
        
        return jsonify({
            'message': 'Plan updated successfully',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update plan error: {e}")
        return jsonify({'error': 'Failed to update plan'}), 500


@subscriptions_bp.route('/admin/subscriptions', methods=['GET'])
@admin_required
def list_subscriptions():
    """List all subscriptions (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        plan_name = request.args.get('plan')
        
        query = Subscription.query
        
        if status:
            query = query.filter_by(status=status)
        
        if plan_name:
            query = query.join(SubscriptionPlan).filter(SubscriptionPlan.name == plan_name)
        
        subscriptions = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'subscriptions': [sub.to_dict() for sub in subscriptions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': subscriptions.total,
                'pages': subscriptions.pages,
                'has_next': subscriptions.has_next,
                'has_prev': subscriptions.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"List subscriptions error: {e}")
        return jsonify({'error': 'Failed to list subscriptions'}), 500
