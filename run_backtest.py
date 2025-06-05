#!/usr/bin/env python3
"""
Command Line Interface for Trading Bot Backtesting
Run backtests and optimizations from the command line
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.config.enhanced_settings import EnhancedTradingConfig
from src.backtesting import (
    BacktestEngine, 
    BacktestConfig, 
    BacktestMode,
    StrategyOptimizer,
    ParameterRange,
    DataSource
)


def parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser(
        description="Trading Bot Backtesting CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run basic backtest
  python run_backtest.py --start 2024-01-01 --end 2024-03-01 --capital 10000

  # Run with custom parameters
  python run_backtest.py --start 2024-01-01 --end 2024-03-01 --rsi-period 12 --ema-short 8

  # Run optimization
  python run_backtest.py --optimize --start 2024-01-01 --end 2024-03-01

  # Run walk-forward optimization
  python run_backtest.py --walk-forward --start 2024-01-01 --end 2024-06-01
        """
    )
    
    # Basic settings
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--pair", default="XBTMYR", help="Trading pair (default: XBTMYR)")
    parser.add_argument("--timeframe", default="1h", choices=["1h", "4h", "1d"], help="Timeframe (default: 1h)")
    parser.add_argument("--capital", type=float, default=10000, help="Initial capital (default: 10000)")
    
    # Strategy parameters
    strategy_group = parser.add_argument_group("Strategy Parameters")
    strategy_group.add_argument("--rsi-period", type=int, default=14, help="RSI period (default: 14)")
    strategy_group.add_argument("--rsi-oversold", type=float, default=30, help="RSI oversold level (default: 30)")
    strategy_group.add_argument("--rsi-overbought", type=float, default=70, help="RSI overbought level (default: 70)")
    strategy_group.add_argument("--ema-short", type=int, default=9, help="Short EMA period (default: 9)")
    strategy_group.add_argument("--ema-medium", type=int, default=21, help="Medium EMA period (default: 21)")
    strategy_group.add_argument("--ema-long", type=int, default=50, help="Long EMA period (default: 50)")
    strategy_group.add_argument("--position-size", type=float, default=1.5, help="Position size % (default: 1.5)")
    strategy_group.add_argument("--stop-loss", type=float, default=3.0, help="Stop loss % (default: 3.0)")
    strategy_group.add_argument("--take-profit", type=float, default=6.0, help="Take profit % (default: 6.0)")
    strategy_group.add_argument("--min-confidence", type=float, default=0.6, help="Min confidence (default: 0.6)")
    
    # Execution modes
    mode_group = parser.add_argument_group("Execution Modes")
    mode_group.add_argument("--optimize", action="store_true", help="Run parameter optimization")
    mode_group.add_argument("--walk-forward", action="store_true", help="Run walk-forward optimization")
    mode_group.add_argument("--fast", action="store_true", help="Fast mode (less detailed output)")
    
    # Optimization settings
    opt_group = parser.add_argument_group("Optimization Settings")
    opt_group.add_argument("--metric", default="sharpe_ratio", 
                          choices=["sharpe_ratio", "total_return", "calmar_ratio", "custom_score"],
                          help="Optimization metric (default: sharpe_ratio)")
    opt_group.add_argument("--max-combinations", type=int, default=100, 
                          help="Max combinations for optimization (default: 100)")
    opt_group.add_argument("--workers", type=int, default=2, 
                          help="Number of parallel workers (default: 2)")
    
    # Output settings
    output_group = parser.add_argument_group("Output Settings")
    output_group.add_argument("--output-dir", default="backtest_results", 
                             help="Output directory (default: backtest_results)")
    output_group.add_argument("--save-trades", action="store_true", help="Save individual trades")
    output_group.add_argument("--save-signals", action="store_true", help="Save trading signals")
    output_group.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    return parser.parse_args()


def create_backtest_config(args) -> BacktestConfig:
    """Create backtest configuration from arguments"""
    
    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")
    
    mode = BacktestMode.FAST if args.fast else BacktestMode.DETAILED
    if args.optimize or args.walk_forward:
        mode = BacktestMode.OPTIMIZATION
    
    return BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        initial_capital=args.capital,
        trading_pair=args.pair,
        timeframe=args.timeframe,
        mode=mode,
        save_trades=args.save_trades,
        save_signals=args.save_signals
    )


def create_strategy_config(args) -> EnhancedTradingConfig:
    """Create strategy configuration from arguments"""
    
    config = EnhancedTradingConfig()
    
    # Apply command line parameters
    config.trading_pair = args.pair
    config.rsi_period = args.rsi_period
    config.rsi_oversold = args.rsi_oversold
    config.rsi_overbought = args.rsi_overbought
    config.ema_short = args.ema_short
    config.ema_medium = args.ema_medium
    config.ema_long = args.ema_long
    config.max_position_size_percent = args.position_size
    config.base_stop_loss_percent = args.stop_loss
    config.base_take_profit_percent = args.take_profit
    config.min_confidence_buy = args.min_confidence
    config.min_confidence_sell = args.min_confidence
    
    return config


def run_basic_backtest(args):
    """Run a basic backtest"""
    
    print("🚀 Starting Basic Backtest")
    print("=" * 50)
    
    # Create configurations
    backtest_config = create_backtest_config(args)
    strategy_config = create_strategy_config(args)
    
    print(f"📅 Period: {args.start} to {args.end}")
    print(f"💰 Initial Capital: ${args.capital:,.2f}")
    print(f"📊 Trading Pair: {args.pair}")
    print(f"⏰ Timeframe: {args.timeframe}")
    print()
    
    # Run backtest
    engine = BacktestEngine(backtest_config)
    results = engine.run_backtest(strategy_config)
    
    # Display results
    print("📈 BACKTEST RESULTS")
    print("=" * 50)
    print(f"Total Return: {results.total_return:.2f}%")
    print(f"Final Value: ${results.final_value:,.2f}")
    print(f"Total Trades: {results.total_trades}")
    print(f"Winning Trades: {results.winning_trades}")
    print(f"Win Rate: {results.metrics.get('win_rate', 0):.1%}")
    print(f"Sharpe Ratio: {results.metrics.get('sharpe_ratio', 0):.2f}")
    print(f"Max Drawdown: {results.risk_metrics.get('max_drawdown', 0):.2f}%")
    print(f"Profit Factor: {results.metrics.get('profit_factor', 0):.2f}")
    
    # Save results
    save_results(results, args.output_dir, "backtest")
    
    return results


def run_optimization(args):
    """Run parameter optimization"""
    
    print("🔧 Starting Parameter Optimization")
    print("=" * 50)
    
    # Create configurations
    backtest_config = create_backtest_config(args)
    strategy_config = create_strategy_config(args)
    
    print(f"📅 Period: {args.start} to {args.end}")
    print(f"🎯 Optimization Metric: {args.metric}")
    print(f"🔢 Max Combinations: {args.max_combinations}")
    print(f"⚡ Workers: {args.workers}")
    print()
    
    # Define parameter ranges
    parameter_ranges = [
        ParameterRange("rsi_period", 10, 20, 2, "int"),
        ParameterRange("rsi_oversold", 25, 35, 5, "float"),
        ParameterRange("ema_short", 7, 12, 1, "int"),
        ParameterRange("ema_medium", 18, 25, 2, "int"),
        ParameterRange("max_position_size_percent", 1.0, 2.5, 0.25, "float"),
        ParameterRange("base_stop_loss_percent", 2.0, 4.0, 0.5, "float"),
        ParameterRange("min_confidence_buy", 0.5, 0.75, 0.05, "float"),
    ]
    
    print(f"🔍 Optimizing {len(parameter_ranges)} parameters:")
    for param_range in parameter_ranges:
        print(f"  • {param_range.name}: {param_range.min_value} to {param_range.max_value} (step: {param_range.step})")
    print()
    
    # Run optimization
    optimizer = StrategyOptimizer(strategy_config, backtest_config)
    results = optimizer.optimize_parameters(
        parameter_ranges,
        args.metric,
        args.workers,
        args.max_combinations
    )
    
    # Display results
    print("🏆 OPTIMIZATION RESULTS")
    print("=" * 50)
    print(f"Best {args.metric}: {results.best_score:.4f}")
    print(f"Optimization Time: {results.optimization_time_seconds:.1f}s")
    print(f"Combinations Tested: {results.completed_combinations}/{results.total_combinations}")
    print()
    
    print("🎯 Best Parameters:")
    best_params = {}
    for param_range in parameter_ranges:
        if hasattr(results.best_config, param_range.name):
            value = getattr(results.best_config, param_range.name)
            best_params[param_range.name] = value
            print(f"  • {param_range.name}: {value}")
    print()
    
    print("📊 Best Strategy Performance:")
    best_results = results.best_results
    print(f"  • Total Return: {best_results.total_return:.2f}%")
    print(f"  • Sharpe Ratio: {best_results.metrics.get('sharpe_ratio', 0):.2f}")
    print(f"  • Max Drawdown: {best_results.risk_metrics.get('max_drawdown', 0):.2f}%")
    print(f"  • Win Rate: {best_results.metrics.get('win_rate', 0):.1%}")
    print(f"  • Total Trades: {best_results.total_trades}")
    
    # Parameter sensitivity
    if results.parameter_sensitivity:
        print()
        print("🎯 Parameter Sensitivity:")
        sorted_sensitivity = sorted(results.parameter_sensitivity.items(), key=lambda x: x[1], reverse=True)
        for param, sensitivity in sorted_sensitivity:
            print(f"  • {param}: {sensitivity:.3f}")
    
    # Save results
    save_optimization_results(results, args.output_dir)
    
    return results


def run_walk_forward_optimization(args):
    """Run walk-forward optimization"""
    
    print("🚶 Starting Walk-Forward Optimization")
    print("=" * 50)
    
    # Create configurations
    backtest_config = create_backtest_config(args)
    strategy_config = create_strategy_config(args)
    
    print(f"📅 Period: {args.start} to {args.end}")
    print(f"🎯 Optimization Metric: {args.metric}")
    print()
    
    # Define parameter ranges (smaller set for walk-forward)
    parameter_ranges = [
        ParameterRange("rsi_period", 12, 16, 2, "int"),
        ParameterRange("ema_short", 8, 12, 2, "int"),
        ParameterRange("ema_medium", 18, 24, 3, "int"),
        ParameterRange("max_position_size_percent", 1.0, 2.0, 0.5, "float"),
        ParameterRange("min_confidence_buy", 0.55, 0.7, 0.05, "float"),
    ]
    
    # Run walk-forward optimization
    optimizer = StrategyOptimizer(strategy_config, backtest_config)
    results_list = optimizer.run_walk_forward_optimization(
        parameter_ranges,
        optimization_window_days=60,
        test_window_days=20,
        optimization_metric=args.metric
    )
    
    # Display results
    print("📊 WALK-FORWARD RESULTS")
    print("=" * 50)
    print(f"Total Periods: {len(results_list)}")
    
    # Aggregate results
    total_return = 0
    total_trades = 0
    winning_periods = 0
    
    for i, result in enumerate(results_list):
        test_return = result.test_results.total_return
        total_return += test_return
        total_trades += result.test_results.total_trades
        
        if test_return > 0:
            winning_periods += 1
        
        print(f"Period {i+1}: {test_return:.2f}% return, {result.test_results.total_trades} trades")
    
    print()
    print(f"📈 Aggregate Performance:")
    print(f"  • Total Return: {total_return:.2f}%")
    print(f"  • Average Return per Period: {total_return/len(results_list):.2f}%")
    print(f"  • Winning Periods: {winning_periods}/{len(results_list)} ({winning_periods/len(results_list):.1%})")
    print(f"  • Total Trades: {total_trades}")
    
    # Save results
    save_walk_forward_results(results_list, args.output_dir)
    
    return results_list


def save_results(results, output_dir: str, prefix: str):
    """Save backtest results to files"""
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save summary
    summary = {
        "config": {
            "start_date": results.config.start_date.isoformat(),
            "end_date": results.config.end_date.isoformat(),
            "trading_pair": results.config.trading_pair,
            "initial_capital": results.initial_capital,
        },
        "performance": {
            "total_return": results.total_return,
            "final_value": results.final_value,
            "total_trades": results.total_trades,
            "winning_trades": results.winning_trades,
            "metrics": results.metrics,
            "risk_metrics": results.risk_metrics,
        },
        "generated_at": datetime.now().isoformat()
    }
    
    summary_file = Path(output_dir) / f"{prefix}_summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"💾 Results saved to: {summary_file}")


def save_optimization_results(results, output_dir: str):
    """Save optimization results"""
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save optimization summary
    summary = {
        "best_score": results.best_score,
        "optimization_metric": results.optimization_metric,
        "total_combinations": results.total_combinations,
        "completed_combinations": results.completed_combinations,
        "optimization_time_seconds": results.optimization_time_seconds,
        "parameter_sensitivity": results.parameter_sensitivity,
        "best_performance": {
            "total_return": results.best_results.total_return,
            "sharpe_ratio": results.best_results.metrics.get('sharpe_ratio', 0),
            "max_drawdown": results.best_results.risk_metrics.get('max_drawdown', 0),
            "win_rate": results.best_results.metrics.get('win_rate', 0),
        },
        "generated_at": datetime.now().isoformat()
    }
    
    summary_file = Path(output_dir) / f"optimization_summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"💾 Optimization results saved to: {summary_file}")


def save_walk_forward_results(results_list, output_dir: str):
    """Save walk-forward results"""
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Aggregate results
    summary = {
        "total_periods": len(results_list),
        "periods": [],
        "aggregate_performance": {
            "total_return": sum(r.test_results.total_return for r in results_list),
            "avg_return_per_period": sum(r.test_results.total_return for r in results_list) / len(results_list),
            "winning_periods": len([r for r in results_list if r.test_results.total_return > 0]),
            "total_trades": sum(r.test_results.total_trades for r in results_list),
        },
        "generated_at": datetime.now().isoformat()
    }
    
    for i, result in enumerate(results_list):
        summary["periods"].append({
            "period": i + 1,
            "test_return": result.test_results.total_return,
            "test_trades": result.test_results.total_trades,
            "optimization_score": result.best_score,
        })
    
    summary_file = Path(output_dir) / f"walk_forward_summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"💾 Walk-forward results saved to: {summary_file}")


def main():
    """Main CLI function"""
    
    args = parse_arguments()
    
    print("🤖 Trading Bot Backtesting CLI")
    print("=" * 50)
    
    try:
        if args.walk_forward:
            results = run_walk_forward_optimization(args)
        elif args.optimize:
            results = run_optimization(args)
        else:
            results = run_basic_backtest(args)
        
        print()
        print("✅ Backtesting completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
