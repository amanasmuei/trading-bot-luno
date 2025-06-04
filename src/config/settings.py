"""
Luno Trading Bot Configuration
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class TradingConfig:
    """Luno trading bot configuration settings"""

    # Luno API Configuration
    api_key: str = os.getenv("LUNO_API_KEY", "")
    api_secret: str = os.getenv("LUNO_API_SECRET", "")

    # Trading Parameters
    trading_pair: str = os.getenv("TRADING_PAIR", "XBTMYR")
    base_currency: str = ""
    counter_currency: str = ""

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
        # Parse trading pair to extract base and counter currencies
        if self.trading_pair and not self.base_currency:
            self.base_currency, self.counter_currency = self._parse_trading_pair(
                self.trading_pair
            )

        # Set default support/resistance levels based on trading pair
        if self.resistance_levels is None:
            self.resistance_levels = self._get_default_resistance_levels()

        if self.support_levels is None:
            self.support_levels = self._get_default_support_levels()

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

    def _get_default_resistance_levels(self) -> list:
        """Get default resistance levels based on trading pair"""
        defaults = {
            "XBTMYR": [463000, 465001, 468000, 475001],
            "XBTZAR": [800000, 820000, 850010, 900000],
            "XBTEUR": [35001, 36000, 37000, 40000],
            "XBTGBP": [30000, 31000, 32000, 35001],
            "ETHXBT": [0.065, 0.070, 0.075, 0.080],
            "LTCXBT": [0.0025, 0.0030, 0.0035, 0.0040],
        }
        return defaults.get(self.trading_pair, [50010, 52000, 55001, 60000])

    def _get_default_support_levels(self) -> list:
        """Get default support levels based on trading pair"""
        defaults = {
            "XBTMYR": [458000, 455001, 453000, 445001],
            "XBTZAR": [750010, 730000, 700000, 650010],
            "XBTEUR": [32000, 31000, 30000, 28000],
            "XBTGBP": [27000, 26000, 25001, 23000],
            "ETHXBT": [0.055, 0.050, 0.045, 0.040],
            "LTCXBT": [0.0020, 0.0018, 0.0015, 0.0012],
        }
        return defaults.get(self.trading_pair, [45001, 42000, 40000, 35001])


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

# Supported Luno Trading Pairs
SUPPORTED_PAIRS = {
    # Bitcoin pairs
    "XBTMYR": {"name": "Bitcoin/Malaysian Ringgit", "min_volume": 0.0001},
    "XBTZAR": {"name": "Bitcoin/South African Rand", "min_volume": 0.0001},
    "XBTEUR": {"name": "Bitcoin/Euro", "min_volume": 0.0001},
    "XBTGBP": {"name": "Bitcoin/British Pound", "min_volume": 0.0001},
    "XBTNGN": {"name": "Bitcoin/Nigerian Naira", "min_volume": 0.0001},
    "XBTUGX": {"name": "Bitcoin/Ugandan Shilling", "min_volume": 0.0001},
    # Ethereum pairs
    "ETHMYR": {"name": "Ethereum/Malaysian Ringgit", "min_volume": 0.001},
    "ETHZAR": {"name": "Ethereum/South African Rand", "min_volume": 0.001},
    "ETHXBT": {"name": "Ethereum/Bitcoin", "min_volume": 0.001},
    # Litecoin pairs
    "LTCMYR": {"name": "Litecoin/Malaysian Ringgit", "min_volume": 0.01},
    "LTCZAR": {"name": "Litecoin/South African Rand", "min_volume": 0.01},
    "LTCXBT": {"name": "Litecoin/Bitcoin", "min_volume": 0.01},
    # Bitcoin Cash pairs
    "BCHMYR": {"name": "Bitcoin Cash/Malaysian Ringgit", "min_volume": 0.001},
    "BCHZAR": {"name": "Bitcoin Cash/South African Rand", "min_volume": 0.001},
    "BCHXBT": {"name": "Bitcoin Cash/Bitcoin", "min_volume": 0.001},
}

# Market Hours (Luno operates 24/7 but we can set preferred trading hours)
TRADING_HOURS = {
    "enabled": True,  # Set to False for 24/7 trading
    "start": 8,  # 8 AM
    "end": 22,  # 10 PM
    "timezone": "UTC",  # Default timezone, can be overridden per pair
    "pair_specific": {
        "XBTMYR": {"timezone": "Asia/Kuala_Lumpur"},
        "XBTZAR": {"timezone": "Africa/Johannesburg"},
        "XBTEUR": {"timezone": "Europe/London"},
        "XBTGBP": {"timezone": "Europe/London"},
    },
}
