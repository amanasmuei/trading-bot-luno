"""
Strategy Templates and Configuration Management
Pre-configured trading strategies and dynamic configuration system
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from src.config.enhanced_settings import EnhancedTradingConfig
from src.notifications.notification_manager import NotificationConfig

logger = logging.getLogger(__name__)


@dataclass
class StrategyTemplate:
    """Template for trading strategy configuration"""
    name: str
    description: str
    risk_level: str  # "conservative", "moderate", "aggressive"
    target_pairs: List[str]
    config_overrides: Dict[str, Any]
    performance_targets: Dict[str, float]
    created_at: datetime
    author: str = "System"
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyTemplate':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class StrategyTemplateManager:
    """Manages strategy templates and configurations"""
    
    def __init__(self, templates_dir: str = "config/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates: Dict[str, StrategyTemplate] = {}
        self._load_default_templates()
        self._load_custom_templates()
        
    def _load_default_templates(self):
        """Load default strategy templates"""
        
        # Conservative Strategy
        conservative = StrategyTemplate(
            name="conservative",
            description="Low-risk strategy focused on capital preservation with steady returns",
            risk_level="conservative",
            target_pairs=["XBTMYR", "ETHMYR"],
            config_overrides={
                "max_position_size_percent": 1.0,
                "base_stop_loss_percent": 2.0,
                "base_take_profit_percent": 4.0,
                "max_daily_trades": 2,
                "min_confidence_buy": 0.75,
                "min_confidence_sell": 0.75,
                "rsi_oversold": 25,
                "rsi_overbought": 75,
                "volatility_position_scaling": True,
                "min_position_multiplier": 0.5,
                "max_position_multiplier": 1.0
            },
            performance_targets={
                "annual_return": 15.0,
                "max_drawdown": -10.0,
                "sharpe_ratio": 1.2,
                "win_rate": 0.65
            },
            created_at=datetime.now()
        )
        
        # Moderate Strategy
        moderate = StrategyTemplate(
            name="moderate",
            description="Balanced strategy with moderate risk for steady growth",
            risk_level="moderate",
            target_pairs=["XBTMYR", "XBTZAR", "ETHMYR", "ETHZAR"],
            config_overrides={
                "max_position_size_percent": 1.5,
                "base_stop_loss_percent": 3.0,
                "base_take_profit_percent": 6.0,
                "max_daily_trades": 3,
                "min_confidence_buy": 0.65,
                "min_confidence_sell": 0.65,
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "volatility_position_scaling": True,
                "min_position_multiplier": 0.4,
                "max_position_multiplier": 1.2
            },
            performance_targets={
                "annual_return": 25.0,
                "max_drawdown": -15.0,
                "sharpe_ratio": 1.0,
                "win_rate": 0.60
            },
            created_at=datetime.now()
        )
        
        # Aggressive Strategy
        aggressive = StrategyTemplate(
            name="aggressive",
            description="High-risk, high-reward strategy for experienced traders",
            risk_level="aggressive",
            target_pairs=["XBTMYR", "XBTZAR", "XBTEUR", "ETHMYR", "ETHZAR", "LTCMYR"],
            config_overrides={
                "max_position_size_percent": 2.5,
                "base_stop_loss_percent": 4.0,
                "base_take_profit_percent": 8.0,
                "max_daily_trades": 5,
                "min_confidence_buy": 0.55,
                "min_confidence_sell": 0.55,
                "rsi_oversold": 35,
                "rsi_overbought": 65,
                "volatility_position_scaling": True,
                "min_position_multiplier": 0.3,
                "max_position_multiplier": 1.5
            },
            performance_targets={
                "annual_return": 40.0,
                "max_drawdown": -25.0,
                "sharpe_ratio": 0.8,
                "win_rate": 0.55
            },
            created_at=datetime.now()
        )
        
        # Scalping Strategy
        scalping = StrategyTemplate(
            name="scalping",
            description="High-frequency trading strategy for quick profits",
            risk_level="aggressive",
            target_pairs=["XBTMYR", "ETHMYR"],
            config_overrides={
                "max_position_size_percent": 3.0,
                "base_stop_loss_percent": 1.5,
                "base_take_profit_percent": 3.0,
                "max_daily_trades": 10,
                "min_confidence_buy": 0.50,
                "min_confidence_sell": 0.50,
                "check_interval": 30,  # 30 seconds
                "rsi_period": 7,
                "ema_short": 5,
                "ema_medium": 10,
                "ema_long": 20
            },
            performance_targets={
                "annual_return": 50.0,
                "max_drawdown": -20.0,
                "sharpe_ratio": 0.9,
                "win_rate": 0.60
            },
            created_at=datetime.now()
        )
        
        # Swing Trading Strategy
        swing = StrategyTemplate(
            name="swing",
            description="Medium-term strategy holding positions for days to weeks",
            risk_level="moderate",
            target_pairs=["XBTMYR", "XBTZAR", "ETHMYR", "ETHZAR"],
            config_overrides={
                "max_position_size_percent": 2.0,
                "base_stop_loss_percent": 5.0,
                "base_take_profit_percent": 10.0,
                "max_daily_trades": 1,
                "min_confidence_buy": 0.70,
                "min_confidence_sell": 0.70,
                "check_interval": 3600,  # 1 hour
                "rsi_period": 21,
                "ema_short": 12,
                "ema_medium": 26,
                "ema_long": 50,
                "bollinger_period": 30
            },
            performance_targets={
                "annual_return": 30.0,
                "max_drawdown": -18.0,
                "sharpe_ratio": 1.1,
                "win_rate": 0.58
            },
            created_at=datetime.now()
        )
        
        # Store templates
        self.templates = {
            "conservative": conservative,
            "moderate": moderate,
            "aggressive": aggressive,
            "scalping": scalping,
            "swing": swing
        }
        
        logger.info(f"Loaded {len(self.templates)} default strategy templates")
    
    def _load_custom_templates(self):
        """Load custom templates from files"""
        try:
            for template_file in self.templates_dir.glob("*.json"):
                with open(template_file, 'r') as f:
                    data = json.load(f)
                    template = StrategyTemplate.from_dict(data)
                    self.templates[template.name] = template
                    logger.info(f"Loaded custom template: {template.name}")
        except Exception as e:
            logger.error(f"Error loading custom templates: {e}")
    
    def get_template(self, name: str) -> Optional[StrategyTemplate]:
        """Get a strategy template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())
    
    def get_templates_by_risk_level(self, risk_level: str) -> List[StrategyTemplate]:
        """Get templates filtered by risk level"""
        return [template for template in self.templates.values() 
                if template.risk_level == risk_level]
    
    def create_config_from_template(self, 
                                  template_name: str, 
                                  base_config: EnhancedTradingConfig,
                                  custom_overrides: Dict[str, Any] = None) -> EnhancedTradingConfig:
        """Create a trading config from a template"""
        
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Start with base config
        config_dict = asdict(base_config)
        
        # Apply template overrides
        config_dict.update(template.config_overrides)
        
        # Apply custom overrides if provided
        if custom_overrides:
            config_dict.update(custom_overrides)
        
        # Create new config
        new_config = EnhancedTradingConfig(**config_dict)
        
        logger.info(f"Created config from template: {template_name}")
        return new_config
    
    def save_template(self, template: StrategyTemplate, overwrite: bool = False):
        """Save a custom template to file"""
        
        template_file = self.templates_dir / f"{template.name}.json"
        
        if template_file.exists() and not overwrite:
            raise ValueError(f"Template '{template.name}' already exists. Use overwrite=True to replace.")
        
        try:
            with open(template_file, 'w') as f:
                json.dump(template.to_dict(), f, indent=2)
            
            # Add to memory
            self.templates[template.name] = template
            
            logger.info(f"Saved template: {template.name}")
            
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            raise
    
    def delete_template(self, name: str):
        """Delete a custom template"""
        
        if name in ["conservative", "moderate", "aggressive", "scalping", "swing"]:
            raise ValueError("Cannot delete default templates")
        
        template_file = self.templates_dir / f"{name}.json"
        
        if template_file.exists():
            template_file.unlink()
        
        if name in self.templates:
            del self.templates[name]
        
        logger.info(f"Deleted template: {name}")
    
    def get_template_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all templates"""
        
        summary = {}
        for name, template in self.templates.items():
            summary[name] = {
                "description": template.description,
                "risk_level": template.risk_level,
                "target_pairs": template.target_pairs,
                "performance_targets": template.performance_targets,
                "created_at": template.created_at.isoformat()
            }
        
        return summary


class ConfigurationManager:
    """Advanced configuration management system"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.template_manager = StrategyTemplateManager()
        self.active_configs: Dict[str, EnhancedTradingConfig] = {}
        
    def create_trading_config(self, 
                            template_name: str = "moderate",
                            trading_pair: str = "XBTMYR",
                            custom_settings: Dict[str, Any] = None) -> EnhancedTradingConfig:
        """Create a complete trading configuration"""
        
        # Base configuration
        base_config = EnhancedTradingConfig(trading_pair=trading_pair)
        
        # Apply template
        config = self.template_manager.create_config_from_template(
            template_name, base_config, custom_settings
        )
        
        # Store active config
        config_key = f"{template_name}_{trading_pair}"
        self.active_configs[config_key] = config
        
        return config
    
    def create_notification_config(self, 
                                 email_settings: Dict[str, Any] = None,
                                 sms_settings: Dict[str, Any] = None,
                                 webhook_settings: Dict[str, Any] = None) -> NotificationConfig:
        """Create notification configuration"""
        
        config = NotificationConfig()
        
        # Email configuration
        if email_settings:
            config.email_enabled = email_settings.get("enabled", False)
            config.smtp_server = email_settings.get("smtp_server", "smtp.gmail.com")
            config.smtp_port = email_settings.get("smtp_port", 587)
            config.email_username = email_settings.get("username", "")
            config.email_password = email_settings.get("password", "")
            config.recipient_emails = email_settings.get("recipients", [])
        
        # SMS configuration
        if sms_settings:
            config.sms_enabled = sms_settings.get("enabled", False)
            config.twilio_account_sid = sms_settings.get("account_sid", "")
            config.twilio_auth_token = sms_settings.get("auth_token", "")
            config.twilio_phone_number = sms_settings.get("phone_number", "")
            config.recipient_phones = sms_settings.get("recipients", [])
        
        # Webhook configuration
        if webhook_settings:
            config.discord_enabled = webhook_settings.get("discord_enabled", False)
            config.discord_webhook_url = webhook_settings.get("discord_url", "")
            config.slack_enabled = webhook_settings.get("slack_enabled", False)
            config.slack_webhook_url = webhook_settings.get("slack_url", "")
            config.webhook_enabled = webhook_settings.get("custom_enabled", False)
            config.webhook_url = webhook_settings.get("custom_url", "")
        
        return config
    
    def save_config(self, config: EnhancedTradingConfig, name: str):
        """Save configuration to file"""
        
        config_file = self.config_dir / f"{name}.json"
        
        try:
            config_dict = asdict(config)
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Saved configuration: {name}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def load_config(self, name: str) -> Optional[EnhancedTradingConfig]:
        """Load configuration from file"""
        
        config_file = self.config_dir / f"{name}.json"
        
        if not config_file.exists():
            logger.warning(f"Configuration file not found: {name}")
            return None
        
        try:
            with open(config_file, 'r') as f:
                config_dict = json.load(f)
            
            config = EnhancedTradingConfig(**config_dict)
            logger.info(f"Loaded configuration: {name}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return None
    
    def get_recommended_template(self, 
                               experience_level: str = "beginner",
                               risk_tolerance: str = "low",
                               trading_style: str = "long_term") -> str:
        """Get recommended template based on user profile"""
        
        if experience_level == "beginner" or risk_tolerance == "low":
            return "conservative"
        elif trading_style == "scalping":
            return "scalping"
        elif trading_style == "swing":
            return "swing"
        elif risk_tolerance == "high":
            return "aggressive"
        else:
            return "moderate"
    
    def validate_config(self, config: EnhancedTradingConfig) -> List[str]:
        """Validate configuration and return any issues"""
        
        issues = []
        
        # Check required fields
        if not config.api_key:
            issues.append("API key is required")
        if not config.api_secret:
            issues.append("API secret is required")
        if not config.trading_pair:
            issues.append("Trading pair is required")
        
        # Check risk management
        if config.max_position_size_percent <= 0 or config.max_position_size_percent > 10:
            issues.append("Position size should be between 0 and 10%")
        
        if config.base_stop_loss_percent <= 0 or config.base_stop_loss_percent > 20:
            issues.append("Stop loss should be between 0 and 20%")
        
        if config.base_take_profit_percent <= config.base_stop_loss_percent:
            issues.append("Take profit should be greater than stop loss")
        
        # Check technical parameters
        if config.rsi_period < 5 or config.rsi_period > 50:
            issues.append("RSI period should be between 5 and 50")
        
        if config.ema_short >= config.ema_medium:
            issues.append("Short EMA should be less than medium EMA")
        
        if config.ema_medium >= config.ema_long:
            issues.append("Medium EMA should be less than long EMA")
        
        return issues
