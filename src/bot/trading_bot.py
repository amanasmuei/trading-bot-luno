"""
Main Trading Bot Engine
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

from src.config.settings import (
    TradingConfig,
    TRADING_SIGNALS,
    TRADING_HOURS,
    SUPPORTED_PAIRS,
)
from src.bot.technical_analysis import TechnicalAnalyzer, TechnicalIndicators
from src.api.luno_client import LunoAPIClient, TradingPortfolio


# Configure logging with proper error handling
def setup_logging():
    """Setup logging with fallback for permission issues"""
    handlers = [logging.StreamHandler(sys.stdout)]

    # Try to create file handler with proper error handling
    try:
        # Ensure logs directory exists
        import os

        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Set proper permissions on the log file if it exists
        log_file = os.path.join(log_dir, "trading_bot.log")
        if os.path.exists(log_file):
            os.chmod(log_file, 0o666)

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
        print(f"✅ Logging to file: {log_file}")

    except (PermissionError, OSError) as e:
        print(f"⚠️  Warning: Cannot write to log file: {e}")
        print("📝 Logging will continue to console only")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


# Setup logging
setup_logging()

logger = logging.getLogger(__name__)


class TradingBot:
    """Advanced cryptocurrency trading bot for Luno exchange"""

    def __init__(self, config: TradingConfig):
        self.config = config
        self.running = False

        # Validate trading pair
        self._validate_trading_pair()

        self.client = LunoAPIClient(config.api_key, config.api_secret)
        self.portfolio = TradingPortfolio(self.client, config)
        self.analyzer = TechnicalAnalyzer(config)

        # Trading state
        self.daily_trades = 0
        self.last_trade_time = None
        self.current_position = None
        self.stop_loss_order = None
        self.take_profit_order = None

        # Performance tracking
        self.trades_history = []
        self.performance_stats = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0.0,
            "start_time": datetime.now(),
            "last_update": datetime.now(),
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("Luno Trading Bot initialized")
        logger.info(f"Dry run mode: {config.dry_run}")
        logger.info(f"Trading pair: {config.trading_pair}")
        logger.info(f"Base currency: {config.base_currency}")
        logger.info(f"Counter currency: {config.counter_currency}")

    def _validate_trading_pair(self):
        """Validate that the trading pair is supported"""
        from src.config.settings import SUPPORTED_PAIRS

        if self.config.trading_pair not in SUPPORTED_PAIRS:
            supported_list = ", ".join(SUPPORTED_PAIRS.keys())
            raise ValueError(
                f"Unsupported trading pair: {self.config.trading_pair}. "
                f"Supported pairs: {supported_list}"
            )

        pair_info = SUPPORTED_PAIRS[self.config.trading_pair]
        logger.info(f"Trading pair validated: {pair_info['name']}")
        logger.info(f"Minimum volume: {pair_info['min_volume']}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()

    def start(self):
        """Start the trading bot"""
        logger.info("Starting Trading Bot...")
        self.running = True

        # Initial setup
        self._update_portfolio_state()
        self._log_initial_state()

        # Main trading loop
        try:
            while self.running:
                self._trading_cycle()
                time.sleep(self.config.check_interval)

        except Exception as e:
            logger.error(f"Critical error in trading loop: {e}")
            self.stop()

    def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping Trading Bot...")
        self.running = False

        # Cancel all open orders
        if not self.config.dry_run:
            cancelled = self.portfolio.cancel_all_orders()
            logger.info(f"Cancelled {cancelled} open orders")

        # Save performance report
        self._save_performance_report()
        logger.info("Trading Bot stopped")

    def _trading_cycle(self):
        """Execute one trading cycle"""
        try:
            # Check if within trading hours
            if not self._is_trading_hours():
                logger.debug("Outside trading hours, skipping cycle")
                return

            # Update portfolio state
            self._update_portfolio_state()

            # Get market data
            market_data = self._get_market_data()
            if not market_data:
                logger.warning("Failed to get market data, skipping cycle")
                return

            # Perform technical analysis
            indicators = self._analyze_market(market_data)
            if not indicators:
                logger.warning("Failed to analyze market, skipping cycle")
                return

            # Generate trading signals
            signals = self.analyzer.generate_signals(
                indicators, market_data["current_volume"]
            )

            # Log current state
            self._log_market_state(indicators, signals)

            # Execute trading decision
            self._execute_trading_decision(signals, market_data["current_price"])

            # Update performance stats
            self._update_performance_stats()

        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")

    def _get_market_data(self) -> Optional[Dict]:
        """Fetch current market data"""
        try:
            # Get current price
            ticker = self.client.get_ticker(self.config.trading_pair)
            current_price = float(ticker["last_trade"])
            current_volume = float(ticker.get("rolling_24_hour_volume", 0))

            # Get historical candles for analysis
            since = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
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

    def _analyze_market(self, market_data: Dict) -> Optional[TechnicalIndicators]:
        """Perform technical analysis on market data"""
        try:
            volume_data = [float(candle["volume"]) for candle in market_data["candles"]]

            indicators = self.analyzer.analyze_market_data(
                market_data["candles"], market_data["current_price"], volume_data
            )

            return indicators

        except Exception as e:
            logger.error(f"Failed to analyze market: {e}")
            return None

    def _execute_trading_decision(self, signals: Dict, current_price: float):
        """Execute trading decision based on signals"""

        action = signals["action"]
        confidence = signals["confidence"]

        # Check if we should trade
        if not self._should_trade(action, confidence):
            return

        # Check daily trade limit
        if self.daily_trades >= self.config.max_daily_trades:
            logger.info(f"Daily trade limit reached ({self.config.max_daily_trades})")
            return

        # Calculate position size
        volume, volume_str = self.portfolio.calculate_position_size(
            current_price, action
        )

        if volume <= 0:
            logger.warning("Calculated position size is zero")
            return

        # Check sufficient balance
        if not self.portfolio.has_sufficient_balance(action, volume, current_price):
            logger.warning(f"Insufficient balance for {action} order")
            return

        # Execute trade
        if action == "BUY":
            self._execute_buy_order(current_price, volume_str, signals)
        elif action == "SELL":
            self._execute_sell_order(current_price, volume_str, signals)

    def _execute_buy_order(self, price: float, volume: str, signals: Dict):
        """Execute buy order"""

        if self.config.dry_run:
            logger.info(
                f"[DRY RUN] BUY {volume} {self.config.base_currency} at {price}"
            )
            self._record_simulated_trade("BUY", price, float(volume), signals)
            return

        try:
            # Place market buy order
            order_result = self.client.place_order(
                "BID", self.config.trading_pair, volume=volume  # Buy order
            )

            order_id = order_result.get("order_id")
            logger.info(f"Buy order placed: {order_id}")

            # Set stop loss and take profit
            if signals.get("stop_loss") and signals.get("take_profit"):
                self._set_risk_management_orders(order_id, signals, "BUY")

            # Record trade
            self._record_trade("BUY", price, float(volume), order_id, signals)

        except Exception as e:
            logger.error(f"Failed to execute buy order: {e}")

    def _execute_sell_order(self, price: float, volume: str, signals: Dict):
        """Execute sell order"""

        if self.config.dry_run:
            logger.info(
                f"[DRY RUN] SELL {volume} {self.config.base_currency} at {price}"
            )
            self._record_simulated_trade("SELL", price, float(volume), signals)
            return

        try:
            # Place market sell order
            order_result = self.client.place_order(
                "ASK", self.config.trading_pair, volume=volume  # Sell order
            )

            order_id = order_result.get("order_id")
            logger.info(f"Sell order placed: {order_id}")

            # Set stop loss and take profit
            if signals.get("stop_loss") and signals.get("take_profit"):
                self._set_risk_management_orders(order_id, signals, "SELL")

            # Record trade
            self._record_trade("SELL", price, float(volume), order_id, signals)

        except Exception as e:
            logger.error(f"Failed to execute sell order: {e}")

    def _should_trade(self, action: str, confidence: float) -> bool:
        """Determine if we should execute a trade"""

        if action == "WAIT":
            return False

        # Confidence threshold
        min_confidence = 0.7
        if confidence < min_confidence:
            logger.debug(
                f"Confidence {confidence:.1%} below threshold {min_confidence:.1%}"
            )
            return False

        # Time since last trade
        if self.last_trade_time:
            time_diff = datetime.now() - self.last_trade_time
            if time_diff.total_seconds() < 3600:  # 1 hour minimum between trades
                logger.debug("Too soon since last trade")
                return False

        return True

    def _set_risk_management_orders(
        self, parent_order_id: str, signals: Dict, side: str
    ):
        """Set stop loss and take profit orders"""
        # This would be implemented based on Luno's specific order management
        # For now, we'll log the intended risk management

        stop_loss = signals.get("stop_loss")
        take_profit = signals.get("take_profit")

        logger.info(f"Risk management for {parent_order_id}:")
        logger.info(f"  Stop Loss: {stop_loss}")
        logger.info(f"  Take Profit: {take_profit}")

    def _record_trade(
        self, action: str, price: float, volume: float, order_id: str, signals: Dict
    ):
        """Record trade in history"""

        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "price": price,
            "volume": volume,
            "order_id": order_id,
            "confidence": signals.get("confidence", 0),
            "reasons": signals.get("reasons", []),
            "stop_loss": signals.get("stop_loss"),
            "take_profit": signals.get("take_profit"),
        }

        self.trades_history.append(trade_record)
        self.daily_trades += 1
        self.last_trade_time = datetime.now()

        logger.info(f"Trade recorded: {action} {volume} at {price}")

    def _record_simulated_trade(
        self, action: str, price: float, volume: float, signals: Dict
    ):
        """Record simulated trade for dry run mode"""

        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "price": price,
            "volume": volume,
            "order_id": "SIMULATED",
            "confidence": signals.get("confidence", 0),
            "reasons": signals.get("reasons", []),
            "stop_loss": signals.get("stop_loss"),
            "take_profit": signals.get("take_profit"),
            "simulated": True,
        }

        self.trades_history.append(trade_record)
        self.daily_trades += 1
        self.last_trade_time = datetime.now()

        logger.info(f"[SIMULATED] Trade recorded: {action} {volume} at {price}")

    def _update_portfolio_state(self):
        """Update current portfolio state"""
        try:
            if not self.config.dry_run:
                self.portfolio.update_balances()
                self.portfolio.update_open_orders()

        except Exception as e:
            logger.error(f"Failed to update portfolio state: {e}")

    def _is_trading_hours(self) -> bool:
        """Check if current time is within trading hours"""
        # For crypto, we can trade 24/7, but this allows for preferred hours
        now = datetime.now()
        current_hour = now.hour

        return TRADING_HOURS["start"] <= current_hour <= TRADING_HOURS["end"]

    def _log_initial_state(self):
        """Log initial bot state"""
        logger.info("=== Trading Bot Initial State ===")
        logger.info(f"Config: {self.config.trading_pair}")
        logger.info(f"Max position size: {self.config.max_position_size_percent}%")
        logger.info(f"Stop loss: {self.config.stop_loss_percent}%")
        logger.info(f"Take profit: {self.config.take_profit_percent}%")

        if not self.config.dry_run:
            portfolio_value = self.portfolio.get_portfolio_value(
                460000
            )  # Approximate current price
            logger.info(f"Portfolio value: {portfolio_value}")

    def _log_market_state(self, indicators: TechnicalIndicators, signals: Dict):
        """Log current market state"""
        sentiment = self.analyzer.get_market_sentiment(indicators)

        logger.info(f"=== Market State ===")
        logger.info(f"Price: {indicators.current_price:.2f}")
        logger.info(f"RSI: {indicators.rsi:.1f}")
        logger.info(f"EMA 9/21: {indicators.ema_short:.1f}/{indicators.ema_long:.1f}")
        logger.info(f"MACD: {indicators.macd:.2f}")
        logger.info(f"Sentiment: {sentiment}")
        logger.info(f"Signal: {signals['action']} ({signals['confidence']:.1%})")
        logger.info(f"Reasons: {', '.join(signals['reasons'])}")

    def _update_performance_stats(self):
        """Update performance statistics"""
        self.performance_stats["last_update"] = datetime.now()
        self.performance_stats["total_trades"] = len(self.trades_history)

    def _save_performance_report(self):
        """Save performance report to file"""

        report = {
            "bot_config": asdict(self.config),
            "performance_stats": self.performance_stats,
            "trades_history": self.trades_history,
            "generated_at": datetime.now().isoformat(),
        }

        filename = f"trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"Performance report saved: {filename}")

        except Exception as e:
            logger.error(f"Failed to save performance report: {e}")


def main():
    """Main entry point"""

    # Load configuration
    config = TradingConfig()

    # Validate configuration
    if not config.api_key or not config.api_secret:
        logger.error("Luno API credentials not configured")
        logger.error("Set LUNO_API_KEY and LUNO_API_SECRET environment variables")
        sys.exit(1)

    # Create and start bot
    bot = TradingBot(config)

    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        bot.stop()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        bot.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
