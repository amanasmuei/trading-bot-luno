"""
Enhanced Trading Bot Configuration
Improved settings for the advanced trading strategy
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class EnhancedTradingConfig:
    """Enhanced trading bot configuration settings"""

    # Luno API Configuration
    api_key: str = os.getenv("LUNO_API_KEY", "")
    api_secret: str = os.getenv("LUNO_API_SECRET", "")

    # Trading Parameters
    trading_pair: str = os.getenv("TRADING_PAIR", "XBTMYR")
    base_currency: str = ""
    counter_currency: str = ""

    # Enhanced Risk Management
    max_position_size_percent: float = (
        1.5  # Max 1.5% of portfolio per trade (more conservative)
    )
    base_stop_loss_percent: float = (
        3.0  # 3% base stop loss (wider for crypto volatility)
    )
    base_take_profit_percent: float = 6.0  # 6% base take profit (better risk-reward)
    max_daily_trades: int = 5  # Allow more trades with better strategy
    min_risk_reward_ratio: float = 1.5  # Minimum 1.5:1 risk-reward

    # Dynamic position sizing
    volatility_position_scaling: bool = True  # Scale position size based on volatility
    min_position_multiplier: float = 0.3  # Minimum position size multiplier
    max_position_multiplier: float = 1.5  # Maximum position size multiplier

    # Technical Analysis Parameters
    rsi_period: int = 14
    rsi_oversold: float = 30
    rsi_overbought: float = 70
    rsi_extreme_oversold: float = 20  # For stronger signals
    rsi_extreme_overbought: float = 80  # For stronger signals

    # Moving Averages
    ema_short: int = 9
    ema_medium: int = 21
    ema_long: int = 50
    sma_trend: int = 200  # Long-term trend filter

    # MACD Parameters
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    # Bollinger Bands
    bollinger_period: int = 20
    bollinger_std: float = 2.0

    # ATR for volatility-based stops
    atr_period: int = 14
    atr_stop_multiplier: float = 2.0
    atr_target_multiplier: float = 3.0

    # Signal Confidence Thresholds
    min_confidence_buy: float = 0.6  # Minimum confidence for buy signals
    min_confidence_sell: float = 0.6  # Minimum confidence for sell signals
    strong_signal_threshold: float = 0.8  # Threshold for strong signals

    # Volume Analysis
    volume_confirmation_threshold: float = 1.2  # 20% above average volume
    volume_period: int = 10  # Period for volume moving average

    # Market Regime Filters
    trend_filter_enabled: bool = True  # Only trade in direction of main trend
    volatility_filter_enabled: bool = True  # Adjust strategy based on volatility

    # Time-based filters
    min_time_between_trades: int = 1800  # 30 minutes minimum between trades

    # Bot Operation
    check_interval: int = 30  # Check every 30 seconds (more responsive)
    dry_run: bool = True  # Start in simulation mode
    log_level: str = "INFO"

    # Dashboard Configuration
    dashboard_host: str = os.getenv(
        "DASHBOARD_HOST", "0.0.0.0"
    )  # Allow external access by default
    dashboard_port: int = int(os.getenv("DASHBOARD_PORT", "5003"))

    # Backtesting and Performance
    track_performance: bool = True
    save_trade_history: bool = True
    performance_report_interval: int = 86400  # Daily performance reports

    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        # Parse trading pair to extract base and counter currencies
        if self.trading_pair and not self.base_currency:
            self.base_currency, self.counter_currency = self._parse_trading_pair(
                self.trading_pair
            )

    def _parse_trading_pair(self, pair: str) -> tuple:
        """Parse trading pair string to extract base and counter currencies"""
        # Common Luno trading pairs
        pair_mappings = {
            "XBTMYR": ("XBT", "MYR"),
            "XBTZAR": ("XBT", "ZAR"),
            "XBTEUR": ("XBT", "EUR"),
            "XBTGBP": ("XBT", "GBP"),
            "XBTNGN": ("XBT", "NGN"),
            "XBTUGX": ("XBT", "UGX"),
            "ETHMYR": ("ETH", "MYR"),
            "ETHZAR": ("ETH", "ZAR"),
            "ETHXBT": ("ETH", "XBT"),
            "LTCMYR": ("LTC", "MYR"),
            "LTCZAR": ("LTC", "ZAR"),
            "LTCXBT": ("LTC", "XBT"),
            "BCHMYR": ("BCH", "MYR"),
            "BCHZAR": ("BCH", "ZAR"),
            "BCHXBT": ("BCH", "XBT"),
        }

        if pair in pair_mappings:
            return pair_mappings[pair]

        # Fallback: try to parse manually (assumes 3-letter currencies)
        if len(pair) == 6:
            return pair[:3], pair[3:]

        # Default fallback
        return "XBT", "MYR"


# Enhanced Trading Signals Configuration
ENHANCED_TRADING_SIGNALS = {
    "VERY_STRONG_BUY": {
        "weight": 5,
        "conditions": [
            "strong_uptrend_alignment",
            "rsi_oversold_no_divergence",
            "macd_bullish_momentum",
            "volume_bullish_confirmation",
            "near_dynamic_support",
            "market_regime_bullish",
        ],
        "min_confidence": 0.8,
        "position_multiplier": 1.3,
    },
    "STRONG_BUY": {
        "weight": 4,
        "conditions": [
            "uptrend_alignment",
            "rsi_favorable",
            "macd_bullish",
            "volume_confirmation",
        ],
        "min_confidence": 0.65,
        "position_multiplier": 1.1,
    },
    "MODERATE_BUY": {
        "weight": 3,
        "conditions": ["short_term_bullish", "momentum_positive", "support_level"],
        "min_confidence": 0.5,
        "position_multiplier": 0.8,
    },
    "VERY_STRONG_SELL": {
        "weight": 5,
        "conditions": [
            "strong_downtrend_alignment",
            "rsi_overbought_no_divergence",
            "macd_bearish_momentum",
            "volume_bearish_confirmation",
            "near_dynamic_resistance",
            "market_regime_bearish",
        ],
        "min_confidence": 0.8,
        "position_multiplier": 1.3,
    },
    "STRONG_SELL": {
        "weight": 4,
        "conditions": [
            "downtrend_alignment",
            "rsi_unfavorable",
            "macd_bearish",
            "volume_confirmation",
        ],
        "min_confidence": 0.65,
        "position_multiplier": 1.1,
    },
    "MODERATE_SELL": {
        "weight": 3,
        "conditions": ["short_term_bearish", "momentum_negative", "resistance_level"],
        "min_confidence": 0.5,
        "position_multiplier": 0.8,
    },
    "WAIT": {
        "weight": 0,
        "conditions": [
            "mixed_signals",
            "low_confidence",
            "insufficient_volume",
            "consolidation_range",
            "high_volatility_risk",
        ],
    },
}

# Enhanced Risk Management Rules
RISK_MANAGEMENT_RULES = {
    "position_sizing": {
        "base_percent": 1.5,  # Base position size as % of portfolio
        "volatility_adjustment": True,
        "confidence_scaling": True,  # Scale position with signal confidence
        "max_portfolio_risk": 5.0,  # Maximum total portfolio risk
    },
    "stop_loss": {
        "method": "dynamic_atr",  # Use ATR-based dynamic stops
        "min_percent": 2.0,  # Minimum stop loss
        "max_percent": 6.0,  # Maximum stop loss
        "trailing_enabled": True,  # Enable trailing stops
        "breakeven_threshold": 2.0,  # Move to breakeven after 2% profit
    },
    "take_profit": {
        "method": "multiple_targets",  # Use multiple take profit levels
        "target_1_ratio": 2.0,  # First target at 2:1 RR
        "target_2_ratio": 3.5,  # Second target at 3.5:1 RR
        "target_3_ratio": 5.0,  # Third target at 5:1 RR
        "partial_close_percent": [50, 30, 20],  # Close percentages at each target
    },
    "daily_limits": {
        "max_trades": 5,
        "max_loss_percent": 3.0,  # Stop trading if daily loss exceeds 3%
        "max_consecutive_losses": 3,  # Stop after 3 consecutive losses
    },
}

# Market Regime Configuration
MARKET_REGIMES = {
    "TRENDING_UP": {
        "bias": "bullish",
        "preferred_signals": ["BUY"],
        "risk_adjustment": 0.9,  # Slightly less risk in trending markets
        "confidence_bonus": 0.1,  # Boost confidence in trend direction
    },
    "TRENDING_DOWN": {
        "bias": "bearish",
        "preferred_signals": ["SELL"],
        "risk_adjustment": 0.9,
        "confidence_bonus": 0.1,
    },
    "RANGING": {
        "bias": "neutral",
        "preferred_signals": ["BUY", "SELL"],  # Both directions OK
        "risk_adjustment": 0.8,  # Reduce risk in ranging markets
        "confidence_penalty": 0.1,  # Reduce confidence in choppy markets
    },
    "HIGH_VOLATILITY": {
        "bias": "cautious",
        "preferred_signals": [],  # Wait for clear signals
        "risk_adjustment": 0.6,  # Significantly reduce risk
        "confidence_penalty": 0.2,  # Require higher confidence
        "position_multiplier": 0.7,
    },
    "LOW_VOLATILITY": {
        "bias": "opportunistic",
        "preferred_signals": ["BUY", "SELL"],
        "risk_adjustment": 1.1,  # Slightly increase risk
        "confidence_bonus": 0.05,
    },
}

# Supported Luno Trading Pairs (Enhanced)
ENHANCED_SUPPORTED_PAIRS = {
    # Bitcoin pairs
    "XBTMYR": {
        "name": "Bitcoin/Malaysian Ringgit",
        "min_volume": 0.0001,
        "tick_size": 1.0,
        "volatility_class": "high",
        "preferred_timeframes": ["1h", "4h", "1d"],
    },
    "XBTZAR": {
        "name": "Bitcoin/South African Rand",
        "min_volume": 0.0001,
        "tick_size": 1.0,
        "volatility_class": "high",
        "preferred_timeframes": ["1h", "4h", "1d"],
    },
    "XBTEUR": {
        "name": "Bitcoin/Euro",
        "min_volume": 0.0001,
        "tick_size": 0.01,
        "volatility_class": "high",
        "preferred_timeframes": ["1h", "4h", "1d"],
    },
    "XBTGBP": {
        "name": "Bitcoin/British Pound",
        "min_volume": 0.0001,
        "tick_size": 0.01,
        "volatility_class": "high",
        "preferred_timeframes": ["1h", "4h", "1d"],
    },
    # Ethereum pairs
    "ETHMYR": {
        "name": "Ethereum/Malaysian Ringgit",
        "min_volume": 0.001,
        "tick_size": 0.1,
        "volatility_class": "high",
        "preferred_timeframes": ["1h", "4h", "1d"],
    },
    "ETHZAR": {
        "name": "Ethereum/South African Rand",
        "min_volume": 0.001,
        "tick_size": 0.1,
        "volatility_class": "high",
        "preferred_timeframes": ["1h", "4h", "1d"],
    },
    "ETHXBT": {
        "name": "Ethereum/Bitcoin",
        "min_volume": 0.001,
        "tick_size": 0.00001,
        "volatility_class": "medium",
        "preferred_timeframes": ["4h", "1d"],
    },
}

# Trading Hours (Enhanced with timezone support)
ENHANCED_TRADING_HOURS = {
    "enabled": False,  # Crypto trades 24/7 by default
    "preferred_hours": {
        "start": 8,  # 8 AM
        "end": 22,  # 10 PM
    },
    "high_activity_periods": [
        {"start": 9, "end": 11, "description": "Asian market open"},
        {"start": 14, "end": 16, "description": "European market open"},
        {"start": 21, "end": 23, "description": "US market open"},
    ],
    "pair_specific": {
        "XBTMYR": {"timezone": "Asia/Kuala_Lumpur"},
        "XBTZAR": {"timezone": "Africa/Johannesburg"},
        "XBTEUR": {"timezone": "Europe/London"},
        "XBTGBP": {"timezone": "Europe/London"},
    },
}

# Performance Tracking Configuration
PERFORMANCE_CONFIG = {
    "metrics": [
        "total_return",
        "sharpe_ratio",
        "max_drawdown",
        "win_rate",
        "avg_win_loss_ratio",
        "profit_factor",
        "total_trades",
        "avg_trade_duration",
    ],
    "reporting": {
        "daily_summary": True,
        "weekly_report": True,
        "monthly_analysis": True,
        "export_to_csv": True,
        "include_charts": True,
    },
    "benchmarks": {
        "buy_and_hold": True,
        "market_index": "BTC",
        "risk_free_rate": 0.03,  # 3% annual risk-free rate
    },
}
