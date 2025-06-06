"""
Base Database Models and Configuration
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import uuid

# SQLAlchemy setup
db = SQLAlchemy()
Base = declarative_base()


class BaseModel(db.Model):
    """Base model with common fields"""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def save(self):
        """Save model to database"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete model from database"""
        db.session.delete(self)
        db.session.commit()


class TenantMixin:
    """Mixin for tenant-aware models"""

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    @classmethod
    def get_for_user(cls, user_id, **filters):
        """Get records for specific user"""
        query = cls.query.filter_by(user_id=user_id)
        for key, value in filters.items():
            query = query.filter(getattr(cls, key) == value)
        return query


def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())


def init_db(app):
    """Initialize database with Flask app"""
    with app.app_context():
        # Import all models to ensure they're registered
        from . import user, subscription, trading, billing

        # Create all tables
        db.create_all()

        # Create default subscription plans
        from .subscription import SubscriptionPlan, PlanFeature

        create_default_plans()


def create_default_plans():
    """Create default subscription plans"""
    plans_data = [
        {
            "name": "Free",
            "price": 0.00,
            "billing_cycle": "monthly",
            "description": "Basic trading bot with limited features",
            "features": [
                {
                    "name": "max_bots",
                    "value": "1",
                    "description": "Maximum number of trading bots",
                },
                {
                    "name": "max_pairs",
                    "value": "1",
                    "description": "Maximum trading pairs",
                },
                {
                    "name": "api_calls_per_hour",
                    "value": "100",
                    "description": "API calls per hour",
                },
                {
                    "name": "backtesting",
                    "value": "false",
                    "description": "Backtesting capabilities",
                },
                {
                    "name": "advanced_strategies",
                    "value": "false",
                    "description": "Advanced trading strategies",
                },
                {
                    "name": "notifications",
                    "value": "email",
                    "description": "Notification channels",
                },
                {
                    "name": "support",
                    "value": "community",
                    "description": "Support level",
                },
            ],
        },
        {
            "name": "Basic",
            "price": 29.99,
            "billing_cycle": "monthly",
            "description": "Enhanced trading with multiple pairs and strategies",
            "features": [
                {
                    "name": "max_bots",
                    "value": "3",
                    "description": "Maximum number of trading bots",
                },
                {
                    "name": "max_pairs",
                    "value": "5",
                    "description": "Maximum trading pairs",
                },
                {
                    "name": "api_calls_per_hour",
                    "value": "1000",
                    "description": "API calls per hour",
                },
                {
                    "name": "backtesting",
                    "value": "true",
                    "description": "Backtesting capabilities",
                },
                {
                    "name": "advanced_strategies",
                    "value": "basic",
                    "description": "Basic advanced strategies",
                },
                {
                    "name": "notifications",
                    "value": "email,sms",
                    "description": "Email and SMS notifications",
                },
                {"name": "support", "value": "email", "description": "Email support"},
            ],
        },
        {
            "name": "Premium",
            "price": 99.99,
            "billing_cycle": "monthly",
            "description": "Professional trading with unlimited features",
            "features": [
                {
                    "name": "max_bots",
                    "value": "10",
                    "description": "Maximum number of trading bots",
                },
                {
                    "name": "max_pairs",
                    "value": "20",
                    "description": "Maximum trading pairs",
                },
                {
                    "name": "api_calls_per_hour",
                    "value": "10000",
                    "description": "API calls per hour",
                },
                {
                    "name": "backtesting",
                    "value": "true",
                    "description": "Advanced backtesting",
                },
                {
                    "name": "advanced_strategies",
                    "value": "all",
                    "description": "All advanced strategies",
                },
                {
                    "name": "notifications",
                    "value": "all",
                    "description": "All notification channels",
                },
                {
                    "name": "support",
                    "value": "priority",
                    "description": "Priority support",
                },
                {
                    "name": "custom_indicators",
                    "value": "true",
                    "description": "Custom indicators",
                },
                {"name": "api_access", "value": "true", "description": "API access"},
            ],
        },
        {
            "name": "Enterprise",
            "price": 299.99,
            "billing_cycle": "monthly",
            "description": "Enterprise-grade trading platform with dedicated support",
            "features": [
                {
                    "name": "max_bots",
                    "value": "unlimited",
                    "description": "Unlimited trading bots",
                },
                {
                    "name": "max_pairs",
                    "value": "unlimited",
                    "description": "Unlimited trading pairs",
                },
                {
                    "name": "api_calls_per_hour",
                    "value": "unlimited",
                    "description": "Unlimited API calls",
                },
                {
                    "name": "backtesting",
                    "value": "true",
                    "description": "Advanced backtesting",
                },
                {
                    "name": "advanced_strategies",
                    "value": "all",
                    "description": "All strategies + custom",
                },
                {
                    "name": "notifications",
                    "value": "all",
                    "description": "All notification channels",
                },
                {
                    "name": "support",
                    "value": "dedicated",
                    "description": "Dedicated account manager",
                },
                {
                    "name": "custom_indicators",
                    "value": "true",
                    "description": "Custom indicators",
                },
                {
                    "name": "api_access",
                    "value": "true",
                    "description": "Full API access",
                },
                {
                    "name": "white_label",
                    "value": "true",
                    "description": "White label options",
                },
                {"name": "sla", "value": "99.9", "description": "99.9% uptime SLA"},
            ],
        },
    ]

    from .subscription import SubscriptionPlan, PlanFeature

    for plan_data in plans_data:
        # Check if plan already exists
        existing_plan = SubscriptionPlan.query.filter_by(name=plan_data["name"]).first()
        if existing_plan:
            continue

        # Create plan
        plan = SubscriptionPlan(
            name=plan_data["name"],
            price=plan_data["price"],
            billing_cycle=plan_data["billing_cycle"],
            description=plan_data["description"],
        )
        plan.save()

        # Create features
        for feature_data in plan_data["features"]:
            feature = PlanFeature(
                plan_id=plan.id,
                name=feature_data["name"],
                value=feature_data["value"],
                description=feature_data["description"],
            )
            feature.save()
