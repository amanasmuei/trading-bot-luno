"""
Strategy Parameter Optimization
Automated parameter tuning and optimization
"""

import logging
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from itertools import product
from copy import deepcopy

from src.config.enhanced_settings import EnhancedTradingConfig
from .backtest_engine import BacktestEngine, BacktestConfig, BacktestMode

logger = logging.getLogger(__name__)


@dataclass
class ParameterRange:
    """Defines a parameter optimization range"""
    name: str
    min_value: float
    max_value: float
    step: float
    param_type: str = "float"  # "float", "int", "choice"
    choices: Optional[List[Any]] = None
    
    def get_values(self) -> List[Any]:
        """Get all values in the range"""
        if self.param_type == "choice" and self.choices:
            return self.choices
        elif self.param_type == "int":
            return list(range(int(self.min_value), int(self.max_value) + 1, int(self.step)))
        else:  # float
            values = []
            current = self.min_value
            while current <= self.max_value:
                values.append(round(current, 6))
                current += self.step
            return values


@dataclass
class OptimizationResult:
    """Results from parameter optimization"""
    
    # Best configuration
    best_config: EnhancedTradingConfig
    best_results: Any  # BacktestResults
    best_score: float
    
    # All results
    all_results: List[Tuple[Dict[str, Any], Any, float]]
    
    # Optimization metadata
    optimization_metric: str
    total_combinations: int
    completed_combinations: int
    optimization_time_seconds: float
    
    # Analysis
    parameter_sensitivity: Dict[str, float] = field(default_factory=dict)
    
    def get_top_results(self, n: int = 10) -> List[Tuple[Dict[str, Any], Any, float]]:
        """Get top N results sorted by score"""
        sorted_results = sorted(self.all_results, key=lambda x: x[2], reverse=True)
        return sorted_results[:n]


class StrategyOptimizer:
    """Automated strategy parameter optimization"""
    
    def __init__(self, base_config: EnhancedTradingConfig, backtest_config: BacktestConfig):
        self.base_config = base_config
        self.backtest_config = backtest_config
        
        # Set optimization mode for faster execution
        self.backtest_config.mode = BacktestMode.OPTIMIZATION
        self.backtest_config.save_trades = False
        self.backtest_config.save_signals = False
        self.backtest_config.generate_charts = False
        
        logger.info("StrategyOptimizer initialized")
    
    def optimize_parameters(
        self,
        parameter_ranges: List[ParameterRange],
        optimization_metric: str = "sharpe_ratio",
        max_workers: int = 1,  # Simplified to single-threaded for now
        max_combinations: Optional[int] = None
    ) -> OptimizationResult:
        """
        Optimize strategy parameters using grid search
        """
        
        start_time = datetime.now()
        logger.info(f"Starting parameter optimization with {len(parameter_ranges)} parameters")
        
        # Generate all parameter combinations
        param_combinations = self._generate_combinations(parameter_ranges, max_combinations)
        total_combinations = len(param_combinations)
        
        logger.info(f"Testing {total_combinations} parameter combinations")
        
        # Run optimizations
        all_results = []
        completed = 0
        
        # Sequential execution (simplified)
        for params in param_combinations:
            try:
                results, score = self._run_single_optimization(params, optimization_metric)
                if results is not None:
                    all_results.append((params, results, score))
                completed += 1
                
                if completed % 10 == 0:
                    logger.info(f"Completed {completed}/{total_combinations} optimizations")
                    
            except Exception as e:
                logger.error(f"Optimization failed for params {params}: {e}")
                completed += 1
        
        end_time = datetime.now()
        optimization_time = (end_time - start_time).total_seconds()
        
        if not all_results:
            raise ValueError("No successful optimizations completed")
        
        # Find best result
        best_params, best_results, best_score = max(all_results, key=lambda x: x[2])
        
        # Create best configuration
        best_config = deepcopy(self.base_config)
        for param_name, param_value in best_params.items():
            setattr(best_config, param_name, param_value)
        
        # Create optimization result
        optimization_result = OptimizationResult(
            best_config=best_config,
            best_results=best_results,
            best_score=best_score,
            all_results=all_results,
            optimization_metric=optimization_metric,
            total_combinations=total_combinations,
            completed_combinations=completed,
            optimization_time_seconds=optimization_time
        )
        
        # Calculate parameter sensitivity
        optimization_result.parameter_sensitivity = self._calculate_parameter_sensitivity(all_results)
        
        logger.info(f"Optimization completed in {optimization_time:.1f}s")
        logger.info(f"Best {optimization_metric}: {best_score:.4f}")
        
        return optimization_result
    
    def _generate_combinations(
        self, 
        parameter_ranges: List[ParameterRange], 
        max_combinations: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Generate all parameter combinations"""
        
        # Get all possible values for each parameter
        param_values = {}
        for param_range in parameter_ranges:
            param_values[param_range.name] = param_range.get_values()
        
        # Generate all combinations
        param_names = list(param_values.keys())
        value_combinations = list(product(*[param_values[name] for name in param_names]))
        
        # Convert to list of dictionaries
        combinations = []
        for value_combo in value_combinations:
            param_dict = dict(zip(param_names, value_combo))
            combinations.append(param_dict)
        
        # Limit combinations if requested
        if max_combinations and len(combinations) > max_combinations:
            # Use random sampling to get diverse combinations
            np.random.seed(42)
            indices = np.random.choice(len(combinations), max_combinations, replace=False)
            combinations = [combinations[i] for i in indices]
            logger.info(f"Limited to {max_combinations} random combinations")
        
        return combinations
    
    def _run_single_optimization(self, params: Dict[str, Any], optimization_metric: str) -> Tuple[Any, float]:
        """Run a single optimization with given parameters"""
        
        try:
            # Create configuration with new parameters
            config = deepcopy(self.base_config)
            for param_name, param_value in params.items():
                if hasattr(config, param_name):
                    setattr(config, param_name, param_value)
                else:
                    logger.warning(f"Parameter {param_name} not found in config")
            
            # Run backtest
            engine = BacktestEngine(self.backtest_config)
            results = engine.run_backtest(config)
            
            # Calculate score based on optimization metric
            score = self._calculate_score(results, optimization_metric)
            
            return results, score
            
        except Exception as e:
            logger.error(f"Single optimization failed: {e}")
            return None, float('-inf')
    
    def _calculate_score(self, results, optimization_metric: str) -> float:
        """Calculate optimization score from results"""
        
        # Handle different metrics
        if optimization_metric == "sharpe_ratio":
            return results.metrics.get('sharpe_ratio', -999)
        elif optimization_metric == "total_return":
            return results.total_return
        elif optimization_metric == "calmar_ratio":
            return results.metrics.get('calmar_ratio', -999)
        elif optimization_metric == "sortino_ratio":
            return results.metrics.get('sortino_ratio', -999)
        elif optimization_metric == "profit_factor":
            return results.metrics.get('profit_factor', 0)
        elif optimization_metric == "win_rate":
            return results.metrics.get('win_rate', 0)
        elif optimization_metric == "max_drawdown":
            # Negative because we want to minimize drawdown
            return -abs(results.risk_metrics.get('max_drawdown', 100))
        elif optimization_metric == "custom_score":
            # Custom composite score
            sharpe = results.metrics.get('sharpe_ratio', 0)
            return_pct = results.total_return / 100
            max_dd = abs(results.risk_metrics.get('max_drawdown', 100)) / 100
            win_rate = results.metrics.get('win_rate', 0)
            
            # Weighted composite score
            score = (sharpe * 0.4) + (return_pct * 0.3) + (win_rate * 0.2) - (max_dd * 0.1)
            return score
        else:
            logger.warning(f"Unknown optimization metric: {optimization_metric}")
            return results.total_return
    
    def _calculate_parameter_sensitivity(self, all_results: List[Tuple[Dict[str, Any], Any, float]]) -> Dict[str, float]:
        """Calculate how sensitive the score is to each parameter"""
        
        if len(all_results) < 2:
            return {}
        
        # Extract parameter values and scores
        param_data = {}
        scores = []
        
        for params, results, score in all_results:
            scores.append(score)
            for param_name, param_value in params.items():
                if param_name not in param_data:
                    param_data[param_name] = []
                param_data[param_name].append(param_value)
        
        # Calculate correlation between each parameter and score
        sensitivity = {}
        for param_name, values in param_data.items():
            if len(set(values)) > 1:  # Only if parameter varies
                try:
                    correlation = np.corrcoef(values, scores)[0, 1]
                    sensitivity[param_name] = abs(correlation) if not np.isnan(correlation) else 0
                except:
                    sensitivity[param_name] = 0
            else:
                sensitivity[param_name] = 0
        
        return sensitivity
    
    def get_default_parameter_ranges(self) -> List[ParameterRange]:
        """Get default parameter ranges for common strategy parameters"""
        
        return [
            # RSI parameters
            ParameterRange("rsi_period", 10, 20, 2, "int"),
            ParameterRange("rsi_oversold", 20, 35, 5, "float"),
            ParameterRange("rsi_overbought", 65, 80, 5, "float"),
            
            # EMA parameters
            ParameterRange("ema_short", 5, 15, 2, "int"),
            ParameterRange("ema_medium", 15, 30, 3, "int"),
            ParameterRange("ema_long", 40, 60, 5, "int"),
            
            # Risk management
            ParameterRange("max_position_size_percent", 0.5, 3.0, 0.5, "float"),
            ParameterRange("base_stop_loss_percent", 1.0, 5.0, 0.5, "float"),
            ParameterRange("base_take_profit_percent", 3.0, 10.0, 1.0, "float"),
            
            # Confidence thresholds
            ParameterRange("min_confidence_buy", 0.5, 0.8, 0.05, "float"),
            ParameterRange("min_confidence_sell", 0.5, 0.8, 0.05, "float"),
        ]
