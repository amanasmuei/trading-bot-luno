"""
Authentication Manager
"""

import secrets
from datetime import datetime, timedelta
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from email_validator import validate_email, EmailNotValidError

from src.models.user import User, UserProfile
from src.models.subscription import Subscription, SubscriptionPlan
from src.models.base import db


class AuthManager:
    """Handles user authentication and authorization"""
    
    @staticmethod
    def register_user(email, password, first_name, last_name, **kwargs):
        """Register a new user"""
        try:
            # Validate email
            valid_email = validate_email(email)
            email = valid_email.email
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                return None, "User with this email already exists"
            
            # Create user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                **kwargs
            )
            user.set_password(password)
            user.save()
            
            # Create user profile
            profile = UserProfile(
                user_id=user.id,
                timezone=kwargs.get('timezone', 'UTC'),
                country=kwargs.get('country'),
                language=kwargs.get('language', 'en')
            )
            profile.save()
            
            # Create free subscription
            free_plan = SubscriptionPlan.query.filter_by(name='Free').first()
            if free_plan:
                subscription = Subscription(
                    user_id=user.id,
                    plan_id=free_plan.id
                )
                subscription.save()
            
            return user, None
            
        except EmailNotValidError as e:
            return None, f"Invalid email: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return None, f"Registration failed: {str(e)}"
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return None, "User not found"
            
            if not user.is_active:
                return None, "Account is deactivated"
            
            if not user.check_password(password):
                return None, "Invalid password"
            
            # Record login
            user.record_login()
            
            return user, None
            
        except Exception as e:
            return None, f"Authentication failed: {str(e)}"
    
    @staticmethod
    def generate_tokens(user):
        """Generate JWT tokens for user"""
        try:
            additional_claims = {
                'email': user.email,
                'is_admin': user.is_admin,
                'is_verified': user.is_verified,
                'subscription_plan': user.subscription.plan.name if user.subscription else 'Free'
            }
            
            access_token = create_access_token(
                identity=user.id,
                additional_claims=additional_claims,
                expires_delta=timedelta(hours=1)
            )
            
            refresh_token = create_refresh_token(
                identity=user.id,
                expires_delta=timedelta(days=30)
            )
            
            return access_token, refresh_token, None
            
        except Exception as e:
            return None, None, f"Token generation failed: {str(e)}"
    
    @staticmethod
    def refresh_access_token():
        """Refresh access token using refresh token"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return None, "User not found or inactive"
            
            additional_claims = {
                'email': user.email,
                'is_admin': user.is_admin,
                'is_verified': user.is_verified,
                'subscription_plan': user.subscription.plan.name if user.subscription else 'Free'
            }
            
            new_access_token = create_access_token(
                identity=user.id,
                additional_claims=additional_claims,
                expires_delta=timedelta(hours=1)
            )
            
            return new_access_token, None
            
        except Exception as e:
            return None, f"Token refresh failed: {str(e)}"
    
    @staticmethod
    def verify_email(token):
        """Verify user email with token"""
        try:
            user = User.query.filter_by(email_verification_token=token).first()
            
            if not user:
                return False, "Invalid verification token"
            
            user.verify_email()
            return True, "Email verified successfully"
            
        except Exception as e:
            return False, f"Email verification failed: {str(e)}"
    
    @staticmethod
    def request_password_reset(email):
        """Request password reset"""
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Don't reveal if email exists
                return True, "If the email exists, a reset link has been sent"
            
            token = user.generate_password_reset_token()
            
            # TODO: Send email with reset link
            # send_password_reset_email(user.email, token)
            
            return True, "Password reset link sent"
            
        except Exception as e:
            return False, f"Password reset request failed: {str(e)}"
    
    @staticmethod
    def reset_password(token, new_password):
        """Reset password with token"""
        try:
            user = User.query.filter_by(password_reset_token=token).first()
            
            if not user:
                return False, "Invalid reset token"
            
            if user.password_reset_expires < datetime.utcnow():
                return False, "Reset token has expired"
            
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.save()
            
            return True, "Password reset successfully"
            
        except Exception as e:
            return False, f"Password reset failed: {str(e)}"
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return False, "User not found"
            
            if not user.check_password(current_password):
                return False, "Current password is incorrect"
            
            user.set_password(new_password)
            user.save()
            
            return True, "Password changed successfully"
            
        except Exception as e:
            return False, f"Password change failed: {str(e)}"
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate user account"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return False, "User not found"
            
            user.is_active = False
            user.save()
            
            # Stop all user bots
            for bot in user.bots:
                bot.stop()
            
            return True, "User account deactivated"
            
        except Exception as e:
            return False, f"User deactivation failed: {str(e)}"
    
    @staticmethod
    def reactivate_user(user_id):
        """Reactivate user account"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return False, "User not found"
            
            user.is_active = True
            user.save()
            
            return True, "User account reactivated"
            
        except Exception as e:
            return False, f"User reactivation failed: {str(e)}"
    
    @staticmethod
    def get_current_user(user_id):
        """Get current user by ID"""
        try:
            user = User.query.get(user_id)
            return user
        except Exception:
            return None
    
    @staticmethod
    def validate_api_key(api_key):
        """Validate API key and return user"""
        try:
            user = User.query.filter_by(api_key=api_key).first()
            
            if not user or not user.is_active:
                return None, "Invalid API key"
            
            # Check rate limits
            if not user.can_make_api_call():
                return None, "API rate limit exceeded"
            
            user.increment_api_calls()
            return user, None
            
        except Exception as e:
            return None, f"API key validation failed: {str(e)}"
