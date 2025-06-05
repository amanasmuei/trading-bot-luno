# 🚀 Trading Bot Backtesting Framework

A comprehensive backtesting and optimization framework for the Luno Trading Bot, featuring advanced performance analytics, parameter optimization, and command-line interface.

## 🌟 Features

### 📊 **Core Backtesting Engine**
- **Historical Strategy Simulation** - Test strategies on historical data
- **Realistic Portfolio Management** - Accurate position sizing, commissions, and slippage
- **Multiple Timeframes** - Support for 1h, 4h, and daily data
- **Synthetic Data Generation** - Realistic market data for testing

### 🔧 **Parameter Optimization**
- **Grid Search Optimization** - Systematic parameter space exploration
- **Multiple Metrics** - Optimize for Sharpe ratio, returns, drawdown, or custom scores
- **Parameter Sensitivity Analysis** - Understand which parameters matter most

### 📈 **Advanced Analytics**
- **Performance Metrics** - Sharpe ratio, Sortino ratio, Calmar ratio, and more
- **Risk Analysis** - Maximum drawdown, VaR, Expected Shortfall
- **Trade Analysis** - Win rate, profit factor, trade distribution
- **Benchmark Comparison** - Compare against buy-and-hold strategy

### 💻 **Command Line Interface**
- **Batch Processing** - Run multiple backtests programmatically
- **Automation Ready** - Perfect for CI/CD and scheduled testing
- **Flexible Configuration** - Extensive command-line options

## 🚀 Quick Start

### 1. **Install Dependencies**

```bash
pip install pandas numpy requests python-dotenv
```

### 2. **Command Line Backtesting**

```bash
# Basic backtest
python run_backtest.py --start 2024-01-01 --end 2024-03-01 --capital 10000

# Parameter optimization
python run_backtest.py --optimize --start 2024-01-01 --end 2024-03-01 --metric sharpe_ratio
```

## 📋 Usage Examples

### **Basic Backtesting**

```python
from datetime import datetime
from src.config.enhanced_settings import EnhancedTradingConfig
from src.backtesting import BacktestEngine, BacktestConfig, BacktestMode

# Create configuration
backtest_config = BacktestConfig(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 3, 1),
    initial_capital=10000.0,
    trading_pair="XBTMYR",
    timeframe="1h"
)

strategy_config = EnhancedTradingConfig()
strategy_config.rsi_period = 14
strategy_config.ema_short = 9
strategy_config.ema_medium = 21

# Run backtest
engine = BacktestEngine(backtest_config)
results = engine.run_backtest(strategy_config)

print(f"Total Return: {results.total_return:.2f}%")
print(f"Sharpe Ratio: {results.metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results.risk_metrics['max_drawdown']:.2f}%")
```

### **Parameter Optimization**

```python
from src.backtesting import StrategyOptimizer, ParameterRange

# Define parameter ranges
parameter_ranges = [
    ParameterRange("rsi_period", 10, 20, 2, "int"),
    ParameterRange("ema_short", 7, 12, 1, "int"),
    ParameterRange("max_position_size_percent", 1.0, 2.5, 0.25, "float"),
]

# Run optimization
optimizer = StrategyOptimizer(strategy_config, backtest_config)
results = optimizer.optimize_parameters(
    parameter_ranges,
    optimization_metric="sharpe_ratio",
    max_workers=4
)

print(f"Best Sharpe Ratio: {results.best_score:.4f}")
print("Best Parameters:")
for param, value in results.best_config.__dict__.items():
    print(f"  {param}: {value}")
```

## 📊 Performance Metrics

### **Return Metrics**
- **Total Return** - Overall strategy performance
- **Annualized Return** - Return adjusted for time period
- **Volatility** - Standard deviation of returns
- **Sharpe Ratio** - Risk-adjusted return measure
- **Sortino Ratio** - Downside risk-adjusted return

### **Risk Metrics**
- **Maximum Drawdown** - Largest peak-to-trough decline
- **Value at Risk (VaR)** - Potential loss at confidence levels
- **Expected Shortfall** - Average loss beyond VaR
- **Calmar Ratio** - Return divided by maximum drawdown

### **Trade Metrics**
- **Win Rate** - Percentage of profitable trades
- **Profit Factor** - Ratio of gross profits to gross losses
- **Average Win/Loss** - Average profit vs average loss
- **Trade Duration** - Average time in position

## 🔧 Configuration Options

### **Backtest Configuration**

```python
BacktestConfig(
    start_date=datetime(2024, 1, 1),      # Backtest start date
    end_date=datetime(2024, 3, 1),        # Backtest end date
    initial_capital=10000.0,              # Starting capital
    trading_pair="XBTMYR",                # Trading pair
    timeframe="1h",                       # Data timeframe
    commission_rate=0.001,                # Trading commission (0.1%)
    slippage_rate=0.0005,                 # Market slippage (0.05%)
    mode=BacktestMode.DETAILED,           # Execution mode
    save_trades=True,                     # Save individual trades
    save_signals=True,                    # Save trading signals
)
```

### **Strategy Configuration**

```python
EnhancedTradingConfig(
    # Technical indicators
    rsi_period=14,
    rsi_oversold=30,
    rsi_overbought=70,
    ema_short=9,
    ema_medium=21,
    ema_long=50,
    
    # Risk management
    max_position_size_percent=1.5,
    base_stop_loss_percent=3.0,
    base_take_profit_percent=6.0,
    min_confidence_buy=0.6,
    min_confidence_sell=0.6,
    
    # Trading rules
    max_daily_trades=5,
    min_risk_reward_ratio=1.5,
)
```

## 📈 Dashboard Features

### **Backtesting Tab**
- Configure strategy parameters with sliders
- Run backtests with real-time progress
- View performance metrics and charts
- Export results and reports

### **Optimization Tab**
- Define parameter ranges for optimization
- Select optimization metrics
- Run parallel optimizations
- Analyze parameter sensitivity

### **Analysis Tab**
- Detailed performance breakdown
- Risk analysis and drawdown charts
- Trade distribution analysis
- Monthly return heatmaps

### **Reports Tab**
- Export comprehensive reports
- Save trade data to CSV
- Generate performance charts
- Create summary documents

## 🛠️ Command Line Options

### **Basic Options**
```bash
--start YYYY-MM-DD          # Start date (required)
--end YYYY-MM-DD            # End date (required)
--pair XBTMYR               # Trading pair
--timeframe 1h              # Data timeframe
--capital 10000             # Initial capital
```

### **Strategy Parameters**
```bash
--rsi-period 14             # RSI period
--rsi-oversold 30           # RSI oversold level
--ema-short 9               # Short EMA period
--ema-medium 21             # Medium EMA period
--position-size 1.5         # Position size percentage
--stop-loss 3.0             # Stop loss percentage
--min-confidence 0.6        # Minimum signal confidence
```

### **Execution Modes**
```bash
--optimize                  # Run parameter optimization
--walk-forward              # Run walk-forward optimization
--fast                      # Fast mode (less detailed)
```

### **Optimization Settings**
```bash
--metric sharpe_ratio       # Optimization metric
--max-combinations 100      # Maximum combinations to test
--workers 4                 # Number of parallel workers
```

## 📁 Output Files

### **Backtest Results**
- `backtest_summary_YYYYMMDD_HHMMSS.json` - Performance summary
- `trades_YYYYMMDD_HHMMSS.csv` - Individual trade details
- `signals_YYYYMMDD_HHMMSS.csv` - Trading signals log

### **Optimization Results**
- `optimization_summary_YYYYMMDD_HHMMSS.json` - Best parameters and performance
- `parameter_sensitivity_YYYYMMDD_HHMMSS.json` - Parameter impact analysis

### **Walk-Forward Results**
- `walk_forward_summary_YYYYMMDD_HHMMSS.json` - Period-by-period results
- `stability_analysis_YYYYMMDD_HHMMSS.json` - Parameter stability metrics

## 🔍 Advanced Features

### **Walk-Forward Optimization**
Test parameter stability by optimizing on rolling windows:

```python
results = optimizer.run_walk_forward_optimization(
    parameter_ranges,
    optimization_window_days=90,    # Optimization period
    test_window_days=30,            # Test period
    optimization_metric="sharpe_ratio"
)
```

### **Custom Optimization Metrics**
Create custom scoring functions:

```python
def custom_score(results):
    sharpe = results.metrics.get('sharpe_ratio', 0)
    return_pct = results.total_return / 100
    max_dd = abs(results.risk_metrics.get('max_drawdown', 100)) / 100
    win_rate = results.metrics.get('win_rate', 0)
    
    # Weighted composite score
    return (sharpe * 0.4) + (return_pct * 0.3) + (win_rate * 0.2) - (max_dd * 0.1)
```

### **Data Source Integration**
Extend with real data sources:

```python
from src.backtesting import HistoricalDataManager, DataSource

data_manager = HistoricalDataManager()
data = data_manager.get_historical_data(
    "XBTMYR",
    start_date,
    end_date,
    timeframe="1h",
    source=DataSource.LUNO  # or DataSource.BINANCE
)
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join the community discussions for questions and ideas

---

**Happy Backtesting! 🚀📈**
