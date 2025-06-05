"""
Enhanced Trading Bot Engine
Advanced cryptocurrency trading bot with improved strategy and risk management
"""

import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import signal
import sys
import threading
from dataclasses import asdict
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from src.config.enhanced_settings import (
    EnhancedTradingConfig,
    ENHANCED_TRADING_SIGNALS,
    RISK_MANAGEMENT_RULES,
    MARKET_REGIMES,
    ENHANCED_SUPPORTED_PAIRS,
    ENHANCED_TRADING_HOURS,
    PERFORMANCE_CONFIG,
)
from src.bot.enhanced_technical_analysis import (
    EnhancedTechnicalAnalyzer,
    EnhancedTechnicalIndicators,
    TradingSignal,
    SignalStrength,
    MarketRegime,
)
from src.api.luno_client import LunoAPIClient, TradingPortfolio
from src.bot.health_server import HealthCheckServer


# Configure logging with error handling
def setup_logging():
    """Setup logging with graceful error handling for Docker permissions"""
    handlers = [logging.StreamHandler(sys.stdout)]

    # Try to add file handler, but gracefully handle permission errors
    try:
        import os

        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/enhanced_trading_bot.log")
        handlers.append(file_handler)
    except (PermissionError, OSError) as e:
        print(f"⚠️  Warning: Cannot write to log file: {e}")
        print("📝 Logging will continue to console only")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


setup_logging()

logger = logging.getLogger(__name__)


class EnhancedRiskManager:
    """Advanced risk management system"""

    def __init__(self, config: EnhancedTradingConfig):
        self.config = config
        self.daily_pnl = 0.0
        self.consecutive_losses = 0
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()

    def check_daily_limits(self) -> bool:
        """Check if daily limits are exceeded"""
        current_date = datetime.now().date()

        # Reset daily counters if new day
        if current_date != self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.last_reset_date = current_date

        # Check daily trade limit
        if self.daily_trades >= RISK_MANAGEMENT_RULES["daily_limits"]["max_trades"]:
            logger.warning("Daily trade limit reached")
            return False

        # Check daily loss limit
        max_daily_loss = RISK_MANAGEMENT_RULES["daily_limits"]["max_loss_percent"]
        if self.daily_pnl < -max_daily_loss:
            logger.warning(f"Daily loss limit exceeded: {self.daily_pnl:.2f}%")
            return False

        # Check consecutive losses
        max_consecutive = RISK_MANAGEMENT_RULES["daily_limits"][
            "max_consecutive_losses"
        ]
        if self.consecutive_losses >= max_consecutive:
            logger.warning(
                f"Maximum consecutive losses reached: {self.consecutive_losses}"
            )
            return False

        return True

    def calculate_position_size(
        self, signal: TradingSignal, portfolio_value: float, current_price: float
    ) -> float:
        """Calculate position size based on signal strength and risk parameters"""

        # Base position size
        base_percent = RISK_MANAGEMENT_RULES["position_sizing"]["base_percent"]
        base_size = portfolio_value * (base_percent / 100)

        # Adjust for signal confidence
        if RISK_MANAGEMENT_RULES["position_sizing"]["confidence_scaling"]:
            confidence_multiplier = 0.5 + (signal.confidence * 0.5)  # 0.5 to 1.0
            base_size *= confidence_multiplier

        # Adjust for volatility
        if RISK_MANAGEMENT_RULES["position_sizing"]["volatility_adjustment"]:
            base_size *= signal.position_size_multiplier

        # Apply signal-specific multiplier
        signal_config = ENHANCED_TRADING_SIGNALS.get(
            f"{signal.strength.name}_{signal.action}", {}
        )
        if "position_multiplier" in signal_config:
            base_size *= signal_config["position_multiplier"]

        # Convert to volume
        volume = base_size / current_price

        # Apply min/max constraints
        min_multiplier = self.config.min_position_multiplier
        max_multiplier = self.config.max_position_multiplier

        volume = max(volume * min_multiplier, min(volume * max_multiplier, volume))

        return volume

    def update_trade_result(self, pnl_percent: float):
        """Update risk metrics with trade result"""
        self.daily_pnl += pnl_percent
        self.daily_trades += 1

        if pnl_percent < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        logger.info(
            f"Trade result: {pnl_percent:.2f}% | Daily PnL: {self.daily_pnl:.2f}% | Consecutive losses: {self.consecutive_losses}"
        )


class PerformanceTracker:
    """Track and analyze trading performance"""

    def __init__(self, config: EnhancedTradingConfig):
        self.config = config
        self.trades = []
        self.portfolio_history = []
        self.start_time = datetime.now()
        self.initial_portfolio_value = 0.0

    def record_trade(self, trade_data: Dict):
        """Record a completed trade"""
        trade_data["timestamp"] = datetime.now()
        self.trades.append(trade_data)

    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {}

        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t.get("pnl_percent", 0) > 0])
        losing_trades = total_trades - winning_trades

        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        total_return = sum(t.get("pnl_percent", 0) for t in self.trades)

        # Average win/loss
        wins = [t["pnl_percent"] for t in self.trades if t.get("pnl_percent", 0) > 0]
        losses = [t["pnl_percent"] for t in self.trades if t.get("pnl_percent", 0) < 0]

        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        avg_win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0

        # Profit factor
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_return": total_return,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "avg_win_loss_ratio": avg_win_loss_ratio,
            "profit_factor": profit_factor,
        }


class EnhancedTradingBot:
    """Advanced cryptocurrency trading bot with enhanced strategy"""

    def __init__(self, config: EnhancedTradingConfig):
        self.config = config
        self.running = False

        # Validate trading pair
        self._validate_trading_pair()

        # Initialize components
        self.client = LunoAPIClient(config.api_key, config.api_secret)
        self.portfolio = TradingPortfolio(self.client, config)
        self.analyzer = EnhancedTechnicalAnalyzer(config)
        self.risk_manager = EnhancedRiskManager(config)
        self.performance_tracker = PerformanceTracker(config)

        # Initialize health check server
        self.health_server = HealthCheckServer(port=5002)

        # Trading state
        self.last_trade_time = None
        self.current_signals_history = []
        self.market_regime_history = []

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("Enhanced Luno Trading Bot initialized")
        logger.info(f"Dry run mode: {config.dry_run}")
        logger.info(f"Trading pair: {config.trading_pair}")
        logger.info(f"Enhanced strategy: ENABLED")

    def _validate_trading_pair(self):
        """Validate that the trading pair is supported"""
        if self.config.trading_pair not in ENHANCED_SUPPORTED_PAIRS:
            supported_list = ", ".join(ENHANCED_SUPPORTED_PAIRS.keys())
            raise ValueError(
                f"Unsupported trading pair: {self.config.trading_pair}. "
                f"Supported pairs: {supported_list}"
            )

        pair_info = ENHANCED_SUPPORTED_PAIRS[self.config.trading_pair]
        logger.info(f"Trading pair validated: {pair_info['name']}")
        logger.info(f"Volatility class: {pair_info['volatility_class']}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()

    def start(self):
        """Start the enhanced trading bot"""
        logger.info("Starting Enhanced Trading Bot...")
        self.running = True

        # Start health check server
        self.health_server.start()

        # Initial setup
        self._update_portfolio_state()
        self._log_initial_state()

        # Main trading loop
        try:
            while self.running:
                self._enhanced_trading_cycle()
                time.sleep(self.config.check_interval)

        except Exception as e:
            logger.error(f"Critical error in trading loop: {e}")
            self.stop()

    def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping Enhanced Trading Bot...")
        self.running = False

        # Stop health check server
        if hasattr(self, "health_server"):
            self.health_server.stop()

        # Cancel all open orders
        if not self.config.dry_run:
            try:
                cancelled = self.portfolio.cancel_all_orders()
                logger.info(f"Cancelled {cancelled} open orders")
            except Exception as e:
                logger.warning(f"Error cancelling orders: {e}")

        # Save performance report
        self._save_enhanced_performance_report()
        logger.info("Enhanced Trading Bot stopped")

    def _enhanced_trading_cycle(self):
        """Execute one enhanced trading cycle"""
        try:
            # Update health status
            self.health_server.update_status(
                {
                    "last_cycle": datetime.now().isoformat(),
                    "running": self.running,
                    "daily_trades": self.risk_manager.daily_trades,
                    "daily_pnl": self.risk_manager.daily_pnl,
                }
            )

            # Check daily risk limits
            if not self.risk_manager.check_daily_limits():
                logger.info("Daily risk limits exceeded, skipping cycle")
                return

            # Check time between trades
            if self._should_wait_for_time_filter():
                logger.debug("Time filter active, skipping cycle")
                return

            # Update portfolio state
            self._update_portfolio_state()

            # Get market data
            market_data = self._get_market_data()
            if not market_data:
                logger.warning("Failed to get market data, skipping cycle")
                return

            # Perform enhanced technical analysis
            indicators = self._analyze_market_enhanced(market_data)
            if not indicators:
                logger.warning("Failed to analyze market, skipping cycle")
                return

            # Generate enhanced trading signals
            signal = self.analyzer.generate_enhanced_signals(
                indicators, market_data["current_volume"]
            )

            # Apply market regime filters
            signal = self._apply_market_regime_filters(signal, indicators)

            # Log current state
            self._log_enhanced_market_state(indicators, signal)

            # Execute trading decision
            self._execute_enhanced_trading_decision(signal, indicators, market_data)

            # Store signal history
            self.current_signals_history.append(signal)
            if len(self.current_signals_history) > 100:  # Keep last 100 signals
                self.current_signals_history.pop(0)

        except Exception as e:
            logger.error(f"Error in enhanced trading cycle: {e}")

    def _get_market_data(self) -> Optional[Dict]:
        """Fetch current market data"""
        try:
            # Get current price and ticker
            ticker = self.client.get_ticker(self.config.trading_pair)
            current_price = float(ticker["last_trade"])
            current_volume = float(ticker.get("rolling_24_hour_volume", 0))

            # Get historical candles for analysis
            since = int((datetime.now() - timedelta(days=60)).timestamp() * 1000)
            candles_data = self.client.get_candles(
                self.config.trading_pair, 86400, since  # 24h candles
            )

            return {
                "current_price": current_price,
                "current_volume": current_volume,
                "candles": candles_data.get("candles", []),
                "ticker": ticker,
            }

        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return None

    def _analyze_market_enhanced(
        self, market_data: Dict
    ) -> Optional[EnhancedTechnicalIndicators]:
        """Perform enhanced technical analysis on market data"""
        try:
            volume_data = [float(candle["volume"]) for candle in market_data["candles"]]

            indicators = self.analyzer.analyze_market_data(
                market_data["candles"], market_data["current_price"], volume_data
            )

            return indicators

        except Exception as e:
            logger.error(f"Failed to analyze market: {e}")
            return None

    def _apply_market_regime_filters(
        self, signal: TradingSignal, indicators: EnhancedTechnicalIndicators
    ) -> TradingSignal:
        """Apply market regime-based filters to trading signals"""

        regime_config = MARKET_REGIMES.get(indicators.market_regime.value, {})

        # Check if signal direction is preferred for current regime
        preferred_signals = regime_config.get("preferred_signals", [])
        if preferred_signals and signal.action not in preferred_signals:
            signal.confidence *= 0.7  # Reduce confidence for non-preferred direction
            signal.risk_factors.append(
                f"Against {indicators.market_regime.value} regime bias"
            )

        # Apply regime-specific adjustments
        if "confidence_bonus" in regime_config:
            bonus = regime_config["confidence_bonus"]
            if isinstance(bonus, (int, float)):
                signal.confidence = min(0.95, signal.confidence + bonus)
        elif "confidence_penalty" in regime_config:
            penalty = regime_config["confidence_penalty"]
            if isinstance(penalty, (int, float)):
                signal.confidence = max(0.05, signal.confidence - penalty)

        # Apply risk adjustments
        if "risk_adjustment" in regime_config:
            risk_adj = regime_config["risk_adjustment"]
            if isinstance(risk_adj, (int, float)):
                signal.position_size_multiplier *= risk_adj

        # Apply position multiplier for high volatility
        if "position_multiplier" in regime_config:
            pos_mult = regime_config["position_multiplier"]
            if isinstance(pos_mult, (int, float)):
                signal.position_size_multiplier *= pos_mult

        return signal

    def _execute_enhanced_trading_decision(
        self,
        signal: TradingSignal,
        indicators: EnhancedTechnicalIndicators,
        market_data: Dict,
    ):
        """Execute enhanced trading decision based on signals"""

        # Check minimum confidence thresholds
        if (
            signal.action == "BUY"
            and signal.confidence < self.config.min_confidence_buy
        ):
            logger.debug(
                f"Buy signal confidence {signal.confidence:.1%} below threshold {self.config.min_confidence_buy:.1%}"
            )
            return
        elif (
            signal.action == "SELL"
            and signal.confidence < self.config.min_confidence_sell
        ):
            logger.debug(
                f"Sell signal confidence {signal.confidence:.1%} below threshold {self.config.min_confidence_sell:.1%}"
            )
            return
        elif signal.action == "WAIT":
            return

        # Check risk-reward ratio
        if signal.risk_reward_ratio < self.config.min_risk_reward_ratio:
            logger.warning(
                f"Risk-reward ratio {signal.risk_reward_ratio:.2f} below minimum {self.config.min_risk_reward_ratio}"
            )
            return

        # Calculate position size
        portfolio_data = self.portfolio.get_portfolio_value(
            market_data["current_price"]
        )
        portfolio_value = portfolio_data.get("total_value", 0.0)
        volume = self.risk_manager.calculate_position_size(
            signal, portfolio_value, market_data["current_price"]
        )

        if volume <= 0:
            logger.warning("Calculated position size is zero")
            return

        # Check sufficient balance
        if not self.portfolio.has_sufficient_balance(
            signal.action, volume, market_data["current_price"]
        ):
            logger.warning(f"Insufficient balance for {signal.action} order")
            return

        # Execute trade
        if signal.action == "BUY":
            self._execute_enhanced_buy_order(
                market_data["current_price"], volume, signal
            )
        elif signal.action == "SELL":
            self._execute_enhanced_sell_order(
                market_data["current_price"], volume, signal
            )

    def _execute_enhanced_buy_order(
        self, price: float, volume: float, signal: TradingSignal
    ):
        """Execute enhanced buy order with improved risk management"""

        volume_str = f"{volume:.8f}".rstrip("0").rstrip(".")

        if self.config.dry_run:
            logger.info(
                f"[DRY RUN] BUY {volume_str} {self.config.base_currency} at {price:.2f}"
            )
            logger.info(
                f"[DRY RUN] Stop Loss: {signal.stop_loss:.2f} | Take Profit: {signal.take_profit_1:.2f}"
            )
            logger.info(
                f"[DRY RUN] Risk-Reward: {signal.risk_reward_ratio:.2f} | Confidence: {signal.confidence:.1%}"
            )
            self._record_simulated_enhanced_trade("BUY", price, volume, signal)
            return

        try:
            # Place market buy order
            order_result = self.client.place_order(
                "BID", self.config.trading_pair, volume=volume_str
            )

            order_id = order_result.get("order_id")
            logger.info(f"Enhanced buy order placed: {order_id}")
            logger.info(
                f"Stop Loss: {signal.stop_loss:.2f} | Take Profit 1: {signal.take_profit_1:.2f}"
            )
            if signal.take_profit_2:
                logger.info(f"Take Profit 2: {signal.take_profit_2:.2f}")
            if signal.take_profit_3:
                logger.info(f"Take Profit 3: {signal.take_profit_3:.2f}")

            # Record trade
            self._record_enhanced_trade("BUY", price, volume, order_id, signal)

        except Exception as e:
            logger.error(f"Failed to execute enhanced buy order: {e}")

    def _execute_enhanced_sell_order(
        self, price: float, volume: float, signal: TradingSignal
    ):
        """Execute enhanced sell order with improved risk management"""

        volume_str = f"{volume:.8f}".rstrip("0").rstrip(".")

        if self.config.dry_run:
            logger.info(
                f"[DRY RUN] SELL {volume_str} {self.config.base_currency} at {price:.2f}"
            )
            logger.info(
                f"[DRY RUN] Stop Loss: {signal.stop_loss:.2f} | Take Profit: {signal.take_profit_1:.2f}"
            )
            logger.info(
                f"[DRY RUN] Risk-Reward: {signal.risk_reward_ratio:.2f} | Confidence: {signal.confidence:.1%}"
            )
            self._record_simulated_enhanced_trade("SELL", price, volume, signal)
            return

        try:
            # Place market sell order
            order_result = self.client.place_order(
                "ASK", self.config.trading_pair, volume=volume_str
            )

            order_id = order_result.get("order_id")
            logger.info(f"Enhanced sell order placed: {order_id}")
            logger.info(
                f"Stop Loss: {signal.stop_loss:.2f} | Take Profit 1: {signal.take_profit_1:.2f}"
            )
            if signal.take_profit_2:
                logger.info(f"Take Profit 2: {signal.take_profit_2:.2f}")
            if signal.take_profit_3:
                logger.info(f"Take Profit 3: {signal.take_profit_3:.2f}")

            # Record trade
            self._record_enhanced_trade("SELL", price, volume, order_id, signal)

        except Exception as e:
            logger.error(f"Failed to execute enhanced sell order: {e}")

    def _should_wait_for_time_filter(self) -> bool:
        """Check if we should wait due to time filters"""
        if not self.last_trade_time:
            return False

        time_diff = datetime.now() - self.last_trade_time
        min_time_between = self.config.min_time_between_trades

        return time_diff.total_seconds() < min_time_between

    def _record_enhanced_trade(
        self,
        action: str,
        price: float,
        volume: float,
        order_id: str,
        signal: TradingSignal,
    ):
        """Record enhanced trade with detailed signal information"""

        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "price": price,
            "volume": volume,
            "order_id": order_id,
            "confidence": signal.confidence,
            "strength": signal.strength.name,
            "primary_reasons": signal.primary_reasons,
            "supporting_factors": signal.supporting_factors,
            "risk_factors": signal.risk_factors,
            "stop_loss": signal.stop_loss,
            "take_profit_1": signal.take_profit_1,
            "take_profit_2": signal.take_profit_2,
            "take_profit_3": signal.take_profit_3,
            "risk_reward_ratio": signal.risk_reward_ratio,
            "market_regime": signal.market_regime.value,
            "position_size_multiplier": signal.position_size_multiplier,
        }

        self.performance_tracker.record_trade(trade_record)
        self.last_trade_time = datetime.now()

        logger.info(f"Enhanced trade recorded: {action} {volume:.6f} at {price:.2f}")

    def _record_simulated_enhanced_trade(
        self, action: str, price: float, volume: float, signal: TradingSignal
    ):
        """Record simulated enhanced trade for dry run mode"""

        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "price": price,
            "volume": volume,
            "order_id": "SIMULATED",
            "confidence": signal.confidence,
            "strength": signal.strength.name,
            "primary_reasons": signal.primary_reasons,
            "supporting_factors": signal.supporting_factors,
            "risk_factors": signal.risk_factors,
            "stop_loss": signal.stop_loss,
            "take_profit_1": signal.take_profit_1,
            "risk_reward_ratio": signal.risk_reward_ratio,
            "market_regime": signal.market_regime.value,
            "simulated": True,
        }

        self.performance_tracker.record_trade(trade_record)
        self.last_trade_time = datetime.now()

        logger.info(
            f"[SIMULATED] Enhanced trade recorded: {action} {volume:.6f} at {price:.2f}"
        )

    def _update_portfolio_state(self):
        """Update current portfolio state"""
        try:
            if not self.config.dry_run:
                self.portfolio.update_balances()
                self.portfolio.update_open_orders()

        except Exception as e:
            logger.error(f"Failed to update portfolio state: {e}")

    def _log_initial_state(self):
        """Log initial enhanced bot state"""
        logger.info("=== Enhanced Trading Bot Initial State ===")
        logger.info(f"Config: {self.config.trading_pair}")
        logger.info(f"Max position size: {self.config.max_position_size_percent}%")
        logger.info(f"Base stop loss: {self.config.base_stop_loss_percent}%")
        logger.info(f"Base take profit: {self.config.base_take_profit_percent}%")
        logger.info(
            f"Min confidence buy/sell: {self.config.min_confidence_buy:.1%}/{self.config.min_confidence_sell:.1%}"
        )
        logger.info(f"Min risk-reward ratio: {self.config.min_risk_reward_ratio}")

        if not self.config.dry_run:
            try:
                portfolio_data = self.portfolio.get_portfolio_value(460000)
                portfolio_value = portfolio_data.get("total_value", 0.0)
                logger.info(f"Portfolio value: {portfolio_value}")
            except:
                logger.info("Portfolio value: Unable to calculate")

    def _log_enhanced_market_state(
        self, indicators: EnhancedTechnicalIndicators, signal: TradingSignal
    ):
        """Log current enhanced market state"""
        sentiment = self.analyzer.get_market_sentiment(indicators)

        logger.info("=== Enhanced Market State ===")
        logger.info(f"Price: {indicators.current_price:.2f}")
        logger.info(f"Market Regime: {indicators.market_regime.value}")
        logger.info(
            f"RSI: {indicators.rsi:.1f} (Divergence: {indicators.rsi_divergence})"
        )
        logger.info(
            f"EMA 9/21/50: {indicators.ema_short:.1f}/{indicators.ema_medium:.1f}/{indicators.ema_long:.1f}"
        )
        logger.info(
            f"MACD: {indicators.macd:.2f} (Divergence: {indicators.macd_divergence})"
        )
        logger.info(f"ATR: {indicators.atr:.2f}")
        logger.info(f"Volume Trend: {indicators.volume_trend}")
        logger.info(
            f"Support/Resistance: {indicators.nearest_support:.2f}/{indicators.nearest_resistance:.2f}"
        )
        logger.info(f"Sentiment: {sentiment}")
        logger.info("=== Trading Signal ===")
        logger.info(f"Action: {signal.action} | Strength: {signal.strength.name}")
        logger.info(
            f"Confidence: {signal.confidence:.1%} | RR Ratio: {signal.risk_reward_ratio:.2f}"
        )
        logger.info(f"Primary Reasons: {', '.join(signal.primary_reasons)}")
        if signal.risk_factors:
            logger.info(f"Risk Factors: {', '.join(signal.risk_factors)}")

    def _save_enhanced_performance_report(self):
        """Save enhanced performance report to file"""

        # Calculate performance metrics
        performance_metrics = self.performance_tracker.calculate_metrics()

        report = {
            "bot_config": asdict(self.config),
            "performance_metrics": performance_metrics,
            "trades_history": self.performance_tracker.trades,
            "risk_management": {
                "daily_pnl": self.risk_manager.daily_pnl,
                "consecutive_losses": self.risk_manager.consecutive_losses,
                "daily_trades": self.risk_manager.daily_trades,
            },
            "market_analysis": {
                "total_signals_generated": len(self.current_signals_history),
                "signal_distribution": self._analyze_signal_distribution(),
            },
            "generated_at": datetime.now().isoformat(),
            "bot_version": "Enhanced v2.0",
        }

        filename = (
            f"enhanced_trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            import os

            os.makedirs("enhanced_reports", exist_ok=True)
            filepath = f"enhanced_reports/{filename}"
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"Enhanced performance report saved: {filepath}")

        except Exception as e:
            logger.error(f"Failed to save enhanced performance report: {e}")

    def _analyze_signal_distribution(self) -> Dict:
        """Analyze distribution of generated signals"""
        if not self.current_signals_history:
            return {}

        signal_counts = {"BUY": 0, "SELL": 0, "WAIT": 0}
        strength_counts = {strength.name: 0 for strength in SignalStrength}
        confidence_sum = 0

        for signal in self.current_signals_history:
            signal_counts[signal.action] += 1
            strength_counts[signal.strength.name] += 1
            confidence_sum += signal.confidence

        avg_confidence = confidence_sum / len(self.current_signals_history)

        return {
            "signal_counts": signal_counts,
            "strength_distribution": strength_counts,
            "average_confidence": avg_confidence,
        }


def main():
    """Main entry point for enhanced trading bot"""

    # Load enhanced configuration
    config = EnhancedTradingConfig()

    # Validate configuration
    if not config.api_key or not config.api_secret:
        logger.error("Luno API credentials not configured")
        logger.error("Set LUNO_API_KEY and LUNO_API_SECRET environment variables")
        sys.exit(1)

    # Create and start enhanced bot
    bot = EnhancedTradingBot(config)

    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("Enhanced bot interrupted by user")
        bot.stop()
    except Exception as e:
        logger.error(f"Enhanced bot crashed: {e}")
        bot.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
