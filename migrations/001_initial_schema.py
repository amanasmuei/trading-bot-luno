"""
Initial SaaS Platform Database Schema
Migration: 001_initial_schema
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    """Create initial database schema"""
    
    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('email_verification_token', sa.String(length=255)),
        sa.Column('password_reset_token', sa.String(length=255)),
        sa.Column('password_reset_expires', sa.DateTime()),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('login_count', sa.Integer()),
        sa.Column('api_key', sa.String(length=255)),
        sa.Column('api_secret', sa.String(length=255)),
        sa.Column('api_calls_count', sa.Integer()),
        sa.Column('api_calls_reset_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_api_key'), 'users', ['api_key'], unique=True)
    op.create_index(op.f('ix_users_email_verification_token'), 'users', ['email_verification_token'], unique=True)
    op.create_index(op.f('ix_users_password_reset_token'), 'users', ['password_reset_token'], unique=True)

    # User profiles table
    op.create_table('user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=20)),
        sa.Column('timezone', sa.String(length=50)),
        sa.Column('country', sa.String(length=100)),
        sa.Column('language', sa.String(length=10)),
        sa.Column('risk_tolerance', sa.String(length=20)),
        sa.Column('preferred_pairs', sa.Text()),
        sa.Column('notification_preferences', sa.Text()),
        sa.Column('theme', sa.String(length=20)),
        sa.Column('dashboard_layout', sa.Text()),
        sa.Column('marketing_emails', sa.Boolean()),
        sa.Column('newsletter', sa.Boolean()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Subscription plans table
    op.create_table('subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('billing_cycle', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean()),
        sa.Column('max_bots', sa.Integer()),
        sa.Column('max_pairs', sa.Integer()),
        sa.Column('api_calls_per_hour', sa.Integer()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Plan features table
    op.create_table('plan_features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20)),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('next_billing_date', sa.DateTime()),
        sa.Column('cancelled_at', sa.DateTime()),
        sa.Column('stripe_subscription_id', sa.String(length=255)),
        sa.Column('stripe_customer_id', sa.String(length=255)),
        sa.Column('current_bots', sa.Integer()),
        sa.Column('current_pairs', sa.Integer()),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )

    # Trading configurations table
    op.create_table('user_trading_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('trading_pair', sa.String(length=20), nullable=False),
        sa.Column('luno_api_key', sa.String(length=255), nullable=False),
        sa.Column('luno_api_secret', sa.String(length=255), nullable=False),
        sa.Column('max_position_size_percent', sa.Numeric(precision=5, scale=2)),
        sa.Column('stop_loss_percent', sa.Numeric(precision=5, scale=2)),
        sa.Column('take_profit_percent', sa.Numeric(precision=5, scale=2)),
        sa.Column('max_daily_trades', sa.Integer()),
        sa.Column('enable_stop_loss', sa.Boolean()),
        sa.Column('enable_take_profit', sa.Boolean()),
        sa.Column('max_drawdown_percent', sa.Numeric(precision=5, scale=2)),
        sa.Column('rsi_period', sa.Integer()),
        sa.Column('rsi_oversold', sa.Integer()),
        sa.Column('rsi_overbought', sa.Integer()),
        sa.Column('ema_short', sa.Integer()),
        sa.Column('ema_long', sa.Integer()),
        sa.Column('bollinger_period', sa.Integer()),
        sa.Column('bollinger_std', sa.Numeric(precision=3, scale=1)),
        sa.Column('strategy_type', sa.String(length=50)),
        sa.Column('strategy_config', sa.JSON()),
        sa.Column('dry_run', sa.Boolean()),
        sa.Column('check_interval', sa.Integer()),
        sa.Column('trading_hours_start', sa.Integer()),
        sa.Column('trading_hours_end', sa.Integer()),
        sa.Column('timezone', sa.String(length=50)),
        sa.Column('is_active', sa.Boolean()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_trading_configs_user_id'), 'user_trading_configs', ['user_id'])

    # Trading bots table
    op.create_table('user_bots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20)),
        sa.Column('is_active', sa.Boolean()),
        sa.Column('total_trades', sa.Integer()),
        sa.Column('winning_trades', sa.Integer()),
        sa.Column('losing_trades', sa.Integer()),
        sa.Column('total_pnl', sa.Numeric(precision=15, scale=8)),
        sa.Column('last_heartbeat', sa.DateTime()),
        sa.Column('last_trade_time', sa.DateTime()),
        sa.Column('error_message', sa.Text()),
        sa.Column('process_id', sa.String(length=100)),
        sa.Column('container_id', sa.String(length=100)),
        sa.ForeignKeyConstraint(['config_id'], ['user_trading_configs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_bots_user_id'), 'user_bots', ['user_id'])

    # Trading history table
    op.create_table('user_trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bot_id', sa.Integer(), nullable=False),
        sa.Column('trade_id', sa.String(length=100), nullable=False),
        sa.Column('pair', sa.String(length=20), nullable=False),
        sa.Column('action', sa.String(length=10), nullable=False),
        sa.Column('volume', sa.Numeric(precision=15, scale=8), nullable=False),
        sa.Column('price', sa.Numeric(precision=15, scale=8), nullable=False),
        sa.Column('commission', sa.Numeric(precision=15, scale=8)),
        sa.Column('pnl', sa.Numeric(precision=15, scale=8)),
        sa.Column('strategy', sa.String(length=50)),
        sa.Column('confidence', sa.Numeric(precision=3, scale=2)),
        sa.Column('market_data', sa.JSON()),
        sa.Column('order_id', sa.String(length=100)),
        sa.Column('order_type', sa.String(length=20)),
        sa.ForeignKeyConstraint(['bot_id'], ['user_bots.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_trades_user_id'), 'user_trades', ['user_id'])

    # Billing addresses table
    op.create_table('billing_addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=255)),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('address_line_1', sa.String(length=255), nullable=False),
        sa.Column('address_line_2', sa.String(length=255)),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100)),
        sa.Column('postal_code', sa.String(length=20), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('tax_id', sa.String(length=50)),
        sa.Column('vat_number', sa.String(length=50)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Invoices table
    op.create_table('invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=10, scale=2)),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3)),
        sa.Column('status', sa.String(length=20)),
        sa.Column('issue_date', sa.DateTime()),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('paid_date', sa.DateTime()),
        sa.Column('billing_period_start', sa.DateTime()),
        sa.Column('billing_period_end', sa.DateTime()),
        sa.Column('stripe_invoice_id', sa.String(length=255)),
        sa.Column('payment_method', sa.String(length=50)),
        sa.Column('line_items', sa.JSON()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number'),
        sa.UniqueConstraint('stripe_invoice_id')
    )

    # Payments table
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer()),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3)),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20)),
        sa.Column('stripe_payment_intent_id', sa.String(length=255)),
        sa.Column('stripe_charge_id', sa.String(length=255)),
        sa.Column('transaction_id', sa.String(length=255)),
        sa.Column('payment_date', sa.DateTime()),
        sa.Column('refund_date', sa.DateTime()),
        sa.Column('description', sa.Text()),
        sa.Column('metadata', sa.JSON()),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_payment_intent_id')
    )


def downgrade():
    """Drop all tables"""
    op.drop_table('payments')
    op.drop_table('invoices')
    op.drop_table('billing_addresses')
    op.drop_table('user_trades')
    op.drop_table('user_bots')
    op.drop_table('user_trading_configs')
    op.drop_table('subscriptions')
    op.drop_table('plan_features')
    op.drop_table('subscription_plans')
    op.drop_table('user_profiles')
    op.drop_table('users')
