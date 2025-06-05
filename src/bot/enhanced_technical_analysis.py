"""
Enhanced Technical Analysis Module for Trading Bot
Advanced strategy with dynamic support/resistance, multiple timeframes, and smart signal logic
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


class SignalStrength(Enum):
    VERY_STRONG = 5
    STRONG = 4
    MODERATE = 3
    WEAK = 2
    VERY_WEAK = 1


@dataclass
class EnhancedTechnicalIndicators:
    """Enhanced container for technical analysis results"""

    # Basic indicators
    rsi: float
    rsi_divergence: bool

    # Moving averages
    ema_short: float
    ema_medium: float
    ema_long: float
    sma_200: float

    # Bollinger Bands
    bollinger_upper: float
    bollinger_middle: float
    bollinger_lower: float
    bollinger_width: float
    bollinger_position: float  # 0-1 where price is within bands

    # MACD
    macd: float
    macd_signal: float
    macd_histogram: float
    macd_divergence: bool

    # Volume indicators
    volume_sma: float
    volume_ratio: float
    volume_trend: str

    # Volatility
    atr: float  # Average True Range
    volatility_percentile: float

    # Dynamic Support/Resistance
    dynamic_support: List[float]
    dynamic_resistance: List[float]
    nearest_support: float
    nearest_resistance: float

    # Market structure
    market_regime: MarketRegime
    trend_strength: float

    # Price action
    current_price: float
    price_momentum: float
    higher_highs: bool
    higher_lows: bool

    timestamp: datetime


@dataclass
class TradingSignal:
    """Enhanced trading signal with detailed analysis"""

    action: str  # BUY, SELL, WAIT
    confidence: float  # 0.0 to 1.0
    strength: SignalStrength
    primary_reasons: List[str]
    supporting_factors: List[str]
    risk_factors: List[str]

    # Entry/Exit levels
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float]
    take_profit_3: Optional[float]

    # Risk management
    risk_reward_ratio: float
    position_size_multiplier: float  # 0.5 to 2.0

    # Market context
    market_regime: MarketRegime
    volatility_adjusted: bool


class EnhancedTechnicalAnalyzer:
    """Advanced technical analysis with dynamic strategies"""

    def __init__(self, config):
        self.config = config
        self.price_history = []
        self.volume_history = []
        self.indicator_history = []

    def calculate_atr(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14,
    ) -> float:
        """Calculate Average True Range for volatility measurement"""
        if len(highs) < period + 1:
            return np.mean(highs) - np.mean(lows)

        true_ranges = []
        for i in range(1, len(highs)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i - 1])
            low_close = abs(lows[i] - closes[i - 1])
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)

        return (
            np.mean(true_ranges[-period:])
            if len(true_ranges) >= period
            else np.mean(true_ranges)
        )

    def calculate_dynamic_support_resistance(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 20,
    ) -> Tuple[List[float], List[float]]:
        """Calculate dynamic support and resistance levels using pivot points"""
        if len(highs) < period:
            avg_price = np.mean(closes)
            return [avg_price * 0.98], [avg_price * 1.02]

        # Find pivot highs and lows
        resistance_levels = []
        support_levels = []

        lookback = 5  # Look 5 periods back and forward for pivots

        for i in range(lookback, len(highs) - lookback):
            # Pivot high
            if all(
                highs[i] >= highs[j]
                for j in range(i - lookback, i + lookback + 1)
                if j != i
            ):
                resistance_levels.append(highs[i])

            # Pivot low
            if all(
                lows[i] <= lows[j]
                for j in range(i - lookback, i + lookback + 1)
                if j != i
            ):
                support_levels.append(lows[i])

        # Keep only recent and significant levels
        current_price = closes[-1]

        # Filter resistance levels above current price
        resistance_levels = [r for r in resistance_levels if r > current_price]
        resistance_levels = sorted(resistance_levels)[:4]  # Top 4 resistance levels

        # Filter support levels below current price
        support_levels = [s for s in support_levels if s < current_price]
        support_levels = sorted(support_levels, reverse=True)[
            :4
        ]  # Top 4 support levels

        return support_levels, resistance_levels

    def detect_market_regime(
        self, prices: List[float], volumes: List[float]
    ) -> MarketRegime:
        """Detect current market regime"""
        if len(prices) < 20:
            return MarketRegime.RANGING

        # Calculate trend strength
        ema_20 = self.calculate_ema(prices, 20)
        ema_50 = self.calculate_ema(prices, 50)

        price_change_20 = (
            (prices[-1] - prices[-20]) / prices[-20] if len(prices) >= 20 else 0
        )

        # Calculate volatility
        price_std = np.std(prices[-20:])
        avg_price = np.mean(prices[-20:])
        volatility = price_std / avg_price

        # Determine regime
        if abs(price_change_20) > 0.05:  # 5% move in 20 periods
            if price_change_20 > 0:
                return MarketRegime.TRENDING_UP
            else:
                return MarketRegime.TRENDING_DOWN
        elif volatility > 0.03:  # High volatility
            return MarketRegime.HIGH_VOLATILITY
        elif volatility < 0.01:  # Low volatility
            return MarketRegime.LOW_VOLATILITY
        else:
            return MarketRegime.RANGING

    def calculate_rsi_with_divergence(
        self, prices: List[float], period: int = 14
    ) -> Tuple[float, bool]:
        """Calculate RSI and detect divergence"""
        rsi = self.calculate_rsi(prices, period)

        # Simple divergence detection
        divergence = False
        if len(prices) >= 40:  # Need enough data
            recent_prices = prices[-20:]
            older_prices = prices[-40:-20]

            recent_high = max(recent_prices)
            older_high = max(older_prices)

            recent_rsi = self.calculate_rsi(prices[-20:], min(period, 14))
            older_rsi = self.calculate_rsi(prices[-40:-20], min(period, 14))

            # Bearish divergence: price higher high, RSI lower high
            if recent_high > older_high and recent_rsi < older_rsi:
                divergence = True
            # Bullish divergence: price lower low, RSI higher low
            elif recent_high < older_high and recent_rsi > older_rsi:
                divergence = True

        return rsi, divergence

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0

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

    def calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return np.mean(prices)

        return np.mean(prices[-period:])

    def calculate_bollinger_bands(
        self, prices: List[float], period: int = 20, std_dev: float = 2.0
    ) -> Tuple[float, float, float, float, float]:
        """Calculate enhanced Bollinger Bands with position and width"""
        if len(prices) < period:
            mean_price = np.mean(prices)
            return mean_price, mean_price, mean_price, 0.0, 0.5

        prices_array = np.array(prices[-period:])
        sma = np.mean(prices_array)
        std = np.std(prices_array)

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)

        # Calculate band width (volatility indicator)
        width = (upper - lower) / sma

        # Calculate price position within bands (0 = lower band, 1 = upper band)
        current_price = prices[-1]
        if upper == lower:
            position = 0.5
        else:
            position = (current_price - lower) / (upper - lower)
            position = max(0, min(1, position))  # Clamp between 0 and 1

        return (
            round(upper, 2),
            round(sma, 2),
            round(lower, 2),
            round(width, 4),
            round(position, 3),
        )

    def calculate_macd_with_divergence(
        self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[float, float, float, bool]:
        """Calculate MACD with divergence detection"""
        if len(prices) < slow:
            return 0.0, 0.0, 0.0, False

        # Calculate MACD
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow

        # Simple signal line calculation (should be EMA of MACD in production)
        signal_line = macd_line * 0.8
        histogram = macd_line - signal_line

        # Divergence detection (simplified)
        divergence = False
        if len(prices) >= 40:
            recent_macd = self.calculate_ema(prices[-20:], fast) - self.calculate_ema(
                prices[-20:], slow
            )
            older_macd = self.calculate_ema(prices[-40:-20], fast) - self.calculate_ema(
                prices[-40:-20], slow
            )

            recent_price_high = max(prices[-20:])
            older_price_high = max(prices[-40:-20])

            # Simple divergence check
            if recent_price_high > older_price_high and recent_macd < older_macd:
                divergence = True
            elif recent_price_high < older_price_high and recent_macd > older_macd:
                divergence = True

        return (
            round(macd_line, 2),
            round(signal_line, 2),
            round(histogram, 2),
            divergence,
        )

    def analyze_volume_trend(
        self, volumes: List[float], prices: List[float]
    ) -> Tuple[float, str]:
        """Analyze volume trend and relationship with price"""
        if len(volumes) < 10:
            return 1.0, "NEUTRAL"

        recent_volume = np.mean(volumes[-5:])
        older_volume = np.mean(volumes[-10:-5])

        volume_ratio = recent_volume / older_volume if older_volume > 0 else 1.0

        # Determine volume trend
        recent_price_change = (
            (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0
        )

        if volume_ratio > 1.2 and recent_price_change > 0:
            trend = "BULLISH_VOLUME"
        elif volume_ratio > 1.2 and recent_price_change < 0:
            trend = "BEARISH_VOLUME"
        elif volume_ratio < 0.8:
            trend = "DECLINING_VOLUME"
        else:
            trend = "NEUTRAL"

        return round(volume_ratio, 2), trend

    def calculate_price_momentum(self, prices: List[float], period: int = 10) -> float:
        """Calculate price momentum"""
        if len(prices) < period:
            return 0.0

        momentum = (prices[-1] - prices[-period]) / prices[-period]
        return round(momentum, 4)

    def detect_market_structure(
        self, highs: List[float], lows: List[float]
    ) -> Tuple[bool, bool]:
        """Detect if market is making higher highs and higher lows"""
        if len(highs) < 6:
            return False, False

        # Check last 3 swings for higher highs
        recent_highs = highs[-3:]
        higher_highs = all(
            recent_highs[i] > recent_highs[i - 1] for i in range(1, len(recent_highs))
        )

        # Check last 3 swings for higher lows
        recent_lows = lows[-3:]
        higher_lows = all(
            recent_lows[i] > recent_lows[i - 1] for i in range(1, len(recent_lows))
        )

        return higher_highs, higher_lows

    def analyze_market_data(
        self, candles: List[Dict], current_price: float, volume_data: List[float]
    ) -> EnhancedTechnicalIndicators:
        """Perform comprehensive enhanced technical analysis"""

        # Extract price data
        closes = [float(candle["close"]) for candle in candles]
        highs = [float(candle["high"]) for candle in candles]
        lows = [float(candle["low"]) for candle in candles]
        volumes = [float(candle["volume"]) for candle in candles]

        # Basic indicators
        rsi, rsi_divergence = self.calculate_rsi_with_divergence(closes)

        # Moving averages
        ema_short = self.calculate_ema(closes, 9)
        ema_medium = self.calculate_ema(closes, 21)
        ema_long = self.calculate_ema(closes, 50)
        sma_200 = self.calculate_sma(closes, 200)

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower, bb_width, bb_position = (
            self.calculate_bollinger_bands(closes)
        )

        # MACD
        macd, macd_signal, macd_histogram, macd_divergence = (
            self.calculate_macd_with_divergence(closes)
        )

        # Volume analysis
        volume_sma = np.mean(volumes[-7:]) if len(volumes) >= 7 else np.mean(volumes)
        volume_ratio, volume_trend = self.analyze_volume_trend(volumes, closes)

        # Volatility
        atr = self.calculate_atr(highs, lows, closes)
        volatility_percentile = 0.5  # Simplified - would need longer history

        # Dynamic Support/Resistance
        support_levels, resistance_levels = self.calculate_dynamic_support_resistance(
            highs, lows, closes
        )
        nearest_support = (
            max(support_levels) if support_levels else current_price * 0.95
        )
        nearest_resistance = (
            min(resistance_levels) if resistance_levels else current_price * 1.05
        )

        # Market regime
        market_regime = self.detect_market_regime(closes, volumes)

        # Price momentum and structure
        price_momentum = self.calculate_price_momentum(closes)
        higher_highs, higher_lows = self.detect_market_structure(highs, lows)

        # Trend strength (simplified)
        trend_strength = abs(price_momentum) * 10  # Scale to 0-1 roughly
        trend_strength = min(1.0, trend_strength)

        return EnhancedTechnicalIndicators(
            rsi=rsi,
            rsi_divergence=rsi_divergence,
            ema_short=ema_short,
            ema_medium=ema_medium,
            ema_long=ema_long,
            sma_200=sma_200,
            bollinger_upper=bb_upper,
            bollinger_middle=bb_middle,
            bollinger_lower=bb_lower,
            bollinger_width=bb_width,
            bollinger_position=bb_position,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            macd_divergence=macd_divergence,
            volume_sma=volume_sma,
            volume_ratio=volume_ratio,
            volume_trend=volume_trend,
            atr=atr,
            volatility_percentile=volatility_percentile,
            dynamic_support=support_levels,
            dynamic_resistance=resistance_levels,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            market_regime=market_regime,
            trend_strength=trend_strength,
            current_price=current_price,
            price_momentum=price_momentum,
            higher_highs=higher_highs,
            higher_lows=higher_lows,
            timestamp=datetime.now(),
        )

    def generate_enhanced_signals(
        self, indicators: EnhancedTechnicalIndicators, current_volume: float
    ) -> TradingSignal:
        """Generate enhanced trading signals with advanced logic"""

        # Initialize signal
        signal = TradingSignal(
            action="WAIT",
            confidence=0.0,
            strength=SignalStrength.WEAK,
            primary_reasons=[],
            supporting_factors=[],
            risk_factors=[],
            entry_price=indicators.current_price,
            stop_loss=0.0,
            take_profit_1=0.0,
            take_profit_2=None,
            take_profit_3=None,
            risk_reward_ratio=0.0,
            position_size_multiplier=1.0,
            market_regime=indicators.market_regime,
            volatility_adjusted=True,
        )

        # Score different factors
        bullish_score = 0
        bearish_score = 0
        confidence_factors = []

        # 1. Trend Analysis (30% weight)
        if indicators.ema_short > indicators.ema_medium > indicators.ema_long:
            bullish_score += 3
            confidence_factors.append("Strong uptrend (EMA alignment)")
        elif indicators.ema_short < indicators.ema_medium < indicators.ema_long:
            bearish_score += 3
            confidence_factors.append("Strong downtrend (EMA alignment)")
        elif indicators.ema_short > indicators.ema_medium:
            bullish_score += 1
            confidence_factors.append("Short-term bullish (EMA 9 > 21)")
        elif indicators.ema_short < indicators.ema_medium:
            bearish_score += 1
            confidence_factors.append("Short-term bearish (EMA 9 < 21)")

        # 2. Momentum Analysis (25% weight)
        if indicators.rsi < 30 and not indicators.rsi_divergence:
            bullish_score += 2
            confidence_factors.append("RSI oversold")
        elif indicators.rsi > 70 and not indicators.rsi_divergence:
            bearish_score += 2
            confidence_factors.append("RSI overbought")
        elif 40 <= indicators.rsi <= 60:
            confidence_factors.append("RSI neutral")

        if indicators.macd > indicators.macd_signal and indicators.macd_histogram > 0:
            bullish_score += 2
            confidence_factors.append("MACD bullish")
        elif indicators.macd < indicators.macd_signal and indicators.macd_histogram < 0:
            bearish_score += 2
            confidence_factors.append("MACD bearish")

        # 3. Price Action Analysis (20% weight)
        if indicators.higher_highs and indicators.higher_lows:
            bullish_score += 2
            confidence_factors.append("Higher highs and higher lows")
        elif not indicators.higher_highs and not indicators.higher_lows:
            bearish_score += 2
            confidence_factors.append("Lower highs and lower lows")

        # Support/Resistance levels
        distance_to_support = (
            indicators.current_price - indicators.nearest_support
        ) / indicators.current_price
        distance_to_resistance = (
            indicators.nearest_resistance - indicators.current_price
        ) / indicators.current_price

        if distance_to_support < 0.02:  # Within 2% of support
            bullish_score += 1
            confidence_factors.append("Near dynamic support")
        elif distance_to_resistance < 0.02:  # Within 2% of resistance
            bearish_score += 1
            confidence_factors.append("Near dynamic resistance")

        # 4. Volume Analysis (15% weight)
        if indicators.volume_trend == "BULLISH_VOLUME":
            bullish_score += 1
            confidence_factors.append("Bullish volume confirmation")
        elif indicators.volume_trend == "BEARISH_VOLUME":
            bearish_score += 1
            confidence_factors.append("Bearish volume confirmation")
        elif indicators.volume_trend == "DECLINING_VOLUME":
            signal.risk_factors.append("Declining volume")

        # 5. Market Regime Adjustment (10% weight)
        if indicators.market_regime == MarketRegime.TRENDING_UP:
            bullish_score += 1
            confidence_factors.append("Trending up market")
        elif indicators.market_regime == MarketRegime.TRENDING_DOWN:
            bearish_score += 1
            confidence_factors.append("Trending down market")
        elif indicators.market_regime == MarketRegime.HIGH_VOLATILITY:
            signal.risk_factors.append("High volatility environment")
            signal.position_size_multiplier = 0.7  # Reduce position size

        # Divergence penalties
        if indicators.rsi_divergence:
            if bullish_score > bearish_score:
                bearish_score += 1
                signal.risk_factors.append("RSI divergence")
            else:
                bullish_score += 1
                confidence_factors.append("RSI divergence signal")

        if indicators.macd_divergence:
            if bullish_score > bearish_score:
                bearish_score += 1
                signal.risk_factors.append("MACD divergence")
            else:
                bullish_score += 1
                confidence_factors.append("MACD divergence signal")

        # Determine action and confidence
        total_score = bullish_score + bearish_score
        if total_score == 0:
            signal.confidence = 0.1
        elif bullish_score > bearish_score:
            signal.action = "BUY"
            signal.confidence = min(
                0.95, bullish_score / (bullish_score + bearish_score)
            )
            signal.primary_reasons = [
                f
                for f in confidence_factors
                if any(
                    word in f.lower()
                    for word in ["bullish", "uptrend", "oversold", "support"]
                )
            ]
        elif bearish_score > bullish_score:
            signal.action = "SELL"
            signal.confidence = min(
                0.95, bearish_score / (bullish_score + bearish_score)
            )
            signal.primary_reasons = [
                f
                for f in confidence_factors
                if any(
                    word in f.lower()
                    for word in ["bearish", "downtrend", "overbought", "resistance"]
                )
            ]
        else:
            signal.confidence = 0.3

        # Set signal strength
        if signal.confidence >= 0.8:
            signal.strength = SignalStrength.VERY_STRONG
        elif signal.confidence >= 0.65:
            signal.strength = SignalStrength.STRONG
        elif signal.confidence >= 0.5:
            signal.strength = SignalStrength.MODERATE
        elif signal.confidence >= 0.3:
            signal.strength = SignalStrength.WEAK
        else:
            signal.strength = SignalStrength.VERY_WEAK

        # Set stop loss and take profit levels
        if signal.action in ["BUY", "SELL"]:
            self._calculate_risk_levels(signal, indicators)

        signal.supporting_factors = [
            f for f in confidence_factors if f not in signal.primary_reasons
        ]

        return signal

    def _calculate_risk_levels(
        self, signal: TradingSignal, indicators: EnhancedTechnicalIndicators
    ):
        """Calculate dynamic stop loss and take profit levels"""

        # Use ATR for dynamic stops
        atr_multiplier = 2.0  # Base multiplier

        # Adjust based on market regime
        if indicators.market_regime == MarketRegime.HIGH_VOLATILITY:
            atr_multiplier = 2.5
        elif indicators.market_regime == MarketRegime.LOW_VOLATILITY:
            atr_multiplier = 1.5
        elif indicators.market_regime in [
            MarketRegime.TRENDING_UP,
            MarketRegime.TRENDING_DOWN,
        ]:
            atr_multiplier = 1.8

        if signal.action == "BUY":
            # Stop loss: Use nearest support or ATR-based
            support_stop = indicators.nearest_support
            atr_stop = indicators.current_price - (indicators.atr * atr_multiplier)
            signal.stop_loss = max(
                support_stop, atr_stop
            )  # Use the higher (less aggressive) stop

            # Take profit levels
            resistance_target = indicators.nearest_resistance
            atr_target1 = indicators.current_price + (indicators.atr * 3)
            atr_target2 = indicators.current_price + (indicators.atr * 5)
            atr_target3 = indicators.current_price + (indicators.atr * 8)

            signal.take_profit_1 = min(resistance_target, atr_target1)
            signal.take_profit_2 = atr_target2
            signal.take_profit_3 = atr_target3

        elif signal.action == "SELL":
            # Stop loss: Use nearest resistance or ATR-based
            resistance_stop = indicators.nearest_resistance
            atr_stop = indicators.current_price + (indicators.atr * atr_multiplier)
            signal.stop_loss = min(
                resistance_stop, atr_stop
            )  # Use the lower (less aggressive) stop

            # Take profit levels
            support_target = indicators.nearest_support
            atr_target1 = indicators.current_price - (indicators.atr * 3)
            atr_target2 = indicators.current_price - (indicators.atr * 5)
            atr_target3 = indicators.current_price - (indicators.atr * 8)

            signal.take_profit_1 = max(support_target, atr_target1)
            signal.take_profit_2 = atr_target2
            signal.take_profit_3 = atr_target3

        # Calculate risk-reward ratio
        if signal.action in ["BUY", "SELL"]:
            risk = abs(signal.entry_price - signal.stop_loss)
            reward = abs(signal.take_profit_1 - signal.entry_price)
            signal.risk_reward_ratio = reward / risk if risk > 0 else 0

            # Minimum risk-reward ratio check
            if signal.risk_reward_ratio < 1.5:
                signal.confidence *= 0.7  # Reduce confidence for poor RR
                signal.risk_factors.append(
                    f"Low risk-reward ratio: {signal.risk_reward_ratio:.2f}"
                )

    def get_market_sentiment(self, indicators: EnhancedTechnicalIndicators) -> str:
        """Enhanced market sentiment analysis"""

        bullish_factors = 0
        bearish_factors = 0

        # Trend analysis
        if indicators.ema_short > indicators.ema_medium > indicators.ema_long:
            bullish_factors += 2
        elif indicators.ema_short < indicators.ema_medium < indicators.ema_long:
            bearish_factors += 2

        # Price vs 200 SMA
        if indicators.current_price > indicators.sma_200:
            bullish_factors += 1
        else:
            bearish_factors += 1

        # Momentum
        if indicators.rsi > 50 and indicators.macd > indicators.macd_signal:
            bullish_factors += 1
        elif indicators.rsi < 50 and indicators.macd < indicators.macd_signal:
            bearish_factors += 1

        # Market structure
        if indicators.higher_highs and indicators.higher_lows:
            bullish_factors += 1
        elif not indicators.higher_highs and not indicators.higher_lows:
            bearish_factors += 1

        # Volume confirmation
        if indicators.volume_trend == "BULLISH_VOLUME":
            bullish_factors += 1
        elif indicators.volume_trend == "BEARISH_VOLUME":
            bearish_factors += 1

        if bullish_factors > bearish_factors + 1:
            return "STRONGLY_BULLISH"
        elif bullish_factors > bearish_factors:
            return "BULLISH"
        elif bearish_factors > bullish_factors + 1:
            return "STRONGLY_BEARISH"
        elif bearish_factors > bullish_factors:
            return "BEARISH"
        else:
            return "NEUTRAL"
