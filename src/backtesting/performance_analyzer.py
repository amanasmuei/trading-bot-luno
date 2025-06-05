"""
Performance Analysis for Backtesting Results
Advanced metrics and statistical analysis
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class BacktestResults:
    """Comprehensive backtesting results container"""
    
    # Configuration
    config: Any  # BacktestConfig
    
    # Raw data
    trades: List[Dict]
    portfolio_history: List[Dict]
    signals: List[Dict]
    market_data: pd.DataFrame
    
    # Basic metrics
    initial_capital: float
    final_value: float
    total_return: float
    
    # Performance metrics (calculated by analyzer)
    metrics: Dict[str, float] = field(default_factory=dict)
    risk_metrics: Dict[str, float] = field(default_factory=dict)
    trade_analysis: Dict[str, Any] = field(default_factory=dict)
    benchmark_comparison: Dict[str, float] = field(default_factory=dict)
    drawdown_analysis: Dict[str, Any] = field(default_factory=dict)
    monthly_returns: Dict[str, float] = field(default_factory=dict)
    
    @property
    def duration_days(self) -> int:
        """Total backtest duration in days"""
        return (self.config.end_date - self.config.start_date).days
    
    @property
    def total_trades(self) -> int:
        """Total number of completed trade pairs"""
        buy_trades = len([t for t in self.trades if t['action'] == 'BUY'])
        sell_trades = len([t for t in self.trades if t['action'] == 'SELL'])
        return min(buy_trades, sell_trades)
    
    @property
    def winning_trades(self) -> int:
        """Number of winning trades (simplified calculation)"""
        if not self.trades:
            return 0
        
        buy_trades = [t for t in self.trades if t['action'] == 'BUY']
        sell_trades = [t for t in self.trades if t['action'] == 'SELL']
        
        winning = 0
        for i in range(min(len(buy_trades), len(sell_trades))):
            if sell_trades[i]['price'] > buy_trades[i]['price']:
                winning += 1
        
        return winning


class PerformanceAnalyzer:
    """Advanced performance analysis for backtesting results"""
    
    def __init__(self):
        self.risk_free_rate = 0.03  # 3% annual risk-free rate
    
    def analyze_results(self, results: BacktestResults) -> BacktestResults:
        """Perform comprehensive analysis of backtest results"""
        
        logger.info("Analyzing backtest performance...")
        
        # Calculate all metrics
        results.metrics.update(self._calculate_performance_metrics(results))
        results.risk_metrics.update(self._calculate_risk_metrics(results))
        results.trade_analysis = self._analyze_trades(results)
        results.drawdown_analysis = self._analyze_drawdowns(results)
        results.monthly_returns = self._calculate_monthly_returns(results)
        results.benchmark_comparison = self._compare_to_benchmark(results)
        
        logger.info(f"Performance analysis completed: {results.total_return:.2f}% return")
        
        return results
    
    def _calculate_performance_metrics(self, results: BacktestResults) -> Dict[str, float]:
        """Calculate core performance metrics"""
        
        metrics = {}
        
        # Basic returns
        metrics['total_return'] = results.total_return
        metrics['annualized_return'] = self._annualize_return(results.total_return, results.duration_days)
        
        # Portfolio value series for calculations
        if not results.portfolio_history:
            return metrics
        
        portfolio_df = pd.DataFrame(results.portfolio_history)
        portfolio_df['timestamp'] = pd.to_datetime(portfolio_df['timestamp'])
        portfolio_df.set_index('timestamp', inplace=True)
        
        # Daily returns
        daily_returns = portfolio_df['portfolio_value'].pct_change().dropna()
        
        if len(daily_returns) > 1:
            # Volatility
            metrics['volatility'] = daily_returns.std() * np.sqrt(252)  # Annualized
            
            # Sharpe ratio
            excess_returns = daily_returns.mean() * 252 - self.risk_free_rate
            metrics['sharpe_ratio'] = excess_returns / metrics['volatility'] if metrics['volatility'] > 0 else 0
            
            # Sortino ratio (downside deviation)
            downside_returns = daily_returns[daily_returns < 0]
            downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            metrics['sortino_ratio'] = excess_returns / downside_std if downside_std > 0 else 0
            
            # Calmar ratio (return / max drawdown)
            max_dd = self._calculate_max_drawdown(portfolio_df['portfolio_value'])
            metrics['calmar_ratio'] = metrics['annualized_return'] / abs(max_dd) if max_dd < 0 else 0
        
        # Trade-based metrics
        if results.trades:
            buy_trades = [t for t in results.trades if t['action'] == 'BUY']
            sell_trades = [t for t in results.trades if t['action'] == 'SELL']
            
            if buy_trades and sell_trades:
                completed_trades = min(len(buy_trades), len(sell_trades))
                metrics['win_rate'] = results.winning_trades / completed_trades if completed_trades > 0 else 0
                
                # Calculate P&L for each trade pair
                pnls = []
                for i in range(completed_trades):
                    buy_price = buy_trades[i]['price']
                    sell_price = sell_trades[i]['price']
                    volume = min(buy_trades[i]['volume'], sell_trades[i]['volume'])
                    pnl = (sell_price - buy_price) * volume
                    pnls.append(pnl)
                
                winning_pnls = [p for p in pnls if p > 0]
                losing_pnls = [p for p in pnls if p < 0]
                
                metrics['avg_win'] = np.mean(winning_pnls) if winning_pnls else 0
                metrics['avg_loss'] = np.mean(losing_pnls) if losing_pnls else 0
                metrics['avg_win_loss_ratio'] = abs(metrics['avg_win'] / metrics['avg_loss']) if metrics['avg_loss'] < 0 else 0
                
                # Profit factor
                total_wins = sum(winning_pnls) if winning_pnls else 0
                total_losses = abs(sum(losing_pnls)) if losing_pnls else 0
                metrics['profit_factor'] = total_wins / total_losses if total_losses > 0 else float('inf')
        
        return metrics
    
    def _calculate_risk_metrics(self, results: BacktestResults) -> Dict[str, float]:
        """Calculate risk-related metrics"""
        
        risk_metrics = {}
        
        if not results.portfolio_history:
            return risk_metrics
        
        portfolio_df = pd.DataFrame(results.portfolio_history)
        portfolio_df['timestamp'] = pd.to_datetime(portfolio_df['timestamp'])
        portfolio_df.set_index('timestamp', inplace=True)
        
        # Maximum drawdown
        risk_metrics['max_drawdown'] = self._calculate_max_drawdown(portfolio_df['portfolio_value'])
        
        # Value at Risk (VaR)
        daily_returns = portfolio_df['portfolio_value'].pct_change().dropna()
        if len(daily_returns) > 0:
            risk_metrics['var_95'] = np.percentile(daily_returns, 5) * 100  # 95% VaR
            risk_metrics['var_99'] = np.percentile(daily_returns, 1) * 100  # 99% VaR
            
            # Expected Shortfall (Conditional VaR)
            var_95_threshold = np.percentile(daily_returns, 5)
            tail_returns = daily_returns[daily_returns <= var_95_threshold]
            risk_metrics['expected_shortfall'] = np.mean(tail_returns) * 100 if len(tail_returns) > 0 else 0
        
        return risk_metrics
    
    def _analyze_trades(self, results: BacktestResults) -> Dict[str, Any]:
        """Analyze individual trades"""
        
        analysis = {}
        
        if not results.trades:
            return analysis
        
        buy_trades = [t for t in results.trades if t['action'] == 'BUY']
        sell_trades = [t for t in results.trades if t['action'] == 'SELL']
        
        analysis['total_trades'] = len(results.trades)
        analysis['buy_trades'] = len(buy_trades)
        analysis['sell_trades'] = len(sell_trades)
        analysis['completed_pairs'] = min(len(buy_trades), len(sell_trades))
        
        if buy_trades and sell_trades:
            # Calculate trade statistics
            pnls = []
            durations = []
            
            for i in range(min(len(buy_trades), len(sell_trades))):
                buy_trade = buy_trades[i]
                sell_trade = sell_trades[i]
                
                # P&L calculation
                volume = min(buy_trade['volume'], sell_trade['volume'])
                pnl = (sell_trade['price'] - buy_trade['price']) * volume
                pnls.append(pnl)
                
                # Duration calculation
                duration = (sell_trade['timestamp'] - buy_trade['timestamp']).total_seconds() / 3600
                durations.append(duration)
            
            analysis['total_pnl'] = sum(pnls)
            analysis['best_trade'] = max(pnls) if pnls else 0
            analysis['worst_trade'] = min(pnls) if pnls else 0
            analysis['avg_pnl'] = np.mean(pnls) if pnls else 0
            analysis['avg_duration_hours'] = np.mean(durations) if durations else 0
            
            # Confidence analysis
            confidences = [t['confidence'] for t in buy_trades if 'confidence' in t]
            if confidences:
                analysis['avg_confidence'] = np.mean(confidences)
                analysis['min_confidence'] = min(confidences)
                analysis['max_confidence'] = max(confidences)
        
        return analysis
    
    def _analyze_drawdowns(self, results: BacktestResults) -> Dict[str, Any]:
        """Analyze drawdown periods in detail"""
        
        if not results.portfolio_history:
            return {}
        
        portfolio_df = pd.DataFrame(results.portfolio_history)
        portfolio_df['timestamp'] = pd.to_datetime(portfolio_df['timestamp'])
        portfolio_df.set_index('timestamp', inplace=True)
        
        values = portfolio_df['portfolio_value']
        
        # Calculate running maximum and drawdown
        running_max = values.expanding().max()
        drawdown = (values - running_max) / running_max * 100
        
        analysis = {
            'max_drawdown': drawdown.min(),
            'current_drawdown': drawdown.iloc[-1] if len(drawdown) > 0 else 0,
            'avg_drawdown': drawdown[drawdown < 0].mean() if len(drawdown[drawdown < 0]) > 0 else 0
        }
        
        return analysis
    
    def _calculate_monthly_returns(self, results: BacktestResults) -> Dict[str, float]:
        """Calculate monthly returns breakdown"""
        
        if not results.portfolio_history:
            return {}
        
        portfolio_df = pd.DataFrame(results.portfolio_history)
        portfolio_df['timestamp'] = pd.to_datetime(portfolio_df['timestamp'])
        portfolio_df.set_index('timestamp', inplace=True)
        
        # Resample to monthly
        monthly_values = portfolio_df['portfolio_value'].resample('M').last()
        monthly_returns = monthly_values.pct_change().dropna() * 100
        
        return {month.strftime('%Y-%m'): return_pct for month, return_pct in monthly_returns.items()}
    
    def _compare_to_benchmark(self, results: BacktestResults) -> Dict[str, float]:
        """Compare performance to buy-and-hold benchmark"""
        
        if len(results.market_data) == 0:
            return {}
        
        # Calculate buy-and-hold return
        start_price = results.market_data['close'].iloc[0]
        end_price = results.market_data['close'].iloc[-1]
        buy_hold_return = (end_price - start_price) / start_price * 100
        
        # Calculate excess return
        excess_return = results.total_return - buy_hold_return
        
        return {
            'buy_hold_return': buy_hold_return,
            'strategy_return': results.total_return,
            'excess_return': excess_return,
            'outperformance': excess_return > 0
        }
    
    def _calculate_max_drawdown(self, values: pd.Series) -> float:
        """Calculate maximum drawdown"""
        running_max = values.expanding().max()
        drawdown = (values - running_max) / running_max * 100
        return drawdown.min()
    
    def _annualize_return(self, total_return: float, days: int) -> float:
        """Convert total return to annualized return"""
        if days <= 0:
            return 0
        
        years = days / 365.25
        return (((1 + total_return / 100) ** (1 / years)) - 1) * 100
