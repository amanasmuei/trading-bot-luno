"""
Multi-Timeframe Analysis Module
Advanced analysis across multiple timeframes for better trading decisions
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from src.bot.enhanced_technical_analysis import EnhancedTechnicalAnalyzer, MarketRegime
from src.bot.advanced_indicators import AdvancedTechnicalIndicators
from src.api.luno_client import LunoAPIClient

logger = logging.getLogger(__name__)


class TimeFrame(Enum):
    """Supported timeframes"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


class TrendDirection(Enum):
    """Trend direction classification"""
    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"


@dataclass
class TimeFrameAnalysis:
    """Analysis results for a specific timeframe"""
    timeframe: TimeFrame
    trend_direction: TrendDirection
    trend_strength: float  # 0-1
    momentum: float
    volatility: float
    support_levels: List[float]
    resistance_levels: List[float]
    key_indicators: Dict[str, float]
    market_regime: MarketRegime
    confidence: float  # 0-1
    timestamp: datetime


@dataclass
class MultiTimeFrameSignal:
    """Combined signal from multiple timeframes"""
    primary_action: str  # BUY, SELL, WAIT
    confidence: float  # 0-1
    timeframe_alignment: float  # 0-1, how aligned timeframes are
    dominant_timeframe: TimeFrame
    supporting_timeframes: List[TimeFrame]
    conflicting_timeframes: List[TimeFrame]
    risk_level: str  # LOW, MEDIUM, HIGH
    entry_conditions: List[str]
    exit_conditions: List[str]
    timeframe_analyses: Dict[TimeFrame, TimeFrameAnalysis]


class MultiTimeFrameAnalyzer:
    """Advanced multi-timeframe analysis system"""
    
    def __init__(self, client: LunoAPIClient, config):
        self.client = client
        self.config = config
        self.analyzer = EnhancedTechnicalAnalyzer(config)
        self.advanced_indicators = AdvancedTechnicalIndicators()
        
        # Timeframe hierarchy (higher timeframes have more weight)
        self.timeframe_weights = {
            TimeFrame.D1: 1.0,    # Daily - highest weight
            TimeFrame.H4: 0.8,    # 4-hour
            TimeFrame.H1: 0.6,    # 1-hour
            TimeFrame.M30: 0.4,   # 30-minute
            TimeFrame.M15: 0.3,   # 15-minute
            TimeFrame.M5: 0.2,    # 5-minute
            TimeFrame.M1: 0.1     # 1-minute - lowest weight
        }
        
        # Cache for market data
        self.data_cache: Dict[str, Dict[TimeFrame, List[Dict]]] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
    def analyze_multiple_timeframes(self, 
                                  pair: str, 
                                  timeframes: List[TimeFrame] = None) -> MultiTimeFrameSignal:
        """Perform comprehensive multi-timeframe analysis"""
        
        if timeframes is None:
            timeframes = [TimeFrame.D1, TimeFrame.H4, TimeFrame.H1, TimeFrame.M30]
        
        logger.info(f"Starting multi-timeframe analysis for {pair}")
        
        # Analyze each timeframe
        timeframe_analyses = {}
        for timeframe in timeframes:
            try:
                analysis = self._analyze_single_timeframe(pair, timeframe)
                if analysis:
                    timeframe_analyses[timeframe] = analysis
                    logger.debug(f"{timeframe.value}: {analysis.trend_direction.value} (confidence: {analysis.confidence:.2f})")
            except Exception as e:
                logger.error(f"Failed to analyze {timeframe.value} for {pair}: {e}")
        
        if not timeframe_analyses:
            logger.warning(f"No successful timeframe analyses for {pair}")
            return self._create_neutral_signal(timeframes)
        
        # Generate combined signal
        combined_signal = self._generate_combined_signal(timeframe_analyses)
        
        logger.info(f"Multi-timeframe signal: {combined_signal.primary_action} "
                   f"(confidence: {combined_signal.confidence:.2f}, "
                   f"alignment: {combined_signal.timeframe_alignment:.2f})")
        
        return combined_signal
    
    def _analyze_single_timeframe(self, pair: str, timeframe: TimeFrame) -> Optional[TimeFrameAnalysis]:
        """Analyze a single timeframe"""
        
        try:
            # Get market data for this timeframe
            candles = self._get_timeframe_data(pair, timeframe)
            if not candles or len(candles) < 50:
                logger.warning(f"Insufficient data for {timeframe.value}")
                return None
            
            # Extract price data
            closes = [float(candle["close"]) for candle in candles]
            highs = [float(candle["high"]) for candle in candles]
            lows = [float(candle["low"]) for candle in candles]
            volumes = [float(candle["volume"]) for candle in candles]
            
            current_price = closes[-1]
            
            # Perform technical analysis
            indicators = self.analyzer.analyze_market_data(candles, current_price, volumes)
            
            # Calculate advanced indicators
            stoch_k, stoch_d = self.advanced_indicators.calculate_stochastic(highs, lows, closes)
            williams_r = self.advanced_indicators.calculate_williams_r(highs, lows, closes)
            roc = self.advanced_indicators.calculate_roc(closes)
            adx, plus_di, minus_di = self.advanced_indicators.calculate_adx(highs, lows, closes)
            
            # Determine trend direction and strength
            trend_direction, trend_strength = self._determine_trend(indicators, adx, plus_di, minus_di)
            
            # Calculate momentum
            momentum = self._calculate_momentum(closes, stoch_k, williams_r, roc)
            
            # Calculate volatility
            volatility = self._calculate_volatility(closes, indicators.atr)
            
            # Determine support and resistance levels
            support_levels = indicators.dynamic_support[:3]  # Top 3 support levels
            resistance_levels = indicators.dynamic_resistance[:3]  # Top 3 resistance levels
            
            # Create key indicators summary
            key_indicators = {
                "rsi": indicators.rsi,
                "macd": indicators.macd,
                "stochastic_k": stoch_k,
                "williams_r": williams_r,
                "adx": adx,
                "bollinger_position": indicators.bollinger_position,
                "volume_ratio": indicators.volume_ratio
            }
            
            # Calculate confidence based on indicator alignment
            confidence = self._calculate_timeframe_confidence(indicators, trend_direction, adx)
            
            return TimeFrameAnalysis(
                timeframe=timeframe,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                momentum=momentum,
                volatility=volatility,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                key_indicators=key_indicators,
                market_regime=indicators.market_regime,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {timeframe.value}: {e}")
            return None
    
    def _get_timeframe_data(self, pair: str, timeframe: TimeFrame) -> List[Dict]:
        """Get market data for specific timeframe with caching"""
        
        cache_key = f"{pair}_{timeframe.value}"
        
        # Check cache
        if (cache_key in self.data_cache and 
            cache_key in self.cache_expiry and 
            datetime.now() < self.cache_expiry[cache_key]):
            return self.data_cache[pair][timeframe]
        
        try:
            # Calculate timeframe duration in seconds
            duration_map = {
                TimeFrame.M1: 60,
                TimeFrame.M5: 300,
                TimeFrame.M15: 900,
                TimeFrame.M30: 1800,
                TimeFrame.H1: 3600,
                TimeFrame.H4: 14400,
                TimeFrame.D1: 86400,
                TimeFrame.W1: 604800
            }
            
            duration = duration_map.get(timeframe, 3600)
            
            # Get data from API (using simulated data for now)
            since = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
            candles_data = self.client.get_candles(pair, duration, since)
            candles = candles_data.get("candles", [])
            
            # Cache the data
            if pair not in self.data_cache:
                self.data_cache[pair] = {}
            
            self.data_cache[pair][timeframe] = candles
            self.cache_expiry[cache_key] = datetime.now() + timedelta(minutes=5)  # 5-minute cache
            
            return candles
            
        except Exception as e:
            logger.error(f"Failed to get {timeframe.value} data for {pair}: {e}")
            return []
    
    def _determine_trend(self, indicators, adx: float, plus_di: float, minus_di: float) -> Tuple[TrendDirection, float]:
        """Determine trend direction and strength"""
        
        # EMA trend analysis
        ema_bullish = indicators.ema_short > indicators.ema_medium > indicators.ema_long
        ema_bearish = indicators.ema_short < indicators.ema_medium < indicators.ema_long
        
        # Price position relative to EMAs
        price_above_emas = indicators.current_price > indicators.ema_short
        price_below_emas = indicators.current_price < indicators.ema_short
        
        # MACD trend
        macd_bullish = indicators.macd > indicators.macd_signal and indicators.macd > 0
        macd_bearish = indicators.macd < indicators.macd_signal and indicators.macd < 0
        
        # ADX trend strength
        strong_trend = adx > 25
        weak_trend = adx < 20
        
        # Directional movement
        di_bullish = plus_di > minus_di
        di_bearish = minus_di > plus_di
        
        # Combine signals
        bullish_signals = sum([ema_bullish, price_above_emas, macd_bullish, di_bullish])
        bearish_signals = sum([ema_bearish, price_below_emas, macd_bearish, di_bearish])
        
        # Determine trend direction
        if bullish_signals >= 3:
            if strong_trend:
                trend_direction = TrendDirection.STRONG_BULLISH
            else:
                trend_direction = TrendDirection.BULLISH
        elif bearish_signals >= 3:
            if strong_trend:
                trend_direction = TrendDirection.STRONG_BEARISH
            else:
                trend_direction = TrendDirection.BEARISH
        else:
            trend_direction = TrendDirection.NEUTRAL
        
        # Calculate trend strength (0-1)
        if strong_trend:
            trend_strength = min(1.0, adx / 50)  # Normalize ADX
        else:
            trend_strength = max(0.1, adx / 50)  # Minimum strength
        
        return trend_direction, trend_strength
    
    def _calculate_momentum(self, closes: List[float], stoch_k: float, williams_r: float, roc: float) -> float:
        """Calculate momentum score"""
        
        # Price momentum (recent vs older prices)
        if len(closes) >= 10:
            recent_avg = np.mean(closes[-5:])
            older_avg = np.mean(closes[-10:-5])
            price_momentum = (recent_avg - older_avg) / older_avg
        else:
            price_momentum = 0
        
        # Normalize indicators
        stoch_momentum = (stoch_k - 50) / 50  # -1 to 1
        williams_momentum = (williams_r + 50) / 50  # -1 to 1
        roc_momentum = roc / 100  # Normalize ROC
        
        # Combine momentum indicators
        momentum = (price_momentum * 0.4 + 
                   stoch_momentum * 0.2 + 
                   williams_momentum * 0.2 + 
                   roc_momentum * 0.2)
        
        return np.clip(momentum, -1, 1)
    
    def _calculate_volatility(self, closes: List[float], atr: float) -> float:
        """Calculate volatility score"""
        
        if len(closes) < 20:
            return 0.5
        
        # Price volatility
        returns = np.diff(closes) / closes[:-1]
        price_volatility = np.std(returns[-20:])
        
        # ATR-based volatility
        current_price = closes[-1]
        atr_volatility = atr / current_price if current_price > 0 else 0
        
        # Combine volatilities
        volatility = (price_volatility + atr_volatility) / 2
        
        # Normalize to 0-1 scale
        return min(1.0, volatility * 100)
    
    def _calculate_timeframe_confidence(self, indicators, trend_direction: TrendDirection, adx: float) -> float:
        """Calculate confidence for timeframe analysis"""
        
        confidence_factors = []
        
        # Trend strength (ADX)
        if adx > 25:
            confidence_factors.append(0.8)
        elif adx > 15:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.3)
        
        # Indicator alignment
        rsi_aligned = (
            (trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH] and indicators.rsi > 50) or
            (trend_direction in [TrendDirection.BEARISH, TrendDirection.STRONG_BEARISH] and indicators.rsi < 50)
        )
        
        macd_aligned = (
            (trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH] and indicators.macd > 0) or
            (trend_direction in [TrendDirection.BEARISH, TrendDirection.STRONG_BEARISH] and indicators.macd < 0)
        )
        
        alignment_score = sum([rsi_aligned, macd_aligned]) / 2
        confidence_factors.append(alignment_score)
        
        # Volume confirmation
        if indicators.volume_ratio > 1.2:  # Above average volume
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        # Market regime consistency
        if indicators.market_regime in [MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN]:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.4)
        
        return np.mean(confidence_factors)
    
    def _generate_combined_signal(self, timeframe_analyses: Dict[TimeFrame, TimeFrameAnalysis]) -> MultiTimeFrameSignal:
        """Generate combined signal from multiple timeframe analyses"""
        
        # Calculate weighted scores for each action
        buy_score = 0
        sell_score = 0
        total_weight = 0
        
        supporting_timeframes = []
        conflicting_timeframes = []
        
        for timeframe, analysis in timeframe_analyses.items():
            weight = self.timeframe_weights.get(timeframe, 0.5)
            confidence_weight = weight * analysis.confidence
            
            if analysis.trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH]:
                buy_score += confidence_weight
                if analysis.trend_direction == TrendDirection.STRONG_BULLISH:
                    buy_score += confidence_weight * 0.5  # Bonus for strong trend
            elif analysis.trend_direction in [TrendDirection.BEARISH, TrendDirection.STRONG_BEARISH]:
                sell_score += confidence_weight
                if analysis.trend_direction == TrendDirection.STRONG_BEARISH:
                    sell_score += confidence_weight * 0.5  # Bonus for strong trend
            
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
        
        # Determine primary action
        if buy_score > sell_score and buy_score > 0.6:
            primary_action = "BUY"
            confidence = buy_score
        elif sell_score > buy_score and sell_score > 0.6:
            primary_action = "SELL"
            confidence = sell_score
        else:
            primary_action = "WAIT"
            confidence = max(buy_score, sell_score)
        
        # Calculate timeframe alignment
        aligned_timeframes = 0
        for timeframe, analysis in timeframe_analyses.items():
            if primary_action == "BUY" and analysis.trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH]:
                aligned_timeframes += 1
                supporting_timeframes.append(timeframe)
            elif primary_action == "SELL" and analysis.trend_direction in [TrendDirection.BEARISH, TrendDirection.STRONG_BEARISH]:
                aligned_timeframes += 1
                supporting_timeframes.append(timeframe)
            elif primary_action == "WAIT" and analysis.trend_direction == TrendDirection.NEUTRAL:
                aligned_timeframes += 1
                supporting_timeframes.append(timeframe)
            else:
                conflicting_timeframes.append(timeframe)
        
        timeframe_alignment = aligned_timeframes / len(timeframe_analyses) if timeframe_analyses else 0
        
        # Determine dominant timeframe (highest weight with supporting trend)
        dominant_timeframe = max(
            supporting_timeframes,
            key=lambda tf: self.timeframe_weights.get(tf, 0),
            default=list(timeframe_analyses.keys())[0] if timeframe_analyses else TimeFrame.H1
        )
        
        # Determine risk level
        if timeframe_alignment > 0.8 and confidence > 0.7:
            risk_level = "LOW"
        elif timeframe_alignment > 0.6 and confidence > 0.5:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Generate entry and exit conditions
        entry_conditions = self._generate_entry_conditions(primary_action, timeframe_analyses)
        exit_conditions = self._generate_exit_conditions(primary_action, timeframe_analyses)
        
        return MultiTimeFrameSignal(
            primary_action=primary_action,
            confidence=confidence,
            timeframe_alignment=timeframe_alignment,
            dominant_timeframe=dominant_timeframe,
            supporting_timeframes=supporting_timeframes,
            conflicting_timeframes=conflicting_timeframes,
            risk_level=risk_level,
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
            timeframe_analyses=timeframe_analyses
        )
    
    def _generate_entry_conditions(self, action: str, analyses: Dict[TimeFrame, TimeFrameAnalysis]) -> List[str]:
        """Generate entry conditions based on timeframe analyses"""
        conditions = []
        
        if action == "BUY":
            conditions.extend([
                "Higher timeframe trend is bullish",
                "Multiple timeframes show upward momentum",
                "Price above key support levels"
            ])
        elif action == "SELL":
            conditions.extend([
                "Higher timeframe trend is bearish", 
                "Multiple timeframes show downward momentum",
                "Price below key resistance levels"
            ])
        else:
            conditions.append("Wait for clearer directional signals")
        
        return conditions
    
    def _generate_exit_conditions(self, action: str, analyses: Dict[TimeFrame, TimeFrameAnalysis]) -> List[str]:
        """Generate exit conditions based on timeframe analyses"""
        conditions = []
        
        if action in ["BUY", "SELL"]:
            conditions.extend([
                "Trend reversal on higher timeframes",
                "Momentum divergence across timeframes",
                "Break of key support/resistance levels"
            ])
        
        return conditions
    
    def _create_neutral_signal(self, timeframes: List[TimeFrame]) -> MultiTimeFrameSignal:
        """Create a neutral signal when analysis fails"""
        return MultiTimeFrameSignal(
            primary_action="WAIT",
            confidence=0.0,
            timeframe_alignment=0.0,
            dominant_timeframe=timeframes[0] if timeframes else TimeFrame.H1,
            supporting_timeframes=[],
            conflicting_timeframes=timeframes,
            risk_level="HIGH",
            entry_conditions=["Insufficient data for analysis"],
            exit_conditions=["Wait for better market conditions"],
            timeframe_analyses={}
        )
