"""
Backtesting Framework for Trading Bot
Advanced historical strategy validation and optimization
"""

from .backtest_engine import BacktestEngine, BacktestConfig
from .data_manager import HistoricalDataManager, DataSource
from .performance_analyzer import PerformanceAnalyzer, BacktestResults
from .strategy_optimizer import StrategyOptimizer, OptimizationResult
from .portfolio_simulator import PortfolioSimulator, SimulatedTrade

__all__ = [
    "BacktestEngine",
    "BacktestConfig", 
    "HistoricalDataManager",
    "DataSource",
    "PerformanceAnalyzer",
    "BacktestResults",
    "StrategyOptimizer",
    "OptimizationResult",
    "PortfolioSimulator",
    "SimulatedTrade",
]

__version__ = "1.0.0"
