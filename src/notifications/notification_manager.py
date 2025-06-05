"""
Notification Manager
Comprehensive notification system for trading alerts and updates
"""

import logging
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import os

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications"""
    TRADE_EXECUTED = "trade_executed"
    SIGNAL_GENERATED = "signal_generated"
    RISK_ALERT = "risk_alert"
    PORTFOLIO_UPDATE = "portfolio_update"
    SYSTEM_ERROR = "system_error"
    DAILY_SUMMARY = "daily_summary"
    PERFORMANCE_MILESTONE = "performance_milestone"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class NotificationConfig:
    """Configuration for notification channels"""
    
    # Email settings
    email_enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    recipient_emails: List[str] = None
    
    # SMS settings (Twilio)
    sms_enabled: bool = False
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    recipient_phones: List[str] = None
    
    # Discord webhook
    discord_enabled: bool = False
    discord_webhook_url: str = ""
    
    # Slack webhook
    slack_enabled: bool = False
    slack_webhook_url: str = ""
    
    # Custom webhook
    webhook_enabled: bool = False
    webhook_url: str = ""
    webhook_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.recipient_emails is None:
            self.recipient_emails = []
        if self.recipient_phones is None:
            self.recipient_phones = []
        if self.webhook_headers is None:
            self.webhook_headers = {}


@dataclass
class Notification:
    """Individual notification message"""
    
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.data is None:
            self.data = {}


class NotificationManager:
    """Comprehensive notification management system"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.notification_history: List[Notification] = []
        self.rate_limits: Dict[str, datetime] = {}
        
        # Rate limiting settings (prevent spam)
        self.rate_limit_minutes = {
            NotificationType.TRADE_EXECUTED: 0,  # No limit
            NotificationType.SIGNAL_GENERATED: 5,  # Max 1 per 5 minutes
            NotificationType.RISK_ALERT: 1,  # Max 1 per minute
            NotificationType.PORTFOLIO_UPDATE: 30,  # Max 1 per 30 minutes
            NotificationType.SYSTEM_ERROR: 5,  # Max 1 per 5 minutes
            NotificationType.DAILY_SUMMARY: 1440,  # Max 1 per day
            NotificationType.PERFORMANCE_MILESTONE: 60,  # Max 1 per hour
        }
        
        logger.info("NotificationManager initialized")
    
    def send_notification(self, notification: Notification) -> bool:
        """Send notification through all enabled channels"""
        
        # Check rate limiting
        if not self._check_rate_limit(notification):
            logger.debug(f"Rate limit exceeded for {notification.type.value}")
            return False
        
        # Store notification
        self.notification_history.append(notification)
        
        # Keep only last 1000 notifications
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
        
        success = True
        
        try:
            # Send through enabled channels
            if self.config.email_enabled:
                success &= self._send_email(notification)
            
            if self.config.sms_enabled:
                success &= self._send_sms(notification)
            
            if self.config.discord_enabled:
                success &= self._send_discord(notification)
            
            if self.config.slack_enabled:
                success &= self._send_slack(notification)
            
            if self.config.webhook_enabled:
                success &= self._send_webhook(notification)
            
            if success:
                logger.info(f"Notification sent: {notification.title}")
            else:
                logger.warning(f"Some notification channels failed: {notification.title}")
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            success = False
        
        return success
    
    def _check_rate_limit(self, notification: Notification) -> bool:
        """Check if notification is within rate limits"""
        
        rate_limit_key = f"{notification.type.value}_{notification.priority.value}"
        limit_minutes = self.rate_limit_minutes.get(notification.type, 0)
        
        if limit_minutes == 0:  # No rate limit
            return True
        
        last_sent = self.rate_limits.get(rate_limit_key)
        if last_sent is None:
            self.rate_limits[rate_limit_key] = datetime.now()
            return True
        
        time_diff = (datetime.now() - last_sent).total_seconds() / 60
        if time_diff >= limit_minutes:
            self.rate_limits[rate_limit_key] = datetime.now()
            return True
        
        return False
    
    def _send_email(self, notification: Notification) -> bool:
        """Send email notification"""
        try:
            if not self.config.recipient_emails:
                return True  # No recipients configured
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.email_username
            msg['Subject'] = f"[Trading Bot] {notification.title}"
            
            # Create email body
            body = self._format_email_body(notification)
            msg.attach(MIMEText(body, 'html'))
            
            # Send to all recipients
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_username, self.config.email_password)
                
                for recipient in self.config.recipient_emails:
                    msg['To'] = recipient
                    server.send_message(msg)
                    del msg['To']
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _send_sms(self, notification: Notification) -> bool:
        """Send SMS notification via Twilio"""
        try:
            if not self.config.recipient_phones:
                return True  # No recipients configured
            
            # Only send SMS for high priority notifications
            if notification.priority.value < NotificationPriority.HIGH.value:
                return True
            
            from twilio.rest import Client
            
            client = Client(self.config.twilio_account_sid, self.config.twilio_auth_token)
            
            # Create SMS message
            sms_body = f"{notification.title}\n{notification.message}"
            if len(sms_body) > 160:  # SMS character limit
                sms_body = sms_body[:157] + "..."
            
            # Send to all recipients
            for phone in self.config.recipient_phones:
                client.messages.create(
                    body=sms_body,
                    from_=self.config.twilio_phone_number,
                    to=phone
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    def _send_discord(self, notification: Notification) -> bool:
        """Send Discord webhook notification"""
        try:
            # Create Discord embed
            embed = {
                "title": notification.title,
                "description": notification.message,
                "color": self._get_color_for_priority(notification.priority),
                "timestamp": notification.timestamp.isoformat(),
                "fields": []
            }
            
            # Add data fields
            for key, value in notification.data.items():
                embed["fields"].append({
                    "name": key.replace("_", " ").title(),
                    "value": str(value),
                    "inline": True
                })
            
            payload = {
                "embeds": [embed],
                "username": "Trading Bot"
            }
            
            response = requests.post(
                self.config.discord_webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False
    
    def _send_slack(self, notification: Notification) -> bool:
        """Send Slack webhook notification"""
        try:
            # Create Slack message
            payload = {
                "text": notification.title,
                "attachments": [
                    {
                        "color": self._get_slack_color_for_priority(notification.priority),
                        "fields": [
                            {
                                "title": "Message",
                                "value": notification.message,
                                "short": False
                            }
                        ],
                        "ts": int(notification.timestamp.timestamp())
                    }
                ]
            }
            
            # Add data fields
            for key, value in notification.data.items():
                payload["attachments"][0]["fields"].append({
                    "title": key.replace("_", " ").title(),
                    "value": str(value),
                    "short": True
                })
            
            response = requests.post(
                self.config.slack_webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _send_webhook(self, notification: Notification) -> bool:
        """Send custom webhook notification"""
        try:
            payload = {
                "type": notification.type.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "timestamp": notification.timestamp.isoformat()
            }
            
            headers = {"Content-Type": "application/json"}
            headers.update(self.config.webhook_headers)
            
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    def _format_email_body(self, notification: Notification) -> str:
        """Format email body with HTML"""
        
        priority_colors = {
            NotificationPriority.LOW: "#28a745",
            NotificationPriority.MEDIUM: "#ffc107", 
            NotificationPriority.HIGH: "#fd7e14",
            NotificationPriority.CRITICAL: "#dc3545"
        }
        
        color = priority_colors.get(notification.priority, "#6c757d")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 20px;">
                <h2 style="color: {color}; margin-top: 0;">{notification.title}</h2>
                <p style="font-size: 16px; line-height: 1.5;">{notification.message}</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px;">
                    <h3 style="margin-top: 0; color: #495057;">Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 5px; font-weight: bold;">Type:</td>
                            <td style="padding: 5px;">{notification.type.value}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px; font-weight: bold;">Priority:</td>
                            <td style="padding: 5px;">{notification.priority.name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px; font-weight: bold;">Time:</td>
                            <td style="padding: 5px;">{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
                        </tr>
        """
        
        # Add data fields
        for key, value in notification.data.items():
            html += f"""
                        <tr>
                            <td style="padding: 5px; font-weight: bold;">{key.replace('_', ' ').title()}:</td>
                            <td style="padding: 5px;">{value}</td>
                        </tr>
            """
        
        html += """
                    </table>
                </div>
                
                <p style="margin-top: 30px; font-size: 12px; color: #6c757d;">
                    This is an automated message from your Trading Bot.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _get_color_for_priority(self, priority: NotificationPriority) -> int:
        """Get Discord embed color for priority"""
        colors = {
            NotificationPriority.LOW: 0x28a745,      # Green
            NotificationPriority.MEDIUM: 0xffc107,   # Yellow
            NotificationPriority.HIGH: 0xfd7e14,     # Orange
            NotificationPriority.CRITICAL: 0xdc3545  # Red
        }
        return colors.get(priority, 0x6c757d)  # Gray default
    
    def _get_slack_color_for_priority(self, priority: NotificationPriority) -> str:
        """Get Slack attachment color for priority"""
        colors = {
            NotificationPriority.LOW: "good",
            NotificationPriority.MEDIUM: "warning",
            NotificationPriority.HIGH: "warning",
            NotificationPriority.CRITICAL: "danger"
        }
        return colors.get(priority, "#6c757d")
    
    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """Get recent notification history"""
        recent_notifications = self.notification_history[-limit:]
        
        return [
            {
                "type": notif.type.value,
                "priority": notif.priority.name,
                "title": notif.title,
                "message": notif.message,
                "timestamp": notif.timestamp.isoformat(),
                "data": notif.data
            }
            for notif in recent_notifications
        ]
    
    # Convenience methods for common notifications
    def notify_trade_executed(self, trade_data: Dict):
        """Send trade execution notification"""
        notification = Notification(
            type=NotificationType.TRADE_EXECUTED,
            priority=NotificationPriority.MEDIUM,
            title=f"Trade Executed: {trade_data.get('action', 'Unknown')}",
            message=f"Executed {trade_data.get('action')} order for {trade_data.get('pair', 'Unknown')} at {trade_data.get('price', 'Unknown')}",
            data=trade_data
        )
        return self.send_notification(notification)
    
    def notify_risk_alert(self, alert_message: str, alert_data: Dict = None):
        """Send risk alert notification"""
        notification = Notification(
            type=NotificationType.RISK_ALERT,
            priority=NotificationPriority.HIGH,
            title="Risk Alert",
            message=alert_message,
            data=alert_data or {}
        )
        return self.send_notification(notification)
    
    def notify_system_error(self, error_message: str, error_data: Dict = None):
        """Send system error notification"""
        notification = Notification(
            type=NotificationType.SYSTEM_ERROR,
            priority=NotificationPriority.CRITICAL,
            title="System Error",
            message=error_message,
            data=error_data or {}
        )
        return self.send_notification(notification)
