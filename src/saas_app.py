"""
Main SaaS Application
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

from src.models.base import db, init_db
from src.api.v1 import api_v1
from src.web.saas_dashboard import saas_dashboard_bp
from src.web.admin_panel import admin_panel_bp
from src.web.auth_views import auth_views_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app(config_name="development"):
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Configuration
    app.config.update(
        # Database
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL", "sqlite:///saas_trading_bot.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # JWT
        JWT_SECRET_KEY=os.getenv(
            "JWT_SECRET_KEY", "your-secret-key-change-in-production"
        ),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
        # Mail
        MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "true").lower() == "true",
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
        # Stripe
        STRIPE_PUBLISHABLE_KEY=os.getenv("STRIPE_PUBLISHABLE_KEY"),
        STRIPE_SECRET_KEY=os.getenv("STRIPE_SECRET_KEY"),
        STRIPE_WEBHOOK_SECRET=os.getenv("STRIPE_WEBHOOK_SECRET"),
        # Redis
        REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        # Security
        SECRET_KEY=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
        WTF_CSRF_ENABLED=True,
        # Rate limiting
        RATELIMIT_STORAGE_URL=os.getenv("REDIS_URL", "redis://localhost:6379/1"),
        # Application
        DEBUG=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        TESTING=False,
    )

    # Initialize extensions
    db.init_app(app)

    # CORS
    CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","))

    # JWT
    jwt = JWTManager(app)

    # Rate limiting
    limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per hour"])
    limiter.init_app(app)

    # Mail
    mail = Mail(app)

    # Register blueprints
    app.register_blueprint(api_v1)
    app.register_blueprint(saas_dashboard_bp)
    app.register_blueprint(admin_panel_bp)
    app.register_blueprint(auth_views_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return (
            jsonify({"error": "Rate limit exceeded", "message": str(e.description)}),
            429,
        )

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization token is required"}), 401

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return jsonify(
            {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    # API info endpoint
    @app.route("/api/info")
    def api_info():
        return jsonify(
            {
                "name": "Luno Trading Bot SaaS Platform",
                "version": "1.0.0",
                "description": "Multi-tenant trading bot platform with subscription management",
                "endpoints": {
                    "auth": "/api/v1/auth",
                    "users": "/api/v1/users",
                    "subscriptions": "/api/v1/subscriptions",
                    "trading": "/api/v1/trading",
                    "billing": "/api/v1/billing",
                    "admin": "/api/v1/admin",
                },
                "documentation": "/docs",
            }
        )

    # Initialize database
    with app.app_context():
        init_db(app)

    # Store extensions in app for access in other modules
    app.limiter = limiter
    app.mail = mail
    app.jwt = jwt

    logger.info("SaaS Trading Bot application created successfully")

    return app


def create_celery_app(app=None):
    """Create Celery app for background tasks"""
    from celery import Celery

    app = app or create_app()

    celery = Celery(
        app.import_name,
        backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
        broker=app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/3"),
    )

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# Create application instance
app = create_app()
celery = create_celery_app(app)


if __name__ == "__main__":
    # Development server
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    logger.info(f"Starting SaaS Trading Bot application on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
