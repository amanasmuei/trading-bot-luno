"""
SaaS Platform API v1
"""

from flask import Blueprint
from .auth import auth_bp
from .users import users_bp
from .subscriptions import subscriptions_bp
from .trading import trading_bp
from .admin import admin_bp
from .billing import billing_bp

# Create main API blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Register sub-blueprints
api_v1.register_blueprint(auth_bp)
api_v1.register_blueprint(users_bp)
api_v1.register_blueprint(subscriptions_bp)
api_v1.register_blueprint(trading_bp)
api_v1.register_blueprint(admin_bp)
api_v1.register_blueprint(billing_bp)

__all__ = ['api_v1']
