"""
Authentication Web Views
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
import logging

logger = logging.getLogger(__name__)

# Create blueprint
auth_views_bp = Blueprint('auth_views', __name__, url_prefix='/auth', template_folder='templates/auth')


@auth_views_bp.route('/login')
def login_page():
    """Login page"""
    return render_template('auth/login.html')


@auth_views_bp.route('/register')
def register_page():
    """Registration page"""
    return render_template('auth/register.html')


@auth_views_bp.route('/forgot-password')
def forgot_password_page():
    """Forgot password page"""
    return render_template('auth/forgot_password.html')


@auth_views_bp.route('/reset-password')
def reset_password_page():
    """Reset password page"""
    token = request.args.get('token')
    if not token:
        flash('Invalid reset link', 'error')
        return redirect(url_for('auth_views.forgot_password_page'))
    
    return render_template('auth/reset_password.html', token=token)


@auth_views_bp.route('/verify-email')
def verify_email_page():
    """Email verification page"""
    token = request.args.get('token')
    if not token:
        flash('Invalid verification link', 'error')
        return redirect(url_for('saas_dashboard.landing_page'))
    
    return render_template('auth/verify_email.html', token=token)


@auth_views_bp.route('/logout')
def logout():
    """Logout and redirect to landing page"""
    # Clear any session data
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('saas_dashboard.landing_page'))
