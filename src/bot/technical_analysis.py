"""
Technical Analysis Module for Trading Bot
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class TechnicalIndicators:
    """Container for technical analysis results"""

    rsi: float
    ema_short: float
    ema_long: float
    bollinger_upper: float
    bollinger_middle: float
    bollinger_lower: float
    macd: float
    macd_signal: float
    macd_histogram: float
    volume_sma: float
    current_price: float
    timestamp: datetime


class TechnicalAnalyzer:
    """Advanced technical analysis for cryptocurrency trading"""

    def __init__(self, config):
        self.config = config

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI if insufficient data

        prices_array = np.array(prices)
        deltas = np.diff(prices_array)

        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.mean(prices)

        prices_array = np.array(prices)
        alpha = 2 / (period + 1)

        ema = prices_array[0]
        for price in prices_array[1:]:
            ema = alpha * price + (1 - alpha) * ema

        return round(ema, 2)

    def calculate_bollinger_bands(
        self, prices: List[float], period: int = 20, std_dev: float = 2.0
    ) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands (upper, middle, lower)"""
        if len(prices) < period:
            mean_price = np.mean(prices)
            return mean_price, mean_price, mean_price

        prices_array = np.array(prices[-period:])
        sma = np.mean(prices_array)
        std = np.std(prices_array)

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)

        return round(upper, 2), round(sma, 2), round(lower, 2)

    def calculate_macd(
        self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[float, float, float]:
        """Calculate MACD, Signal line, and Histogram"""
        if len(prices) < slow:
            return 0.0, 0.0, 0.0

        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)

        macd_line = ema_fast - ema_slow

        # For signal line, we need MACD history - simplified version
        signal_line = macd_line * 0.8  # Simplified calculation
        histogram = macd_line - signal_line

        return round(macd_line, 2), round(signal_line, 2), round(histogram, 2)

    def analyze_market_data(
        self, candles: List[Dict], current_price: float, volume_data: List[float]
    ) -> TechnicalIndicators:
        """Perform comprehensive technical analysis"""

        # Extract price data
        closes = [float(candle["close"]) for candle in candles]
        highs = [float(candle["high"]) for candle in candles]
        lows = [float(candle["low"]) for candle in candles]
        volumes = [float(candle["volume"]) for candle in candles]

        # Calculate all indicators
        rsi = self.calculate_rsi(closes, self.config.rsi_period)
        ema_short = self.calculate_ema(closes, self.config.ema_short)
        ema_long = self.calculate_ema(closes, self.config.ema_long)

        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(closes)
        macd, macd_signal, macd_histogram = self.calculate_macd(closes)

        volume_sma = np.mean(volumes[-7:]) if len(volumes) >= 7 else np.mean(volumes)

        return TechnicalIndicators(
            rsi=rsi,
            ema_short=ema_short,
            ema_long=ema_long,
            bollinger_upper=bb_upper,
            bollinger_middle=bb_middle,
            bollinger_lower=bb_lower,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            volume_sma=volume_sma,
            current_price=current_price,
            timestamp=datetime.now(),
        )

    def generate_signals(
        self, indicators: TechnicalIndicators, current_volume: float
    ) -> Dict[str, any]:
        """Generate trading signals based on technical analysis"""

        signals = {
            "action": "WAIT",
            "confidence": 0.0,
            "reasons": [],
            "price_level": indicators.current_price,
            "stop_loss": None,
            "take_profit": None,
        }

        # Price level analysis
        price_above_resistance = any(
            indicators.current_price > level for level in self.config.resistance_levels
        )
        price_below_support = any(
            indicators.current_price < level for level in self.config.support_levels
        )

        # Volume analysis
        volume_above_average = current_volume > indicators.volume_sma * 1.2

        # Technical signals
        rsi_oversold = indicators.rsi < self.config.rsi_oversold
        rsi_overbought = indicators.rsi > self.config.rsi_overbought
        ema_bullish = indicators.ema_short > indicators.ema_long
        ema_bearish = indicators.ema_short < indicators.ema_long

        # MACD signals
        macd_bullish = indicators.macd > indicators.macd_signal
        macd_bearish = indicators.macd < indicators.macd_signal

        # Bollinger Bands position
        bb_squeeze = (
            indicators.bollinger_upper - indicators.bollinger_lower
        ) / indicators.bollinger_middle < 0.02
        price_near_upper_bb = (
            indicators.current_price > indicators.bollinger_upper * 0.98
        )
        price_near_lower_bb = (
            indicators.current_price < indicators.bollinger_lower * 1.02
        )

        confidence_score = 0.0

        # BULLISH CONDITIONS
        if (
            not rsi_overbought
            and ema_bullish
            and macd_bullish
            and volume_above_average
            and indicators.current_price > max(self.config.resistance_levels[:2])
        ):

            signals["action"] = "BUY"
            signals["reasons"].extend(
                [
                    "Price broke resistance",
                    "EMA bullish cross",
                    "MACD bullish",
                    "Volume confirmation",
                    f"RSI healthy at {indicators.rsi}",
                ]
            )
            confidence_score = 0.8
            signals["stop_loss"] = indicators.current_price * (
                1 - self.config.stop_loss_percent / 100
            )
            signals["take_profit"] = indicators.current_price * (
                1 + self.config.take_profit_percent / 100
            )

        # BEARISH CONDITIONS
        elif (
            not rsi_oversold
            and ema_bearish
            and macd_bearish
            and volume_above_average
            and indicators.current_price < min(self.config.support_levels[:2])
        ):

            signals["action"] = "SELL"
            signals["reasons"].extend(
                [
                    "Price broke support",
                    "EMA bearish cross",
                    "MACD bearish",
                    "Volume confirmation",
                    f"RSI healthy at {indicators.rsi}",
                ]
            )
            confidence_score = 0.8
            signals["stop_loss"] = indicators.current_price * (
                1 + self.config.stop_loss_percent / 100
            )
            signals["take_profit"] = indicators.current_price * (
                1 - self.config.take_profit_percent / 100
            )

        # CONSOLIDATION/WAIT CONDITIONS
        else:
            reasons = []
            if not volume_above_average:
                reasons.append("Low volume")
            if bb_squeeze:
                reasons.append("Bollinger Bands squeeze")
            if (
                self.config.support_levels[1]
                <= indicators.current_price
                <= self.config.resistance_levels[1]
            ):
                reasons.append("Price in consolidation range")
            if abs(indicators.rsi - 50) < 10:
                reasons.append("RSI neutral")

            signals["reasons"] = reasons if reasons else ["Mixed signals"]
            confidence_score = 0.2

        signals["confidence"] = confidence_score

        logger.info(
            f"Signal generated: {signals['action']} with {confidence_score:.1%} confidence"
        )
        logger.info(f"Reasons: {', '.join(signals['reasons'])}")

        return signals

    def get_market_sentiment(self, indicators: TechnicalIndicators) -> str:
        """Determine overall market sentiment"""

        bullish_signals = 0
        bearish_signals = 0

        # RSI sentiment
        if indicators.rsi > 60:
            bullish_signals += 1
        elif indicators.rsi < 40:
            bearish_signals += 1

        # EMA sentiment
        if indicators.ema_short > indicators.ema_long:
            bullish_signals += 1
        else:
            bearish_signals += 1

        # MACD sentiment
        if indicators.macd > indicators.macd_signal:
            bullish_signals += 1
        else:
            bearish_signals += 1

        # Bollinger Bands sentiment
        if indicators.current_price > indicators.bollinger_middle:
            bullish_signals += 1
        else:
            bearish_signals += 1

        if bullish_signals > bearish_signals + 1:
            return "BULLISH"
        elif bearish_signals > bullish_signals + 1:
            return "BEARISH"
        else:
            return "NEUTRAL"
