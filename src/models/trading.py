"""
Trading-related Models for Multi-tenant Support
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
import json

from .base import db, BaseModel, TenantMixin


class UserTradingConfig(BaseModel, TenantMixin):
    """User-specific trading configuration"""
    __tablename__ = 'user_trading_configs'
    
    name = db.Column(db.String(100), nullable=False)
    trading_pair = db.Column(db.String(20), nullable=False)
    
    # API Credentials (encrypted)
    luno_api_key = db.Column(db.String(255), nullable=False)
    luno_api_secret = db.Column(db.String(255), nullable=False)
    
    # Trading parameters
    max_position_size_percent = db.Column(db.Numeric(5, 2), default=2.0)
    stop_loss_percent = db.Column(db.Numeric(5, 2), default=1.5)
    take_profit_percent = db.Column(db.Numeric(5, 2), default=3.0)
    max_daily_trades = db.Column(db.Integer, default=3)
    
    # Risk management
    enable_stop_loss = db.Column(db.Boolean, default=True)
    enable_take_profit = db.Column(db.Boolean, default=True)
    max_drawdown_percent = db.Column(db.Numeric(5, 2), default=10.0)
    
    # Technical analysis settings
    rsi_period = db.Column(db.Integer, default=14)
    rsi_oversold = db.Column(db.Integer, default=30)
    rsi_overbought = db.Column(db.Integer, default=70)
    ema_short = db.Column(db.Integer, default=9)
    ema_long = db.Column(db.Integer, default=21)
    bollinger_period = db.Column(db.Integer, default=20)
    bollinger_std = db.Column(db.Numeric(3, 1), default=2.0)
    
    # Strategy settings
    strategy_type = db.Column(db.String(50), default='basic')
    strategy_config = db.Column(db.JSON)
    
    # Operation settings
    dry_run = db.Column(db.Boolean, default=True)
    check_interval = db.Column(db.Integer, default=60)
    trading_hours_start = db.Column(db.Integer, default=8)
    trading_hours_end = db.Column(db.Integer, default=22)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Status
    is_active = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="trading_configs")
    bots = relationship("UserBot", back_populates="config", cascade="all, delete-orphan")
    
    def to_dict(self, include_secrets=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'trading_pair': self.trading_pair,
            'max_position_size_percent': float(self.max_position_size_percent),
            'stop_loss_percent': float(self.stop_loss_percent),
            'take_profit_percent': float(self.take_profit_percent),
            'max_daily_trades': self.max_daily_trades,
            'enable_stop_loss': self.enable_stop_loss,
            'enable_take_profit': self.enable_take_profit,
            'max_drawdown_percent': float(self.max_drawdown_percent),
            'rsi_period': self.rsi_period,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'ema_short': self.ema_short,
            'ema_long': self.ema_long,
            'bollinger_period': self.bollinger_period,
            'bollinger_std': float(self.bollinger_std),
            'strategy_type': self.strategy_type,
            'strategy_config': self.strategy_config,
            'dry_run': self.dry_run,
            'check_interval': self.check_interval,
            'trading_hours_start': self.trading_hours_start,
            'trading_hours_end': self.trading_hours_end,
            'timezone': self.timezone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_secrets:
            data.update({
                'luno_api_key': self.luno_api_key,
                'luno_api_secret': self.luno_api_secret
            })
        
        return data


class UserBot(BaseModel, TenantMixin):
    """User trading bot instance"""
    __tablename__ = 'user_bots'
    
    config_id = db.Column(db.Integer, db.ForeignKey('user_trading_configs.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Bot status
    status = db.Column(db.String(20), default='stopped')  # stopped, running, paused, error
    is_active = db.Column(db.Boolean, default=False)
    
    # Performance tracking
    total_trades = db.Column(db.Integer, default=0)
    winning_trades = db.Column(db.Integer, default=0)
    losing_trades = db.Column(db.Integer, default=0)
    total_pnl = db.Column(db.Numeric(15, 8), default=0.0)
    
    # Runtime info
    last_heartbeat = db.Column(db.DateTime)
    last_trade_time = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Process info
    process_id = db.Column(db.String(100))
    container_id = db.Column(db.String(100))
    
    # Relationships
    user = relationship("User", back_populates="bots")
    config = relationship("UserTradingConfig", back_populates="bots")
    trades = relationship("UserTrade", back_populates="bot", cascade="all, delete-orphan")
    
    def start(self):
        """Start the bot"""
        self.status = 'running'
        self.is_active = True
        self.error_message = None
        self.save()
    
    def stop(self):
        """Stop the bot"""
        self.status = 'stopped'
        self.is_active = False
        self.save()
    
    def pause(self):
        """Pause the bot"""
        self.status = 'paused'
        self.save()
    
    def error(self, message):
        """Set bot to error state"""
        self.status = 'error'
        self.is_active = False
        self.error_message = message
        self.save()
    
    def heartbeat(self):
        """Update heartbeat"""
        self.last_heartbeat = datetime.utcnow()
        self.save()
    
    def record_trade(self, trade_data):
        """Record a trade"""
        self.total_trades += 1
        if trade_data.get('pnl', 0) > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        self.total_pnl += trade_data.get('pnl', 0)
        self.last_trade_time = datetime.utcnow()
        self.save()
    
    @property
    def win_rate(self):
        """Calculate win rate"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'config_id': self.config_id,
            'name': self.name,
            'status': self.status,
            'is_active': self.is_active,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_pnl': float(self.total_pnl),
            'win_rate': self.win_rate,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'last_trade_time': self.last_trade_time.isoformat() if self.last_trade_time else None,
            'error_message': self.error_message,
            'process_id': self.process_id,
            'container_id': self.container_id,
            'config': self.config.to_dict() if self.config else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class UserTrade(BaseModel, TenantMixin):
    """User trade record"""
    __tablename__ = 'user_trades'
    
    bot_id = db.Column(db.Integer, db.ForeignKey('user_bots.id'), nullable=False)
    trade_id = db.Column(db.String(100), nullable=False)
    
    # Trade details
    pair = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # BUY, SELL
    volume = db.Column(db.Numeric(15, 8), nullable=False)
    price = db.Column(db.Numeric(15, 8), nullable=False)
    commission = db.Column(db.Numeric(15, 8), default=0.0)
    pnl = db.Column(db.Numeric(15, 8), default=0.0)
    
    # Strategy info
    strategy = db.Column(db.String(50))
    confidence = db.Column(db.Numeric(3, 2))
    
    # Market data at time of trade
    market_data = db.Column(db.JSON)
    
    # Order info
    order_id = db.Column(db.String(100))
    order_type = db.Column(db.String(20))
    
    # Relationships
    user = relationship("User", back_populates="trades")
    bot = relationship("UserBot", back_populates="trades")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bot_id': self.bot_id,
            'trade_id': self.trade_id,
            'pair': self.pair,
            'action': self.action,
            'volume': float(self.volume),
            'price': float(self.price),
            'commission': float(self.commission),
            'pnl': float(self.pnl),
            'strategy': self.strategy,
            'confidence': float(self.confidence) if self.confidence else None,
            'market_data': self.market_data,
            'order_id': self.order_id,
            'order_type': self.order_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
