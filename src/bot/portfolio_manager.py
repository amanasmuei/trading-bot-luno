"""
Multi-Pair Portfolio Manager
Advanced portfolio management for diversified trading across multiple pairs
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from src.config.enhanced_settings import ENHANCED_SUPPORTED_PAIRS
from src.api.luno_client import LunoAPIClient

logger = logging.getLogger(__name__)


class AllocationStrategy(Enum):
    """Portfolio allocation strategies"""
    EQUAL_WEIGHT = "equal_weight"
    VOLATILITY_WEIGHTED = "volatility_weighted"
    MOMENTUM_WEIGHTED = "momentum_weighted"
    RISK_PARITY = "risk_parity"
    DYNAMIC_REBALANCING = "dynamic_rebalancing"


@dataclass
class PairAllocation:
    """Individual trading pair allocation"""
    pair: str
    target_weight: float
    current_weight: float
    position_size: float
    unrealized_pnl: float
    daily_pnl: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    last_rebalance: datetime
    
    
@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: float
    total_pnl: float
    daily_pnl: float
    portfolio_volatility: float
    portfolio_sharpe: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    correlation_matrix: Dict[str, Dict[str, float]]
    diversification_ratio: float
    var_95: float  # Value at Risk 95%
    expected_shortfall: float


class MultiPairPortfolioManager:
    """Advanced multi-pair portfolio management system"""
    
    def __init__(self, client: LunoAPIClient, config, 
                 allocation_strategy: AllocationStrategy = AllocationStrategy.DYNAMIC_REBALANCING):
        self.client = client
        self.config = config
        self.allocation_strategy = allocation_strategy
        
        # Portfolio state
        self.allocations: Dict[str, PairAllocation] = {}
        self.price_history: Dict[str, List[float]] = {}
        self.return_history: Dict[str, List[float]] = {}
        self.portfolio_history: List[Dict] = []
        
        # Risk management
        self.max_portfolio_risk = 0.15  # 15% max portfolio risk
        self.rebalance_threshold = 0.05  # 5% deviation triggers rebalance
        self.correlation_threshold = 0.7  # High correlation threshold
        
        # Performance tracking
        self.start_time = datetime.now()
        self.last_rebalance = datetime.now()
        
        # Initialize supported pairs
        self._initialize_portfolio()
        
    def _initialize_portfolio(self):
        """Initialize portfolio with supported trading pairs"""
        supported_pairs = list(ENHANCED_SUPPORTED_PAIRS.keys())
        
        # Filter pairs based on configuration or user preferences
        active_pairs = self._select_active_pairs(supported_pairs)
        
        # Calculate initial allocations
        initial_allocations = self._calculate_initial_allocations(active_pairs)
        
        for pair, weight in initial_allocations.items():
            self.allocations[pair] = PairAllocation(
                pair=pair,
                target_weight=weight,
                current_weight=0.0,
                position_size=0.0,
                unrealized_pnl=0.0,
                daily_pnl=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                last_rebalance=datetime.now()
            )
            
            # Initialize price history
            self.price_history[pair] = []
            self.return_history[pair] = []
            
        logger.info(f"Portfolio initialized with {len(active_pairs)} pairs: {active_pairs}")
    
    def _select_active_pairs(self, supported_pairs: List[str]) -> List[str]:
        """Select active trading pairs based on criteria"""
        # For now, select top pairs by volume and liquidity
        # In production, this could be based on user preferences, market conditions, etc.
        
        priority_pairs = [
            "XBTMYR", "XBTZAR", "XBTEUR",  # Bitcoin pairs
            "ETHMYR", "ETHZAR", "ETHXBT",  # Ethereum pairs
            "LTCMYR", "LTCZAR"             # Litecoin pairs
        ]
        
        # Filter to only include supported pairs
        active_pairs = [pair for pair in priority_pairs if pair in supported_pairs]
        
        # Limit to maximum number of pairs for manageable portfolio
        max_pairs = getattr(self.config, 'max_portfolio_pairs', 6)
        return active_pairs[:max_pairs]
    
    def _calculate_initial_allocations(self, pairs: List[str]) -> Dict[str, float]:
        """Calculate initial portfolio allocations"""
        if self.allocation_strategy == AllocationStrategy.EQUAL_WEIGHT:
            weight = 1.0 / len(pairs)
            return {pair: weight for pair in pairs}
            
        elif self.allocation_strategy == AllocationStrategy.VOLATILITY_WEIGHTED:
            # Inverse volatility weighting (lower volatility = higher weight)
            volatilities = self._estimate_pair_volatilities(pairs)
            inv_vol = {pair: 1.0 / vol for pair, vol in volatilities.items()}
            total_inv_vol = sum(inv_vol.values())
            return {pair: weight / total_inv_vol for pair, weight in inv_vol.items()}
            
        elif self.allocation_strategy == AllocationStrategy.MOMENTUM_WEIGHTED:
            # Momentum-based weighting
            momentum_scores = self._calculate_momentum_scores(pairs)
            total_momentum = sum(momentum_scores.values())
            if total_momentum > 0:
                return {pair: score / total_momentum for pair, score in momentum_scores.items()}
            else:
                # Fallback to equal weight
                weight = 1.0 / len(pairs)
                return {pair: weight for pair in pairs}
                
        else:  # Default to equal weight
            weight = 1.0 / len(pairs)
            return {pair: weight for pair in pairs}
    
    def _estimate_pair_volatilities(self, pairs: List[str]) -> Dict[str, float]:
        """Estimate volatility for each trading pair"""
        volatilities = {}
        
        for pair in pairs:
            try:
                # Get recent price data
                ticker = self.client.get_ticker(pair)
                current_price = float(ticker.get("last_trade", 0))
                
                # Use pair characteristics to estimate volatility
                pair_info = ENHANCED_SUPPORTED_PAIRS.get(pair, {})
                volatility_class = pair_info.get("volatility_class", "medium")
                
                if volatility_class == "high":
                    base_vol = 0.04  # 4% daily volatility
                elif volatility_class == "low":
                    base_vol = 0.02  # 2% daily volatility
                else:
                    base_vol = 0.03  # 3% daily volatility
                    
                volatilities[pair] = base_vol
                
            except Exception as e:
                logger.warning(f"Could not estimate volatility for {pair}: {e}")
                volatilities[pair] = 0.03  # Default volatility
                
        return volatilities
    
    def _calculate_momentum_scores(self, pairs: List[str]) -> Dict[str, float]:
        """Calculate momentum scores for each pair"""
        momentum_scores = {}
        
        for pair in pairs:
            try:
                # Get recent price data
                ticker = self.client.get_ticker(pair)
                current_price = float(ticker.get("last_trade", 0))
                
                # Simple momentum calculation (would be enhanced with historical data)
                # For now, use a placeholder momentum score
                momentum_scores[pair] = max(0.1, np.random.uniform(0.5, 1.5))
                
            except Exception as e:
                logger.warning(f"Could not calculate momentum for {pair}: {e}")
                momentum_scores[pair] = 1.0  # Neutral momentum
                
        return momentum_scores
    
    def update_portfolio_state(self) -> PortfolioMetrics:
        """Update portfolio state and calculate metrics"""
        total_portfolio_value = 0.0
        total_pnl = 0.0
        daily_pnl = 0.0
        
        # Update each pair's allocation
        for pair, allocation in self.allocations.items():
            try:
                # Get current market data
                ticker = self.client.get_ticker(pair)
                current_price = float(ticker.get("last_trade", 0))
                
                # Update price history
                self.price_history[pair].append(current_price)
                if len(self.price_history[pair]) > 100:  # Keep last 100 prices
                    self.price_history[pair] = self.price_history[pair][-100:]
                
                # Calculate returns
                if len(self.price_history[pair]) > 1:
                    returns = np.diff(self.price_history[pair]) / self.price_history[pair][:-1]
                    self.return_history[pair] = returns.tolist()
                
                # Update allocation metrics
                allocation.volatility = np.std(self.return_history[pair]) if self.return_history[pair] else 0.0
                
                # Calculate position value (placeholder - would use actual positions)
                position_value = allocation.position_size * current_price
                total_portfolio_value += position_value
                
            except Exception as e:
                logger.error(f"Error updating {pair}: {e}")
        
        # Calculate portfolio metrics
        portfolio_metrics = self._calculate_portfolio_metrics(total_portfolio_value)
        
        # Check if rebalancing is needed
        if self._should_rebalance():
            self._rebalance_portfolio()
        
        return portfolio_metrics
    
    def _calculate_portfolio_metrics(self, total_value: float) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        
        # Calculate portfolio returns
        portfolio_returns = []
        if len(self.portfolio_history) > 1:
            for i in range(1, len(self.portfolio_history)):
                prev_value = self.portfolio_history[i-1].get("total_value", total_value)
                curr_value = self.portfolio_history[i].get("total_value", total_value)
                if prev_value > 0:
                    portfolio_returns.append((curr_value - prev_value) / prev_value)
        
        # Portfolio volatility
        portfolio_volatility = np.std(portfolio_returns) if portfolio_returns else 0.0
        
        # Portfolio Sharpe ratio (assuming 3% risk-free rate)
        if portfolio_volatility > 0:
            excess_return = np.mean(portfolio_returns) - 0.03/252  # Daily risk-free rate
            portfolio_sharpe = excess_return / portfolio_volatility
        else:
            portfolio_sharpe = 0.0
        
        # Maximum drawdown
        if len(self.portfolio_history) > 1:
            values = [h.get("total_value", total_value) for h in self.portfolio_history]
            running_max = np.maximum.accumulate(values)
            drawdowns = (np.array(values) - running_max) / running_max
            max_drawdown = np.min(drawdowns)
        else:
            max_drawdown = 0.0
        
        # Correlation matrix
        correlation_matrix = self._calculate_correlation_matrix()
        
        # Diversification ratio
        diversification_ratio = self._calculate_diversification_ratio(correlation_matrix)
        
        return PortfolioMetrics(
            total_value=total_value,
            total_pnl=0.0,  # Would calculate from actual positions
            daily_pnl=0.0,  # Would calculate from actual positions
            portfolio_volatility=portfolio_volatility,
            portfolio_sharpe=portfolio_sharpe,
            max_drawdown=max_drawdown,
            win_rate=0.0,  # Would calculate from trade history
            profit_factor=0.0,  # Would calculate from trade history
            correlation_matrix=correlation_matrix,
            diversification_ratio=diversification_ratio,
            var_95=0.0,  # Would calculate VaR
            expected_shortfall=0.0  # Would calculate Expected Shortfall
        )
    
    def _calculate_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between pairs"""
        correlation_matrix = {}
        pairs = list(self.allocations.keys())
        
        for pair1 in pairs:
            correlation_matrix[pair1] = {}
            for pair2 in pairs:
                if pair1 == pair2:
                    correlation_matrix[pair1][pair2] = 1.0
                else:
                    returns1 = self.return_history.get(pair1, [])
                    returns2 = self.return_history.get(pair2, [])
                    
                    if len(returns1) > 10 and len(returns2) > 10:
                        min_len = min(len(returns1), len(returns2))
                        corr = np.corrcoef(returns1[-min_len:], returns2[-min_len:])[0, 1]
                        correlation_matrix[pair1][pair2] = corr if not np.isnan(corr) else 0.0
                    else:
                        correlation_matrix[pair1][pair2] = 0.0
        
        return correlation_matrix
    
    def _calculate_diversification_ratio(self, correlation_matrix: Dict[str, Dict[str, float]]) -> float:
        """Calculate portfolio diversification ratio"""
        pairs = list(self.allocations.keys())
        if len(pairs) < 2:
            return 1.0
        
        # Weighted average volatility
        weighted_vol = sum(
            self.allocations[pair].target_weight * self.allocations[pair].volatility
            for pair in pairs
        )
        
        # Portfolio volatility (simplified calculation)
        portfolio_variance = 0.0
        for pair1 in pairs:
            for pair2 in pairs:
                weight1 = self.allocations[pair1].target_weight
                weight2 = self.allocations[pair2].target_weight
                vol1 = self.allocations[pair1].volatility
                vol2 = self.allocations[pair2].volatility
                corr = correlation_matrix.get(pair1, {}).get(pair2, 0.0)
                
                portfolio_variance += weight1 * weight2 * vol1 * vol2 * corr
        
        portfolio_vol = np.sqrt(portfolio_variance)
        
        if portfolio_vol > 0:
            diversification_ratio = weighted_vol / portfolio_vol
        else:
            diversification_ratio = 1.0
        
        return diversification_ratio
    
    def _should_rebalance(self) -> bool:
        """Determine if portfolio should be rebalanced"""
        # Check time since last rebalance
        time_since_rebalance = datetime.now() - self.last_rebalance
        if time_since_rebalance < timedelta(hours=6):  # Minimum 6 hours between rebalances
            return False
        
        # Check allocation drift
        for pair, allocation in self.allocations.items():
            drift = abs(allocation.current_weight - allocation.target_weight)
            if drift > self.rebalance_threshold:
                logger.info(f"Rebalancing triggered by {pair}: drift = {drift:.3f}")
                return True
        
        return False
    
    def _rebalance_portfolio(self):
        """Rebalance portfolio to target allocations"""
        logger.info("Starting portfolio rebalancing...")
        
        # Update target allocations based on current strategy
        if self.allocation_strategy == AllocationStrategy.DYNAMIC_REBALANCING:
            self._update_dynamic_allocations()
        
        # Execute rebalancing trades (placeholder)
        for pair, allocation in self.allocations.items():
            target_weight = allocation.target_weight
            current_weight = allocation.current_weight
            
            if abs(target_weight - current_weight) > self.rebalance_threshold:
                logger.info(f"Rebalancing {pair}: {current_weight:.3f} -> {target_weight:.3f}")
                # In production, this would execute actual trades
        
        self.last_rebalance = datetime.now()
        logger.info("Portfolio rebalancing completed")
    
    def _update_dynamic_allocations(self):
        """Update allocations for dynamic rebalancing strategy"""
        # Recalculate allocations based on recent performance and market conditions
        pairs = list(self.allocations.keys())
        
        # Calculate momentum and volatility scores
        momentum_scores = {}
        volatility_scores = {}
        
        for pair in pairs:
            returns = self.return_history.get(pair, [])
            if len(returns) > 10:
                # Momentum score (recent performance)
                momentum_scores[pair] = np.mean(returns[-10:])
                # Volatility score (inverse volatility)
                volatility_scores[pair] = 1.0 / (np.std(returns[-20:]) + 0.001)
            else:
                momentum_scores[pair] = 0.0
                volatility_scores[pair] = 1.0
        
        # Combine scores (50% momentum, 50% inverse volatility)
        combined_scores = {}
        for pair in pairs:
            combined_scores[pair] = 0.5 * momentum_scores[pair] + 0.5 * volatility_scores[pair]
        
        # Normalize to get new target weights
        total_score = sum(max(0.1, score) for score in combined_scores.values())  # Minimum weight
        
        for pair in pairs:
            new_weight = max(0.1, combined_scores[pair]) / total_score
            self.allocations[pair].target_weight = new_weight
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        metrics = self.update_portfolio_state()
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_pairs": len(self.allocations),
            "allocation_strategy": self.allocation_strategy.value,
            "metrics": {
                "total_value": metrics.total_value,
                "portfolio_volatility": metrics.portfolio_volatility,
                "sharpe_ratio": metrics.portfolio_sharpe,
                "max_drawdown": metrics.max_drawdown,
                "diversification_ratio": metrics.diversification_ratio
            },
            "allocations": {
                pair: {
                    "target_weight": alloc.target_weight,
                    "current_weight": alloc.current_weight,
                    "volatility": alloc.volatility,
                    "sharpe_ratio": alloc.sharpe_ratio
                }
                for pair, alloc in self.allocations.items()
            }
        }
        
        return summary
