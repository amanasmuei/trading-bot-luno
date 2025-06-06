"""
User Management Models
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
import secrets

from .base import db, BaseModel, generate_uuid


class User(BaseModel):
    """User account model"""

    __tablename__ = "users"

    # Basic info
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Security
    email_verification_token = db.Column(db.String(255), unique=True)
    password_reset_token = db.Column(db.String(255), unique=True)
    password_reset_expires = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)

    # API Access
    api_key = db.Column(db.String(255), unique=True)
    api_secret = db.Column(db.String(255))
    api_calls_count = db.Column(db.Integer, default=0)
    api_calls_reset_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    subscription = relationship(
        "Subscription",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    trading_configs = relationship(
        "UserTradingConfig", back_populates="user", cascade="all, delete-orphan"
    )
    bots = relationship("UserBot", back_populates="user", cascade="all, delete-orphan")
    trades = relationship(
        "UserTrade", back_populates="user", cascade="all, delete-orphan"
    )
    invoices = relationship(
        "Invoice", back_populates="user", cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api_key:
            self.generate_api_credentials()
        if not self.email_verification_token:
            self.email_verification_token = secrets.token_urlsafe(32)

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)

    def generate_api_credentials(self):
        """Generate API key and secret"""
        self.api_key = f"luno_saas_{secrets.token_urlsafe(16)}"
        self.api_secret = secrets.token_urlsafe(32)

    def regenerate_api_credentials(self):
        """Regenerate API credentials"""
        self.generate_api_credentials()
        self.save()

    def generate_tokens(self):
        """Generate JWT tokens"""
        access_token = create_access_token(
            identity=self.id,
            additional_claims={
                "email": self.email,
                "is_admin": self.is_admin,
                "subscription_plan": (
                    self.subscription.plan.name if self.subscription else "Free"
                ),
            },
        )
        refresh_token = create_refresh_token(identity=self.id)
        return access_token, refresh_token

    def generate_password_reset_token(self):
        """Generate password reset token"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        self.save()
        return self.password_reset_token

    def verify_email(self):
        """Verify user email"""
        self.is_verified = True
        self.email_verification_token = None
        self.save()

    def record_login(self):
        """Record user login"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.save()

    def increment_api_calls(self):
        """Increment API calls counter"""
        # Reset counter if it's a new hour
        now = datetime.utcnow()
        if (now - self.api_calls_reset_at).total_seconds() >= 3600:
            self.api_calls_count = 0
            self.api_calls_reset_at = now

        self.api_calls_count += 1
        self.save()

    def can_make_api_call(self):
        """Check if user can make API call based on plan limits"""
        if not self.subscription:
            return self.api_calls_count < 100  # Free plan limit

        plan_limit = self.subscription.get_feature_value("api_calls_per_hour")
        if plan_limit == "unlimited":
            return True

        return self.api_calls_count < int(plan_limit)

    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_premium(self):
        """Check if user has premium subscription"""
        if not self.subscription:
            return False
        return self.subscription.plan.name in ["Premium", "Enterprise"]

    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_admin": self.is_admin,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "subscription": self.subscription.to_dict() if self.subscription else None,
            "profile": self.profile.to_dict() if self.profile else None,
        }

        if include_sensitive:
            data.update(
                {
                    "api_key": self.api_key,
                    "api_calls_count": self.api_calls_count,
                    "api_calls_reset_at": (
                        self.api_calls_reset_at.isoformat()
                        if self.api_calls_reset_at
                        else None
                    ),
                }
            )

        return data


class UserProfile(BaseModel):
    """Extended user profile information"""

    __tablename__ = "user_profiles"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )

    # Personal info
    phone = db.Column(db.String(20))
    timezone = db.Column(db.String(50), default="UTC")
    country = db.Column(db.String(100))
    language = db.Column(db.String(10), default="en")

    # Trading preferences
    risk_tolerance = db.Column(db.String(20), default="medium")  # low, medium, high
    preferred_pairs = db.Column(db.Text)  # JSON array of trading pairs
    notification_preferences = db.Column(db.Text)  # JSON object

    # Platform settings
    theme = db.Column(db.String(20), default="light")
    dashboard_layout = db.Column(db.Text)  # JSON object

    # Marketing
    marketing_emails = db.Column(db.Boolean, default=True)
    newsletter = db.Column(db.Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="profile")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "phone": self.phone,
            "timezone": self.timezone,
            "country": self.country,
            "language": self.language,
            "risk_tolerance": self.risk_tolerance,
            "preferred_pairs": self.preferred_pairs,
            "notification_preferences": self.notification_preferences,
            "theme": self.theme,
            "dashboard_layout": self.dashboard_layout,
            "marketing_emails": self.marketing_emails,
            "newsletter": self.newsletter,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
