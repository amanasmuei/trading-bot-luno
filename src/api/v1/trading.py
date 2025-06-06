"""
Trading API Endpoints
"""

from flask import Blueprint, request, jsonify, g
import logging

from src.auth.decorators import login_required, subscription_required, feature_required
from src.models.trading import UserTradingConfig, UserBot, UserTrade
from src.models.base import db

logger = logging.getLogger(__name__)

trading_bp = Blueprint('trading', __name__, url_prefix='/trading')


@trading_bp.route('/configs', methods=['GET'])
@login_required
def get_trading_configs():
    """Get user trading configurations"""
    try:
        user = g.current_user
        configs = UserTradingConfig.get_for_user(user.id).all()
        
        return jsonify({
            'configs': [config.to_dict() for config in configs]
        }), 200
        
    except Exception as e:
        logger.error(f"Get trading configs error: {e}")
        return jsonify({'error': 'Failed to get trading configs'}), 500


@trading_bp.route('/configs', methods=['POST'])
@login_required
def create_trading_config():
    """Create new trading configuration"""
    try:
        user = g.current_user
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'trading_pair', 'luno_api_key', 'luno_api_secret']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user can create more configs based on subscription
        if user.subscription:
            max_pairs = user.subscription.get_feature_value('max_pairs')
            if max_pairs != 'unlimited':
                current_pairs = len(set(config.trading_pair for config in user.trading_configs))
                if current_pairs >= int(max_pairs):
                    return jsonify({
                        'error': 'Trading pair limit reached',
                        'message': f'Your plan allows maximum {max_pairs} trading pairs'
                    }), 402
        
        # Create configuration
        config = UserTradingConfig(
            user_id=user.id,
            name=data['name'],
            trading_pair=data['trading_pair'],
            luno_api_key=data['luno_api_key'],
            luno_api_secret=data['luno_api_secret'],
            max_position_size_percent=data.get('max_position_size_percent', 2.0),
            stop_loss_percent=data.get('stop_loss_percent', 1.5),
            take_profit_percent=data.get('take_profit_percent', 3.0),
            max_daily_trades=data.get('max_daily_trades', 3),
            enable_stop_loss=data.get('enable_stop_loss', True),
            enable_take_profit=data.get('enable_take_profit', True),
            max_drawdown_percent=data.get('max_drawdown_percent', 10.0),
            rsi_period=data.get('rsi_period', 14),
            rsi_oversold=data.get('rsi_oversold', 30),
            rsi_overbought=data.get('rsi_overbought', 70),
            ema_short=data.get('ema_short', 9),
            ema_long=data.get('ema_long', 21),
            bollinger_period=data.get('bollinger_period', 20),
            bollinger_std=data.get('bollinger_std', 2.0),
            strategy_type=data.get('strategy_type', 'basic'),
            strategy_config=data.get('strategy_config', {}),
            dry_run=data.get('dry_run', True),
            check_interval=data.get('check_interval', 60),
            trading_hours_start=data.get('trading_hours_start', 8),
            trading_hours_end=data.get('trading_hours_end', 22),
            timezone=data.get('timezone', 'UTC')
        )
        config.save()
        
        return jsonify({
            'message': 'Trading configuration created successfully',
            'config': config.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create trading config error: {e}")
        return jsonify({'error': 'Failed to create trading config'}), 500


@trading_bp.route('/configs/<int:config_id>', methods=['GET'])
@login_required
def get_trading_config(config_id):
    """Get specific trading configuration"""
    try:
        user = g.current_user
        config = UserTradingConfig.get_for_user(user.id, id=config_id).first()
        
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        return jsonify({
            'config': config.to_dict(include_secrets=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Get trading config error: {e}")
        return jsonify({'error': 'Failed to get trading config'}), 500


@trading_bp.route('/configs/<int:config_id>', methods=['PUT'])
@login_required
def update_trading_config(config_id):
    """Update trading configuration"""
    try:
        user = g.current_user
        config = UserTradingConfig.get_for_user(user.id, id=config_id).first()
        
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        data = request.get_json()
        
        # Update configuration fields
        updatable_fields = [
            'name', 'trading_pair', 'luno_api_key', 'luno_api_secret',
            'max_position_size_percent', 'stop_loss_percent', 'take_profit_percent',
            'max_daily_trades', 'enable_stop_loss', 'enable_take_profit',
            'max_drawdown_percent', 'rsi_period', 'rsi_oversold', 'rsi_overbought',
            'ema_short', 'ema_long', 'bollinger_period', 'bollinger_std',
            'strategy_type', 'strategy_config', 'dry_run', 'check_interval',
            'trading_hours_start', 'trading_hours_end', 'timezone'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(config, field, data[field])
        
        config.save()
        
        return jsonify({
            'message': 'Trading configuration updated successfully',
            'config': config.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update trading config error: {e}")
        return jsonify({'error': 'Failed to update trading config'}), 500


@trading_bp.route('/configs/<int:config_id>', methods=['DELETE'])
@login_required
def delete_trading_config(config_id):
    """Delete trading configuration"""
    try:
        user = g.current_user
        config = UserTradingConfig.get_for_user(user.id, id=config_id).first()
        
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Stop all bots using this config
        for bot in config.bots:
            if bot.is_active:
                bot.stop()
        
        config.delete()
        
        return jsonify({'message': 'Trading configuration deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete trading config error: {e}")
        return jsonify({'error': 'Failed to delete trading config'}), 500


@trading_bp.route('/bots', methods=['GET'])
@login_required
def get_bots():
    """Get user trading bots"""
    try:
        user = g.current_user
        bots = UserBot.get_for_user(user.id).all()
        
        return jsonify({
            'bots': [bot.to_dict() for bot in bots]
        }), 200
        
    except Exception as e:
        logger.error(f"Get bots error: {e}")
        return jsonify({'error': 'Failed to get bots'}), 500


@trading_bp.route('/bots', methods=['POST'])
@login_required
def create_bot():
    """Create new trading bot"""
    try:
        user = g.current_user
        data = request.get_json()
        
        config_id = data.get('config_id')
        name = data.get('name')
        
        if not config_id or not name:
            return jsonify({'error': 'config_id and name are required'}), 400
        
        # Verify config belongs to user
        config = UserTradingConfig.get_for_user(user.id, id=config_id).first()
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Check if user can create more bots based on subscription
        if user.subscription and not user.subscription.can_create_bot():
            max_bots = user.subscription.get_feature_value('max_bots')
            return jsonify({
                'error': 'Bot limit reached',
                'message': f'Your plan allows maximum {max_bots} trading bots'
            }), 402
        
        # Create bot
        bot = UserBot(
            user_id=user.id,
            config_id=config_id,
            name=name
        )
        bot.save()
        
        # Update subscription bot count
        if user.subscription:
            user.subscription.increment_bot_count()
        
        return jsonify({
            'message': 'Trading bot created successfully',
            'bot': bot.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create bot error: {e}")
        return jsonify({'error': 'Failed to create bot'}), 500


@trading_bp.route('/bots/<int:bot_id>/start', methods=['POST'])
@login_required
def start_bot(bot_id):
    """Start trading bot"""
    try:
        user = g.current_user
        bot = UserBot.get_for_user(user.id, id=bot_id).first()
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        if bot.is_active:
            return jsonify({'error': 'Bot is already running'}), 400
        
        # TODO: Implement actual bot starting logic
        # This would involve spawning a new process or container
        bot.start()
        
        return jsonify({
            'message': 'Bot started successfully',
            'bot': bot.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Start bot error: {e}")
        return jsonify({'error': 'Failed to start bot'}), 500


@trading_bp.route('/bots/<int:bot_id>/stop', methods=['POST'])
@login_required
def stop_bot(bot_id):
    """Stop trading bot"""
    try:
        user = g.current_user
        bot = UserBot.get_for_user(user.id, id=bot_id).first()
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        if not bot.is_active:
            return jsonify({'error': 'Bot is not running'}), 400
        
        # TODO: Implement actual bot stopping logic
        bot.stop()
        
        return jsonify({
            'message': 'Bot stopped successfully',
            'bot': bot.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Stop bot error: {e}")
        return jsonify({'error': 'Failed to stop bot'}), 500


@trading_bp.route('/bots/<int:bot_id>', methods=['DELETE'])
@login_required
def delete_bot(bot_id):
    """Delete trading bot"""
    try:
        user = g.current_user
        bot = UserBot.get_for_user(user.id, id=bot_id).first()
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        # Stop bot if running
        if bot.is_active:
            bot.stop()
        
        # Update subscription bot count
        if user.subscription:
            user.subscription.decrement_bot_count()
        
        bot.delete()
        
        return jsonify({'message': 'Bot deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete bot error: {e}")
        return jsonify({'error': 'Failed to delete bot'}), 500


@trading_bp.route('/trades', methods=['GET'])
@login_required
def get_trades():
    """Get user trades"""
    try:
        user = g.current_user
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        bot_id = request.args.get('bot_id', type=int)
        
        query = UserTrade.get_for_user(user.id)
        
        if bot_id:
            query = query.filter_by(bot_id=bot_id)
        
        trades = query.order_by(UserTrade.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'trades': [trade.to_dict() for trade in trades.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': trades.total,
                'pages': trades.pages,
                'has_next': trades.has_next,
                'has_prev': trades.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get trades error: {e}")
        return jsonify({'error': 'Failed to get trades'}), 500
