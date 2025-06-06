"""
Subscription and Billing Models
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
import json

from .base import db, BaseModel


class SubscriptionPlan(BaseModel):
    """Subscription plan model"""
    __tablename__ = 'subscription_plans'
    
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    billing_cycle = db.Column(db.String(20), nullable=False)  # monthly, yearly
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Plan metadata
    max_bots = db.Column(db.Integer, default=1)
    max_pairs = db.Column(db.Integer, default=1)
    api_calls_per_hour = db.Column(db.Integer, default=100)
    
    # Relationships
    features = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="plan")
    
    def get_feature_value(self, feature_name):
        """Get feature value by name"""
        feature = next((f for f in self.features if f.name == feature_name), None)
        return feature.value if feature else None
    
    def has_feature(self, feature_name):
        """Check if plan has specific feature"""
        return any(f.name == feature_name for f in self.features)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'billing_cycle': self.billing_cycle,
            'description': self.description,
            'is_active': self.is_active,
            'max_bots': self.max_bots,
            'max_pairs': self.max_pairs,
            'api_calls_per_hour': self.api_calls_per_hour,
            'features': [f.to_dict() for f in self.features],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class PlanFeature(BaseModel):
    """Plan feature model"""
    __tablename__ = 'plan_features'
    
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="features")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'name': self.name,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Subscription(BaseModel):
    """User subscription model"""
    __tablename__ = 'subscriptions'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    
    # Subscription status
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired, suspended
    
    # Billing dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    next_billing_date = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Payment info
    stripe_subscription_id = db.Column(db.String(255), unique=True)
    stripe_customer_id = db.Column(db.String(255))
    
    # Usage tracking
    current_bots = db.Column(db.Integer, default=0)
    current_pairs = db.Column(db.Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.end_date and self.plan:
            self.calculate_end_date()
    
    def calculate_end_date(self):
        """Calculate subscription end date based on billing cycle"""
        if self.plan.billing_cycle == 'monthly':
            self.end_date = self.start_date + timedelta(days=30)
            self.next_billing_date = self.end_date
        elif self.plan.billing_cycle == 'yearly':
            self.end_date = self.start_date + timedelta(days=365)
            self.next_billing_date = self.end_date
    
    def is_active(self):
        """Check if subscription is active"""
        return (
            self.status == 'active' and
            self.end_date > datetime.utcnow()
        )
    
    def is_expired(self):
        """Check if subscription is expired"""
        return self.end_date <= datetime.utcnow()
    
    def days_remaining(self):
        """Get days remaining in subscription"""
        if self.is_expired():
            return 0
        return (self.end_date - datetime.utcnow()).days
    
    def renew(self):
        """Renew subscription"""
        self.start_date = datetime.utcnow()
        self.calculate_end_date()
        self.status = 'active'
        self.save()
    
    def cancel(self):
        """Cancel subscription"""
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.save()
    
    def suspend(self):
        """Suspend subscription"""
        self.status = 'suspended'
        self.save()
    
    def reactivate(self):
        """Reactivate subscription"""
        self.status = 'active'
        self.save()
    
    def get_feature_value(self, feature_name):
        """Get feature value from plan"""
        return self.plan.get_feature_value(feature_name)
    
    def has_feature(self, feature_name):
        """Check if subscription has feature"""
        return self.plan.has_feature(feature_name)
    
    def can_create_bot(self):
        """Check if user can create another bot"""
        max_bots = self.get_feature_value('max_bots')
        if max_bots == 'unlimited':
            return True
        return self.current_bots < int(max_bots)
    
    def can_add_pair(self):
        """Check if user can add another trading pair"""
        max_pairs = self.get_feature_value('max_pairs')
        if max_pairs == 'unlimited':
            return True
        return self.current_pairs < int(max_pairs)
    
    def increment_bot_count(self):
        """Increment bot count"""
        self.current_bots += 1
        self.save()
    
    def decrement_bot_count(self):
        """Decrement bot count"""
        if self.current_bots > 0:
            self.current_bots -= 1
            self.save()
    
    def increment_pair_count(self):
        """Increment pair count"""
        self.current_pairs += 1
        self.save()
    
    def decrement_pair_count(self):
        """Decrement pair count"""
        if self.current_pairs > 0:
            self.current_pairs -= 1
            self.save()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'status': self.status,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'days_remaining': self.days_remaining(),
            'is_active': self.is_active(),
            'current_bots': self.current_bots,
            'current_pairs': self.current_pairs,
            'stripe_subscription_id': self.stripe_subscription_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
