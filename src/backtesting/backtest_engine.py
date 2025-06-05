"""
Core Backtesting Engine
Simulates trading strategies on historical data
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

from src.config.enhanced_settings import EnhancedTradingConfig
from src.bot.enhanced_technical_analysis import EnhancedTechnicalAnalyzer

logger = logging.getLogger(__name__)


class BacktestMode(Enum):
    """Backtesting execution modes"""
    FAST = "fast"
    DETAILED = "detailed"
    OPTIMIZATION = "optimization"


@dataclass
class BacktestConfig:
    """Configuration for backtesting runs"""
    
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000.0
    trading_pair: str = "XBTMYR"
    commission_rate: float = 0.001
    slippage_rate: float = 0.0005
    timeframe: str = "1h"
    warmup_period: int = 200
    mode: BacktestMode = BacktestMode.DETAILED
    save_trades: bool = True
    save_signals: bool = True
    generate_charts: bool = True
    
    def __post_init__(self):
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        if self.initial_capital <= 0:
            raise ValueError("Initial capital must be positive")


class BacktestEngine:
    """Advanced backtesting engine for trading strategies"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.analyzer = None
        
        # Results storage
        self.trades = []
        self.signals = []
        self.portfolio_history = []
        self.market_data = None
        
        # Portfolio state
        self.cash = config.initial_capital
        self.position = 0.0
        self.trade_counter = 0
        
        logger.info(f"BacktestEngine initialized for {config.trading_pair}")
    
    def run_backtest(self, strategy_config: EnhancedTradingConfig):
        """Run complete backtest with given strategy configuration"""
        
        logger.info("Starting backtest execution...")
        
        # Initialize strategy analyzer
        self.analyzer = EnhancedTechnicalAnalyzer(strategy_config)
        
        # Load historical data
        self.market_data = self._generate_synthetic_data()
        if len(self.market_data) < self.config.warmup_period:
            raise ValueError("Insufficient historical data for backtesting")
        
        # Reset state
        self._reset_portfolio()
        
        # Run simulation
        self._execute_simulation(strategy_config)
        
        # Generate results
        results = self._generate_results()
        
        logger.info(f"Backtest completed: {len(self.trades)} trades")
        return results
    
    def _generate_synthetic_data(self) -> pd.DataFrame:
        """Generate realistic synthetic market data"""
        
        # Create date range
        freq = '1H' if self.config.timeframe == '1h' else '1D'
        date_range = pd.date_range(
            start=self.config.start_date,
            end=self.config.end_date,
            freq=freq
        )
        
        # Generate realistic price movements
        np.random.seed(42)
        initial_price = 200000.0 if 'MYR' in self.config.trading_pair else 45000.0
        
        returns = np.random.normal(0.0001, 0.02, len(date_range))
        prices = [initial_price]
        
        for i in range(1, len(date_range)):
            # Add trend and mean reversion
            trend = 0.00005 * np.sin(i / 100)
            mean_reversion = -0.05 * (prices[-1] / initial_price - 1)
            
            price_change = returns[i] + trend + mean_reversion
            new_price = prices[-1] * (1 + price_change)
            prices.append(max(new_price, initial_price * 0.1))
        
        # Generate OHLCV data
        data = []
        for i, (timestamp, close_price) in enumerate(zip(date_range, prices)):
            volatility = abs(np.random.normal(0, 0.005))
            
            open_price = prices[i-1] if i > 0 else close_price
            high = max(open_price, close_price) * (1 + volatility)
            low = min(open_price, close_price) * (1 - volatility)
            volume = np.random.uniform(0.5, 3.0)
            
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
    
    def _reset_portfolio(self):
        """Reset portfolio to initial state"""
        self.cash = self.config.initial_capital
        self.position = 0.0
        self.trade_counter = 0
        self.trades.clear()
        self.signals.clear()
        self.portfolio_history.clear()
    
    def _execute_simulation(self, strategy_config: EnhancedTradingConfig):
        """Execute the main simulation loop"""
        
        start_idx = self.config.warmup_period
        
        for i in range(start_idx, len(self.market_data)):
            current_time = self.market_data.index[i]
            current_data = self.market_data.iloc[max(0, i-200):i+1]
            
            # Convert to format expected by analyzer
            candles = self._convert_to_candles(current_data)
            current_price = float(current_data['close'].iloc[-1])
            volume_data = current_data['volume'].tolist()
            
            try:
                # Perform technical analysis
                indicators = self.analyzer.analyze_market_data(candles, current_price, volume_data)
                signal = self.analyzer.generate_enhanced_signals(indicators, current_data['volume'].iloc[-1])
                
                # Store signal
                if self.config.save_signals:
                    self.signals.append({
                        'timestamp': current_time,
                        'action': signal.action,
                        'confidence': signal.confidence,
                        'price': current_price
                    })
                
                # Execute trading decision
                self._process_signal(signal, current_price, current_time, strategy_config)
                
                # Update portfolio history
                portfolio_value = self._get_portfolio_value(current_price)
                self.portfolio_history.append({
                    'timestamp': current_time,
                    'portfolio_value': portfolio_value,
                    'cash': self.cash,
                    'position': self.position,
                    'price': current_price
                })
                
            except Exception as e:
                if self.config.mode == BacktestMode.DETAILED:
                    logger.warning(f"Error at {current_time}: {e}")
                continue
    
    def _convert_to_candles(self, data: pd.DataFrame) -> List[Dict]:
        """Convert DataFrame to candles format"""
        candles = []
        for _, row in data.iterrows():
            candles.append({
                'open': str(row['open']),
                'high': str(row['high']),
                'low': str(row['low']),
                'close': str(row['close']),
                'volume': str(row['volume']),
                'timestamp': int(row.name.timestamp() * 1000)
            })
        return candles
    
    def _process_signal(self, signal, current_price: float, current_time: datetime, config: EnhancedTradingConfig):
        """Process trading signal and execute trades"""
        
        if signal.action == "BUY" and signal.confidence >= config.min_confidence_buy:
            if self.position == 0:  # Only buy if no position
                portfolio_value = self._get_portfolio_value(current_price)
                position_size = portfolio_value * (config.max_position_size_percent / 100)
                volume = position_size / current_price
                
                if self.cash >= position_size:
                    self._execute_trade("BUY", volume, current_price, current_time, signal)
                    
        elif signal.action == "SELL" and signal.confidence >= config.min_confidence_sell:
            if self.position > 0:  # Only sell if we have position
                self._execute_trade("SELL", self.position, current_price, current_time, signal)
    
    def _execute_trade(self, action: str, volume: float, price: float, timestamp: datetime, signal):
        """Execute a trade and update portfolio"""
        
        self.trade_counter += 1
        commission = volume * price * self.config.commission_rate
        
        if action == "BUY":
            total_cost = volume * price + commission
            self.cash -= total_cost
            self.position += volume
            
        else:  # SELL
            proceeds = volume * price - commission
            self.cash += proceeds
            self.position -= volume
        
        # Record trade
        trade = {
            'trade_id': f"TRADE_{self.trade_counter:06d}",
            'timestamp': timestamp,
            'action': action,
            'volume': volume,
            'price': price,
            'commission': commission,
            'confidence': signal.confidence,
            'portfolio_value': self._get_portfolio_value(price)
        }
        
        if self.config.save_trades:
            self.trades.append(trade)
    
    def _get_portfolio_value(self, current_price: float) -> float:
        """Calculate total portfolio value"""
        return self.cash + (self.position * current_price)
    
    def _generate_results(self):
        """Generate comprehensive backtest results"""
        
        final_price = float(self.market_data['close'].iloc[-1])
        final_value = self._get_portfolio_value(final_price)
        total_return = (final_value - self.config.initial_capital) / self.config.initial_capital * 100
        
        # Calculate basic metrics
        metrics = self._calculate_metrics()
        risk_metrics = self._calculate_risk_metrics()
        
        # Create results object
        from .performance_analyzer import BacktestResults
        
        results = BacktestResults(
            config=self.config,
            trades=self.trades.copy(),
            portfolio_history=self.portfolio_history.copy(),
            signals=self.signals.copy(),
            market_data=self.market_data.copy(),
            initial_capital=self.config.initial_capital,
            final_value=final_value,
            total_return=total_return
        )
        
        results.metrics = metrics
        results.risk_metrics = risk_metrics
        
        return results
    
    def _calculate_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics"""
        
        if not self.portfolio_history:
            return {}
        
        df = pd.DataFrame(self.portfolio_history)
        returns = df['portfolio_value'].pct_change().dropna()
        
        metrics = {}
        
        if len(returns) > 1:
            metrics['volatility'] = returns.std() * np.sqrt(252)
            excess_return = returns.mean() * 252 - 0.03  # 3% risk-free rate
            metrics['sharpe_ratio'] = excess_return / metrics['volatility'] if metrics['volatility'] > 0 else 0
        
        # Trade metrics
        if self.trades:
            buy_trades = [t for t in self.trades if t['action'] == 'BUY']
            sell_trades = [t for t in self.trades if t['action'] == 'SELL']
            
            if buy_trades and sell_trades:
                # Simple P&L calculation
                total_pnl = 0
                winning_trades = 0
                
                for i in range(min(len(buy_trades), len(sell_trades))):
                    buy_price = buy_trades[i]['price']
                    sell_price = sell_trades[i]['price']
                    volume = min(buy_trades[i]['volume'], sell_trades[i]['volume'])
                    
                    pnl = (sell_price - buy_price) * volume
                    total_pnl += pnl
                    
                    if pnl > 0:
                        winning_trades += 1
                
                completed_trades = min(len(buy_trades), len(sell_trades))
                metrics['win_rate'] = winning_trades / completed_trades if completed_trades > 0 else 0
                metrics['total_trades'] = completed_trades
        
        return metrics
    
    def _calculate_risk_metrics(self) -> Dict[str, float]:
        """Calculate risk metrics"""
        
        if not self.portfolio_history:
            return {}
        
        df = pd.DataFrame(self.portfolio_history)
        values = df['portfolio_value']
        
        # Maximum drawdown
        running_max = values.expanding().max()
        drawdown = (values - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        return {
            'max_drawdown': max_drawdown
        }
