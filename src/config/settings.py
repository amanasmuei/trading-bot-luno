"""
Trading Bot Configuration
"""

import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TradingConfig:
    """Trading bot configuration settings"""

    # Luno API Configuration
    api_key: str = os.getenv("LUNO_API_KEY", "")
    api_secret: str = os.getenv("LUNO_API_SECRET", "")

    # Trading Parameters
    trading_pair: str = "XBTMYR"
    base_currency: str = "XBT"
    counter_currency: str = "MYR"

    # Risk Management
    max_position_size_percent: float = 2.0  # Max 2% of portfolio per trade
    stop_loss_percent: float = 1.5  # 1.5% stop loss
    take_profit_percent: float = 3.0  # 3% take profit
    max_daily_trades: int = 3

    # Technical Analysis Parameters
    rsi_period: int = 14
    rsi_oversold: float = 30
    rsi_overbought: float = 70

    ema_short: int = 9
    ema_long: int = 21

    bollinger_period: int = 20
    bollinger_std: float = 2.0

    # Key Price Levels (from our analysis)
    resistance_levels: list = None
    support_levels: list = None

    # Bot Operation
    check_interval: int = 60  # Check every 60 seconds
    dry_run: bool = True  # Start in simulation mode
    log_level: str = "INFO"

    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        if self.resistance_levels is None:
            self.resistance_levels = [463000, 465000, 468000, 475000]

        if self.support_levels is None:
            self.support_levels = [458000, 455000, 453000, 445000]


# Trading Signals Configuration
TRADING_SIGNALS = {
    "STRONG_BUY": {
        "conditions": [
            "price_breaks_resistance",
            "volume_above_average",
            "rsi_not_overbought",
            "ema_bullish_cross",
        ],
        "confidence_threshold": 0.8,
    },
    "STRONG_SELL": {
        "conditions": [
            "price_breaks_support",
            "volume_above_average",
            "rsi_not_oversold",
            "ema_bearish_cross",
        ],
        "confidence_threshold": 0.8,
    },
    "WAIT": {"conditions": ["price_in_consolidation", "low_volume", "mixed_signals"]},
}

# Market Hours (Luno operates 24/7 but we can set preferred trading hours)
TRADING_HOURS = {
    "start": 8,  # 8 AM MYT
    "end": 22,  # 10 PM MYT
    "timezone": "Asia/Kuala_Lumpur",
}
