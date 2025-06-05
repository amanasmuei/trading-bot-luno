"""
Historical Data Manager for Backtesting
Handles data fetching, caching, and preprocessing
"""

import logging
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Available data sources"""
    LUNO = "luno"
    BINANCE = "binance"
    SYNTHETIC = "synthetic"


class HistoricalDataManager:
    """Manages historical market data for backtesting"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
        
        logger.info(f"HistoricalDataManager initialized with cache dir: {cache_dir}")
    
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "processed"), exist_ok=True)
    
    def get_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime,
        timeframe: str = "1h",
        source: DataSource = DataSource.SYNTHETIC
    ) -> Optional[pd.DataFrame]:
        """Get historical OHLCV data for the specified period"""
        
        # For now, always generate synthetic data
        # In production, this would check cache and fetch real data
        data = self._generate_synthetic_data(symbol, start_date, end_date, timeframe)
        
        if data is not None:
            logger.info(f"Generated {len(data)} records for {symbol}")
        
        return data
    
    def _generate_synthetic_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime, 
        timeframe: str
    ) -> pd.DataFrame:
        """Generate realistic synthetic market data"""
        
        # Determine frequency
        freq_map = {
            "1m": "1T",
            "5m": "5T", 
            "15m": "15T",
            "30m": "30T",
            "1h": "1H",
            "4h": "4H",
            "1d": "1D"
        }
        
        freq = freq_map.get(timeframe, "1H")
        
        # Create date range
        date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        # Set initial price based on symbol
        price_map = {
            "XBTMYR": 200000.0,  # BTC in MYR
            "XBTZAR": 800000.0,  # BTC in ZAR
            "XBTEUR": 45000.0,   # BTC in EUR
            "ETHMYR": 15000.0,   # ETH in MYR
            "ETHZAR": 60000.0,   # ETH in ZAR
        }
        
        initial_price = price_map.get(symbol, 45000.0)
        
        # Generate price movements with realistic characteristics
        np.random.seed(42)  # For reproducible results
        
        # Market regime parameters
        n_periods = len(date_range)
        
        # Create different market regimes
        regime_length = max(100, n_periods // 4)  # Each regime lasts ~25% of period
        regimes = []
        
        for i in range(0, n_periods, regime_length):
            regime_type = np.random.choice(['trending_up', 'trending_down', 'sideways', 'volatile'])
            regime_end = min(i + regime_length, n_periods)
            regimes.extend([regime_type] * (regime_end - i))
        
        # Ensure we have exactly n_periods regimes
        regimes = regimes[:n_periods]
        
        # Generate returns based on regime
        returns = []
        volatilities = []
        
        for regime in regimes:
            if regime == 'trending_up':
                ret = np.random.normal(0.0008, 0.015)  # Positive drift, moderate vol
                vol = np.random.uniform(0.01, 0.025)
            elif regime == 'trending_down':
                ret = np.random.normal(-0.0005, 0.018)  # Negative drift, higher vol
                vol = np.random.uniform(0.015, 0.03)
            elif regime == 'sideways':
                ret = np.random.normal(0.0001, 0.008)  # Low drift, low vol
                vol = np.random.uniform(0.005, 0.015)
            else:  # volatile
                ret = np.random.normal(0.0002, 0.035)  # Low drift, high vol
                vol = np.random.uniform(0.025, 0.05)
            
            returns.append(ret)
            volatilities.append(vol)
        
        # Generate price series
        prices = [initial_price]
        volumes = []
        
        for i in range(1, n_periods):
            # Add some autocorrelation and mean reversion
            momentum = 0.1 * returns[i-1] if i > 0 else 0
            mean_reversion = -0.05 * (prices[-1] / initial_price - 1)
            
            price_change = returns[i] + momentum + mean_reversion
            
            # Add volatility clustering
            vol_factor = volatilities[i] * (1 + 0.3 * abs(returns[i-1]))
            noise = np.random.normal(0, vol_factor)
            
            new_price = prices[-1] * (1 + price_change + noise)
            
            # Prevent extreme moves
            max_change = 0.15  # 15% max change per period
            if new_price > prices[-1] * (1 + max_change):
                new_price = prices[-1] * (1 + max_change)
            elif new_price < prices[-1] * (1 - max_change):
                new_price = prices[-1] * (1 - max_change)
            
            prices.append(max(new_price, initial_price * 0.1))  # Prevent going too low
            
            # Generate volume (higher volume during volatile periods)
            base_volume = np.random.uniform(0.5, 2.0)
            vol_multiplier = 1 + 2 * volatilities[i]
            volume = base_volume * vol_multiplier * (1 + abs(price_change) * 5)
            volumes.append(volume)
        
        # Add first volume
        volumes.insert(0, np.random.uniform(0.5, 2.0))
        
        # Generate OHLC from close prices
        data = []
        for i, (timestamp, close_price, volume) in enumerate(zip(date_range, prices, volumes)):
            # Generate realistic OHLC
            volatility = volatilities[i] if i < len(volatilities) else 0.01
            
            # Open is previous close (with small gap)
            if i == 0:
                open_price = close_price
            else:
                gap = np.random.normal(0, volatility * 0.3)
                open_price = prices[i-1] * (1 + gap)
            
            # High and low based on intraperiod volatility
            intraperiod_vol = volatility * np.random.uniform(0.5, 1.5)
            high = max(open_price, close_price) * (1 + intraperiod_vol)
            low = min(open_price, close_price) * (1 - intraperiod_vol)
            
            # Ensure OHLC relationships are valid
            high = max(high, open_price, close_price)
            low = min(low, open_price, close_price)
            
            data.append({
                'timestamp': timestamp,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': round(volume, 6)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def clear_cache(self):
        """Clear all cached data"""
        import shutil
        
        try:
            shutil.rmtree(self.cache_dir)
            self.ensure_cache_dir()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data"""
        cache_info = {
            'total_files': 0,
            'total_size_mb': 0,
            'files': []
        }
        
        try:
            processed_dir = os.path.join(self.cache_dir, "processed")
            if os.path.exists(processed_dir):
                for filename in os.listdir(processed_dir):
                    if filename.endswith('.parquet'):
                        filepath = os.path.join(processed_dir, filename)
                        size_mb = os.path.getsize(filepath) / (1024 * 1024)
                        modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        cache_info['files'].append({
                            'filename': filename,
                            'size_mb': round(size_mb, 2),
                            'modified': modified.isoformat()
                        })
                        
                        cache_info['total_files'] += 1
                        cache_info['total_size_mb'] += size_mb
            
            cache_info['total_size_mb'] = round(cache_info['total_size_mb'], 2)
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
        
        return cache_info
