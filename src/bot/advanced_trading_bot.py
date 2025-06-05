"""
Advanced Trading Bot Engine
Next-generation trading bot with comprehensive features and multi-pair support
"""

import time
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import signal
import sys
import threading
from dataclasses import asdict
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from src.config.enhanced_settings import EnhancedTradingConfig
from src.config.strategy_templates import ConfigurationManager, StrategyTemplateManager
from src.bot.enhanced_technical_analysis import EnhancedTechnicalAnalyzer
from src.bot.multi_timeframe_analyzer import MultiTimeFrameAnalyzer, TimeFrame
from src.bot.portfolio_manager import MultiPairPortfolioManager, AllocationStrategy
from src.api.luno_client import LunoAPIClient, TradingPortfolio
from src.notifications.notification_manager import NotificationManager, NotificationConfig, Notification, NotificationType, NotificationPriority
from src.database.database_manager import DatabaseManager, TradeRecord, PerformanceRecord, MarketDataRecord

logger = logging.getLogger(__name__)


class AdvancedTradingBot:
    """Advanced multi-pair trading bot with comprehensive features"""
    
    def __init__(self, config: EnhancedTradingConfig, notification_config: NotificationConfig = None):
        self.config = config
        self.running = False
        
        # Initialize core components
        self.client = LunoAPIClient(config.api_key, config.api_secret)
        self.portfolio = TradingPortfolio(self.client, config)
        self.analyzer = EnhancedTechnicalAnalyzer(config)
        self.multi_timeframe_analyzer = MultiTimeFrameAnalyzer(self.client, config)
        
        # Initialize advanced components
        self.portfolio_manager = MultiPairPortfolioManager(
            self.client, config, AllocationStrategy.DYNAMIC_REBALANCING
        )
        
        # Initialize notification system
        if notification_config:
            self.notification_manager = NotificationManager(notification_config)
        else:
            self.notification_manager = None
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Initialize configuration management
        self.config_manager = ConfigurationManager()
        self.template_manager = StrategyTemplateManager()
        
        # Trading state
        self.start_time = datetime.now()
        self.last_portfolio_update = None
        self.daily_stats = {
            "trades": 0,
            "pnl": 0.0,
            "start_value": 0.0
        }
        
        # Performance tracking
        self.performance_history = []
        self.trade_history = []
        
        # Multi-threading support
        self.analysis_thread = None
        self.portfolio_thread = None
        self.notification_thread = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Advanced Trading Bot initialized")
        
        # Send startup notification
        if self.notification_manager:
            self.notification_manager.send_notification(Notification(
                type=NotificationType.SYSTEM_ERROR,
                priority=NotificationPriority.MEDIUM,
                title="Trading Bot Started",
                message=f"Advanced trading bot started for {config.trading_pair}",
                data={"config": config.trading_pair, "start_time": datetime.now().isoformat()}
            ))
    
    def start(self):
        """Start the advanced trading bot"""
        logger.info("Starting Advanced Trading Bot...")
        self.running = True
        
        # Initialize daily stats
        self.daily_stats["start_value"] = self._get_portfolio_value()
        
        # Start background threads
        self._start_background_threads()
        
        # Main trading loop
        try:
            while self.running:
                self._main_trading_cycle()
                time.sleep(self.config.check_interval)
                
        except Exception as e:
            logger.error(f"Critical error in main trading loop: {e}")
            if self.notification_manager:
                self.notification_manager.notify_system_error(
                    f"Critical trading bot error: {str(e)}",
                    {"error_type": type(e).__name__, "timestamp": datetime.now().isoformat()}
                )
            self.stop()
    
    def stop(self):
        """Stop the trading bot gracefully"""
        logger.info("Stopping Advanced Trading Bot...")
        self.running = False
        
        # Stop background threads
        self._stop_background_threads()
        
        # Cancel all open orders
        if not self.config.dry_run:
            try:
                cancelled = self.portfolio.cancel_all_orders()
                logger.info(f"Cancelled {cancelled} open orders")
            except Exception as e:
                logger.error(f"Error cancelling orders: {e}")
        
        # Save final performance report
        self._save_final_report()
        
        # Close database connection
        self.db_manager.close()
        
        # Send shutdown notification
        if self.notification_manager:
            self.notification_manager.send_notification(Notification(
                type=NotificationType.SYSTEM_ERROR,
                priority=NotificationPriority.MEDIUM,
                title="Trading Bot Stopped",
                message="Advanced trading bot has been stopped",
                data={"stop_time": datetime.now().isoformat()}
            ))
        
        logger.info("Advanced Trading Bot stopped")
    
    def _main_trading_cycle(self):
        """Execute main trading cycle"""
        try:
            # Update portfolio state
            portfolio_metrics = self.portfolio_manager.update_portfolio_state()
            
            # Perform multi-timeframe analysis for each active pair
            for pair in self.portfolio_manager.allocations.keys():
                try:
                    # Get multi-timeframe signal
                    timeframes = [TimeFrame.D1, TimeFrame.H4, TimeFrame.H1]
                    mtf_signal = self.multi_timeframe_analyzer.analyze_multiple_timeframes(pair, timeframes)
                    
                    # Execute trading decision based on signal
                    if mtf_signal.primary_action in ["BUY", "SELL"] and mtf_signal.confidence > 0.6:
                        self._execute_multi_timeframe_trade(pair, mtf_signal)
                    
                    # Store signal in database
                    self.db_manager.store_signal(
                        timestamp=datetime.now(),
                        pair=pair,
                        signal_type="multi_timeframe",
                        action=mtf_signal.primary_action,
                        confidence=mtf_signal.confidence,
                        price=self._get_current_price(pair),
                        indicators={
                            "timeframe_alignment": mtf_signal.timeframe_alignment,
                            "risk_level": mtf_signal.risk_level,
                            "dominant_timeframe": mtf_signal.dominant_timeframe.value
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error analyzing {pair}: {e}")
            
            # Update performance metrics
            self._update_performance_metrics(portfolio_metrics)
            
            # Check for daily summary
            self._check_daily_summary()
            
        except Exception as e:
            logger.error(f"Error in main trading cycle: {e}")
    
    def _execute_multi_timeframe_trade(self, pair: str, signal):
        """Execute trade based on multi-timeframe signal"""
        
        try:
            current_price = self._get_current_price(pair)
            
            # Calculate position size based on signal confidence and risk level
            base_position_size = self.config.max_position_size_percent / 100
            
            # Adjust position size based on signal quality
            confidence_multiplier = signal.confidence
            alignment_multiplier = signal.timeframe_alignment
            
            if signal.risk_level == "LOW":
                risk_multiplier = 1.2
            elif signal.risk_level == "MEDIUM":
                risk_multiplier = 1.0
            else:  # HIGH
                risk_multiplier = 0.7
            
            adjusted_position_size = (base_position_size * 
                                    confidence_multiplier * 
                                    alignment_multiplier * 
                                    risk_multiplier)
            
            # Calculate volume
            portfolio_value = self._get_portfolio_value()
            position_value = portfolio_value * adjusted_position_size
            volume = position_value / current_price
            
            if volume < 0.0001:  # Minimum volume check
                logger.debug(f"Position size too small for {pair}: {volume}")
                return
            
            # Execute trade
            if signal.primary_action == "BUY":
                self._execute_buy_order(pair, current_price, volume, signal)
            elif signal.primary_action == "SELL":
                self._execute_sell_order(pair, current_price, volume, signal)
            
        except Exception as e:
            logger.error(f"Error executing trade for {pair}: {e}")
    
    def _execute_buy_order(self, pair: str, price: float, volume: float, signal):
        """Execute buy order"""
        
        if self.config.dry_run:
            logger.info(f"[DRY RUN] BUY {volume:.6f} {pair} at {price:.2f}")
            self._record_simulated_trade("BUY", pair, price, volume, signal)
            return
        
        try:
            # Place market buy order
            order_result = self.client.place_order("BID", pair, volume=str(volume))
            order_id = order_result.get("order_id")
            
            logger.info(f"Buy order placed for {pair}: {order_id}")
            
            # Record trade
            self._record_trade("BUY", pair, price, volume, order_id, signal)
            
            # Send notification
            if self.notification_manager:
                self.notification_manager.notify_trade_executed({
                    "action": "BUY",
                    "pair": pair,
                    "volume": volume,
                    "price": price,
                    "order_id": order_id,
                    "confidence": signal.confidence,
                    "timeframe_alignment": signal.timeframe_alignment
                })
            
        except Exception as e:
            logger.error(f"Failed to execute buy order for {pair}: {e}")
            if self.notification_manager:
                self.notification_manager.notify_system_error(
                    f"Failed to execute buy order for {pair}: {str(e)}"
                )
    
    def _execute_sell_order(self, pair: str, price: float, volume: float, signal):
        """Execute sell order"""
        
        if self.config.dry_run:
            logger.info(f"[DRY RUN] SELL {volume:.6f} {pair} at {price:.2f}")
            self._record_simulated_trade("SELL", pair, price, volume, signal)
            return
        
        try:
            # Place market sell order
            order_result = self.client.place_order("ASK", pair, volume=str(volume))
            order_id = order_result.get("order_id")
            
            logger.info(f"Sell order placed for {pair}: {order_id}")
            
            # Record trade
            self._record_trade("SELL", pair, price, volume, order_id, signal)
            
            # Send notification
            if self.notification_manager:
                self.notification_manager.notify_trade_executed({
                    "action": "SELL",
                    "pair": pair,
                    "volume": volume,
                    "price": price,
                    "order_id": order_id,
                    "confidence": signal.confidence,
                    "timeframe_alignment": signal.timeframe_alignment
                })
            
        except Exception as e:
            logger.error(f"Failed to execute sell order for {pair}: {e}")
            if self.notification_manager:
                self.notification_manager.notify_system_error(
                    f"Failed to execute sell order for {pair}: {str(e)}"
                )
    
    def _record_trade(self, action: str, pair: str, price: float, volume: float, order_id: str, signal):
        """Record trade in database and memory"""
        
        trade_id = f"{pair}_{action}_{int(datetime.now().timestamp())}"
        
        # Calculate commission (simplified)
        commission = volume * price * 0.001  # 0.1% commission
        
        trade_record = TradeRecord(
            trade_id=trade_id,
            timestamp=datetime.now(),
            pair=pair,
            action=action,
            volume=volume,
            price=price,
            commission=commission,
            pnl=0.0,  # Will be calculated later
            strategy="multi_timeframe",
            confidence=signal.confidence,
            metadata={
                "order_id": order_id,
                "timeframe_alignment": signal.timeframe_alignment,
                "risk_level": signal.risk_level,
                "dominant_timeframe": signal.dominant_timeframe.value
            }
        )
        
        # Store in database
        self.db_manager.store_trade(trade_record)
        
        # Update daily stats
        self.daily_stats["trades"] += 1
        
        logger.info(f"Trade recorded: {trade_id}")
    
    def _record_simulated_trade(self, action: str, pair: str, price: float, volume: float, signal):
        """Record simulated trade for dry run mode"""
        
        trade_id = f"SIM_{pair}_{action}_{int(datetime.now().timestamp())}"
        
        trade_record = TradeRecord(
            trade_id=trade_id,
            timestamp=datetime.now(),
            pair=pair,
            action=action,
            volume=volume,
            price=price,
            commission=0.0,
            pnl=0.0,
            strategy="multi_timeframe_simulation",
            confidence=signal.confidence,
            metadata={
                "simulation": True,
                "timeframe_alignment": signal.timeframe_alignment,
                "risk_level": signal.risk_level
            }
        )
        
        # Store in database
        self.db_manager.store_trade(trade_record)
        
        logger.info(f"Simulated trade recorded: {trade_id}")
    
    def _get_current_price(self, pair: str) -> float:
        """Get current price for a trading pair"""
        try:
            ticker = self.client.get_ticker(pair)
            return float(ticker.get("last_trade", 0))
        except Exception as e:
            logger.error(f"Error getting price for {pair}: {e}")
            return 0.0
    
    def _get_portfolio_value(self) -> float:
        """Get total portfolio value"""
        try:
            # This would calculate actual portfolio value
            # For now, return a placeholder
            return 10000.0  # $10,000 default
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {e}")
            return 0.0
    
    def _update_performance_metrics(self, portfolio_metrics):
        """Update performance metrics"""
        
        try:
            current_value = portfolio_metrics.total_value
            daily_pnl = current_value - self.daily_stats["start_value"]
            
            performance_record = PerformanceRecord(
                timestamp=datetime.now(),
                portfolio_value=current_value,
                total_pnl=portfolio_metrics.total_pnl,
                daily_pnl=daily_pnl,
                drawdown=portfolio_metrics.max_drawdown,
                sharpe_ratio=portfolio_metrics.portfolio_sharpe,
                win_rate=portfolio_metrics.win_rate,
                total_trades=self.daily_stats["trades"],
                metadata={
                    "diversification_ratio": portfolio_metrics.diversification_ratio,
                    "portfolio_volatility": portfolio_metrics.portfolio_volatility
                }
            )
            
            # Store in database
            self.db_manager.store_performance(performance_record)
            
            # Update daily stats
            self.daily_stats["pnl"] = daily_pnl
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    def _check_daily_summary(self):
        """Check if daily summary should be sent"""
        
        now = datetime.now()
        if (self.last_portfolio_update is None or 
            now.date() > self.last_portfolio_update.date()):
            
            self._send_daily_summary()
            self.last_portfolio_update = now
    
    def _send_daily_summary(self):
        """Send daily performance summary"""
        
        if not self.notification_manager:
            return
        
        try:
            # Get portfolio summary
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            
            # Calculate daily performance
            daily_return = (self.daily_stats["pnl"] / self.daily_stats["start_value"]) * 100 if self.daily_stats["start_value"] > 0 else 0
            
            summary_message = f"""
Daily Trading Summary:
• Trades: {self.daily_stats['trades']}
• Daily P&L: ${self.daily_stats['pnl']:.2f} ({daily_return:.2f}%)
• Portfolio Value: ${portfolio_summary['metrics']['total_value']:.2f}
• Sharpe Ratio: {portfolio_summary['metrics']['sharpe_ratio']:.2f}
• Max Drawdown: {portfolio_summary['metrics']['max_drawdown']:.2f}%
            """
            
            self.notification_manager.send_notification(Notification(
                type=NotificationType.DAILY_SUMMARY,
                priority=NotificationPriority.LOW,
                title="Daily Trading Summary",
                message=summary_message.strip(),
                data=portfolio_summary
            ))
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
    
    def _start_background_threads(self):
        """Start background processing threads"""
        # For now, keep it simple without additional threads
        # In production, you might want separate threads for:
        # - Market data collection
        # - Portfolio rebalancing
        # - Performance monitoring
        pass
    
    def _stop_background_threads(self):
        """Stop background processing threads"""
        # Stop any background threads here
        pass
    
    def _save_final_report(self):
        """Save final performance report"""
        
        try:
            # Get final portfolio state
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            
            # Get trade statistics
            trade_stats = self.db_manager.calculate_trade_statistics()
            
            final_report = {
                "session_summary": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "total_trades": self.daily_stats["trades"],
                    "final_pnl": self.daily_stats["pnl"]
                },
                "portfolio_summary": portfolio_summary,
                "trade_statistics": trade_stats
            }
            
            # Save to file
            report_file = f"reports/final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Path("reports").mkdir(exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(final_report, f, indent=2)
            
            logger.info(f"Final report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"Error saving final report: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
