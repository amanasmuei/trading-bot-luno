"""
Advanced Technical Indicators Module
Additional sophisticated indicators for enhanced trading strategies
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AdvancedIndicatorResults:
    """Container for advanced technical indicator results"""
    
    # Momentum Indicators
    stochastic_k: float
    stochastic_d: float
    williams_r: float
    roc: float  # Rate of Change
    momentum: float
    
    # Volatility Indicators
    keltner_upper: float
    keltner_middle: float
    keltner_lower: float
    donchian_upper: float
    donchian_lower: float
    
    # Trend Indicators
    adx: float  # Average Directional Index
    plus_di: float
    minus_di: float
    parabolic_sar: float
    
    # Volume Indicators
    obv: float  # On Balance Volume
    vwap: float  # Volume Weighted Average Price
    mfi: float  # Money Flow Index
    
    # Market Structure
    pivot_points: Dict[str, float]
    fibonacci_levels: Dict[str, float]
    
    # Multi-timeframe signals
    trend_alignment: str  # "BULLISH", "BEARISH", "MIXED"
    momentum_divergence: bool
    volume_confirmation: bool


class AdvancedTechnicalIndicators:
    """Advanced technical indicators calculator"""
    
    def __init__(self):
        self.price_history = []
        self.volume_history = []
        
    def calculate_stochastic(self, highs: List[float], lows: List[float], 
                           closes: List[float], k_period: int = 14, 
                           d_period: int = 3) -> Tuple[float, float]:
        """Calculate Stochastic Oscillator %K and %D"""
        if len(closes) < k_period:
            return 50.0, 50.0
            
        # Calculate %K
        current_close = closes[-1]
        lowest_low = min(lows[-k_period:])
        highest_high = max(highs[-k_period:])
        
        if highest_high == lowest_low:
            k_percent = 50.0
        else:
            k_percent = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # Calculate %D (moving average of %K)
        if len(closes) >= k_period + d_period - 1:
            k_values = []
            for i in range(d_period):
                idx = -(i + 1)
                if abs(idx) <= len(closes):
                    close = closes[idx]
                    low = min(lows[idx - k_period + 1:idx + 1])
                    high = max(highs[idx - k_period + 1:idx + 1])
                    if high != low:
                        k_val = ((close - low) / (high - low)) * 100
                    else:
                        k_val = 50.0
                    k_values.append(k_val)
            
            d_percent = np.mean(k_values)
        else:
            d_percent = k_percent
            
        return round(k_percent, 2), round(d_percent, 2)
    
    def calculate_williams_r(self, highs: List[float], lows: List[float], 
                           closes: List[float], period: int = 14) -> float:
        """Calculate Williams %R"""
        if len(closes) < period:
            return -50.0
            
        current_close = closes[-1]
        highest_high = max(highs[-period:])
        lowest_low = min(lows[-period:])
        
        if highest_high == lowest_low:
            return -50.0
            
        williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        return round(williams_r, 2)
    
    def calculate_roc(self, prices: List[float], period: int = 12) -> float:
        """Calculate Rate of Change"""
        if len(prices) < period + 1:
            return 0.0
            
        current_price = prices[-1]
        past_price = prices[-(period + 1)]
        
        if past_price == 0:
            return 0.0
            
        roc = ((current_price - past_price) / past_price) * 100
        return round(roc, 2)
    
    def calculate_momentum(self, prices: List[float], period: int = 10) -> float:
        """Calculate Momentum indicator"""
        if len(prices) < period + 1:
            return 0.0
            
        current_price = prices[-1]
        past_price = prices[-(period + 1)]
        
        momentum = current_price - past_price
        return round(momentum, 2)
    
    def calculate_keltner_channels(self, highs: List[float], lows: List[float], 
                                 closes: List[float], period: int = 20, 
                                 multiplier: float = 2.0) -> Tuple[float, float, float]:
        """Calculate Keltner Channels"""
        if len(closes) < period:
            avg_price = np.mean(closes)
            return avg_price, avg_price, avg_price
            
        # Calculate EMA of typical price
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        ema = self._calculate_ema(typical_prices, period)
        
        # Calculate ATR
        atr = self._calculate_atr(highs, lows, closes, period)
        
        upper = ema + (multiplier * atr)
        lower = ema - (multiplier * atr)
        
        return round(upper, 2), round(ema, 2), round(lower, 2)
    
    def calculate_donchian_channels(self, highs: List[float], lows: List[float], 
                                  period: int = 20) -> Tuple[float, float]:
        """Calculate Donchian Channels"""
        if len(highs) < period:
            return max(highs), min(lows)
            
        upper = max(highs[-period:])
        lower = min(lows[-period:])
        
        return round(upper, 2), round(lower, 2)
    
    def calculate_adx(self, highs: List[float], lows: List[float], 
                     closes: List[float], period: int = 14) -> Tuple[float, float, float]:
        """Calculate ADX, +DI, and -DI"""
        if len(closes) < period + 1:
            return 25.0, 25.0, 25.0
            
        # Calculate True Range and Directional Movement
        tr_values = []
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(closes)):
            # True Range
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr = max(tr1, tr2, tr3)
            tr_values.append(tr)
            
            # Directional Movement
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]
            
            plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0)
            minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0)
        
        # Calculate smoothed averages
        if len(tr_values) >= period:
            atr = np.mean(tr_values[-period:])
            plus_di = (np.mean(plus_dm[-period:]) / atr) * 100 if atr > 0 else 0
            minus_di = (np.mean(minus_dm[-period:]) / atr) * 100 if atr > 0 else 0
            
            # Calculate ADX
            dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
            adx = dx  # Simplified ADX calculation
        else:
            adx, plus_di, minus_di = 25.0, 25.0, 25.0
            
        return round(adx, 2), round(plus_di, 2), round(minus_di, 2)
    
    def calculate_parabolic_sar(self, highs: List[float], lows: List[float], 
                              acceleration: float = 0.02, 
                              maximum: float = 0.2) -> float:
        """Calculate Parabolic SAR (simplified version)"""
        if len(highs) < 2:
            return lows[-1] if lows else 0.0
            
        # Simplified SAR calculation
        current_high = highs[-1]
        current_low = lows[-1]
        prev_high = highs[-2] if len(highs) > 1 else current_high
        prev_low = lows[-2] if len(lows) > 1 else current_low
        
        # Determine trend direction
        if current_high > prev_high:
            # Uptrend - SAR below price
            sar = current_low * (1 - acceleration)
        else:
            # Downtrend - SAR above price
            sar = current_high * (1 + acceleration)
            
        return round(sar, 2)
    
    def calculate_obv(self, closes: List[float], volumes: List[float]) -> float:
        """Calculate On Balance Volume"""
        if len(closes) < 2 or len(volumes) < 2:
            return 0.0
            
        obv = 0.0
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv += volumes[i]
            elif closes[i] < closes[i-1]:
                obv -= volumes[i]
            # If closes[i] == closes[i-1], OBV remains unchanged
            
        return round(obv, 2)
    
    def calculate_vwap(self, highs: List[float], lows: List[float], 
                      closes: List[float], volumes: List[float]) -> float:
        """Calculate Volume Weighted Average Price"""
        if not volumes or len(volumes) != len(closes):
            return np.mean(closes) if closes else 0.0
            
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        
        total_volume = sum(volumes)
        if total_volume == 0:
            return np.mean(typical_prices)
            
        weighted_sum = sum(tp * vol for tp, vol in zip(typical_prices, volumes))
        vwap = weighted_sum / total_volume
        
        return round(vwap, 2)
    
    def calculate_mfi(self, highs: List[float], lows: List[float], 
                     closes: List[float], volumes: List[float], 
                     period: int = 14) -> float:
        """Calculate Money Flow Index"""
        if len(closes) < period + 1 or not volumes:
            return 50.0
            
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        money_flows = [tp * vol for tp, vol in zip(typical_prices, volumes)]
        
        positive_flows = []
        negative_flows = []
        
        for i in range(1, len(typical_prices)):
            if typical_prices[i] > typical_prices[i-1]:
                positive_flows.append(money_flows[i])
                negative_flows.append(0)
            elif typical_prices[i] < typical_prices[i-1]:
                positive_flows.append(0)
                negative_flows.append(money_flows[i])
            else:
                positive_flows.append(0)
                negative_flows.append(0)
        
        if len(positive_flows) >= period:
            positive_sum = sum(positive_flows[-period:])
            negative_sum = sum(negative_flows[-period:])
            
            if negative_sum == 0:
                return 100.0
                
            money_ratio = positive_sum / negative_sum
            mfi = 100 - (100 / (1 + money_ratio))
        else:
            mfi = 50.0
            
        return round(mfi, 2)
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.mean(prices)
            
        alpha = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
            
        return ema
    
    def _calculate_atr(self, highs: List[float], lows: List[float], 
                      closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(highs) < period + 1:
            return np.mean(highs) - np.mean(lows)
            
        true_ranges = []
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            true_ranges.append(max(tr1, tr2, tr3))
            
        return np.mean(true_ranges[-period:]) if len(true_ranges) >= period else np.mean(true_ranges)
