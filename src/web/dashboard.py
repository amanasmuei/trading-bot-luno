"""
Web Dashboard for Trading Bot Monitoring
"""

import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from threading import Thread
import logging

from src.config.settings import TradingConfig, SUPPORTED_PAIRS
from src.api.luno_client import LunoAPIClient

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates")


class TradingDashboard:
    """Web dashboard for monitoring trading bot"""

    def __init__(self, config: TradingConfig):
        self.config = config
        self.client = LunoAPIClient(config.api_key, config.api_secret)
        self.app = app

        # Create/update dashboard template files
        create_dashboard_files()

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route("/")
        def dashboard():
            # Return the dashboard HTML directly instead of using template file
            return DASHBOARD_HTML

        @self.app.route("/api/market_data")
        def get_market_data():
            """Get current market data"""
            try:
                ticker = self.client.get_ticker(self.config.trading_pair)
                return jsonify(
                    {
                        "success": True,
                        "data": {
                            "price": float(ticker["last_trade"]),
                            "bid": float(ticker["bid"]),
                            "ask": float(ticker["ask"]),
                            "volume": float(ticker.get("rolling_24_hour_volume", 0)),
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                )
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/api/chart_data")
        def get_chart_data():
            """Get basic chart data for TradingView integration"""
            try:
                # Get current market data
                ticker = self.client.get_ticker(self.config.trading_pair)

                # Get some recent candles for indicator calculation
                candles_data = self.client.get_candles(
                    self.config.trading_pair,
                    3600,
                    int((datetime.now() - timedelta(hours=24)).timestamp() * 1000),
                )
                candles = candles_data.get("candles", [])

                indicators = {}
                if candles:
                    close_prices = [float(c["close"]) for c in candles]

                    # Import technical analysis module
                    from src.bot.technical_analysis import TechnicalAnalyzer

                    analyzer = TechnicalAnalyzer(self.config)

                    # Calculate basic indicators
                    if len(close_prices) >= self.config.rsi_period:
                        rsi_values = analyzer.calculate_rsi(
                            close_prices, self.config.rsi_period
                        )
                        if rsi_values:
                            indicators["current_rsi"] = rsi_values[-1]

                    if len(close_prices) >= max(
                        self.config.ema_short, self.config.ema_long
                    ):
                        ema_short = analyzer.calculate_ema(
                            close_prices, self.config.ema_short
                        )
                        ema_long = analyzer.calculate_ema(
                            close_prices, self.config.ema_long
                        )
                        if ema_short:
                            indicators["current_ema_short"] = ema_short[-1]
                        if ema_long:
                            indicators["current_ema_long"] = ema_long[-1]

                return jsonify(
                    {
                        "success": True,
                        "data": {
                            "price": float(ticker["last_trade"]),
                            "bid": float(ticker["bid"]),
                            "ask": float(ticker["ask"]),
                            "volume": float(ticker.get("rolling_24_hour_volume", 0)),
                            "indicators": indicators,
                            "config": {
                                "rsi_period": self.config.rsi_period,
                                "ema_short": self.config.ema_short,
                                "ema_long": self.config.ema_long,
                            },
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                )
            except Exception as e:
                logger.error(f"Error in get_chart_data: {e}")
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/api/price_chart")
        def get_price_chart():
            """Get candlestick chart data with technical analysis indicators"""
            try:
                # Get timeframe and interval from query parameters
                timeframe = request.args.get("timeframe", "1d")  # Default 1 day
                interval = request.args.get("interval", "5m")  # Default 5 minutes

                # Map intervals to Luno candle durations (in seconds)
                interval_map = {
                    "1m": 60,
                    "5m": 300,
                    "15m": 900,
                    "30m": 1800,
                    "1h": 3600,
                    "4h": 14400,
                    "1d": 86400,
                }

                # Map timeframes to days
                timeframe_map = {
                    "1h": 1 / 24,
                    "4h": 4 / 24,
                    "12h": 0.5,
                    "1d": 1,
                    "3d": 3,
                    "1w": 7,
                    "2w": 14,
                    "1m": 30,
                    "3m": 90,
                }

                # Get the duration in seconds and days
                candle_duration = interval_map.get(interval, 300)  # Default 5min
                days = timeframe_map.get(timeframe, 1)  # Default 1 day

                # Calculate since timestamp
                since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

                logger.info(
                    f"Requesting candles: pair={self.config.trading_pair}, interval={interval}({candle_duration}s), timeframe={timeframe}({days} days)"
                )

                # Try to get candles data with progressive fallback
                candles = []
                fallback_attempts = [
                    {
                        "days": days,
                        "duration": candle_duration,
                        "name": f"{timeframe} with {interval}",
                    },
                    {"days": 1, "duration": 3600, "name": "1 day with 1h"},
                    {"days": 0.5, "duration": 1800, "name": "12h with 30min"},
                    {"days": 0.25, "duration": 900, "name": "6h with 15min"},
                ]

                for attempt in fallback_attempts:
                    try:
                        since_attempt = int(
                            (
                                datetime.now() - timedelta(days=attempt["days"])
                            ).timestamp()
                            * 1000
                        )
                        logger.info(f"Trying: {attempt['name']}")

                        candles_data = self.client.get_candles(
                            self.config.trading_pair, attempt["duration"], since_attempt
                        )
                        candles = candles_data.get("candles", [])

                        if candles:
                            logger.info(
                                f"Success: Got {len(candles)} candles with {attempt['name']}"
                            )
                            break
                        else:
                            logger.warning(f"No candles returned for {attempt['name']}")

                    except Exception as e:
                        logger.warning(f"Failed {attempt['name']}: {e}")
                        continue

                if not candles:
                    logger.error("All fallback attempts failed")
                    return jsonify(
                        {"success": False, "error": "No candle data available"}
                    )

                # Calculate technical indicators
                close_prices = [float(c["close"]) for c in candles]
                high_prices = [float(c["high"]) for c in candles]
                low_prices = [float(c["low"]) for c in candles]
                volumes = [float(c["volume"]) for c in candles]

                # Import technical analysis module
                from src.bot.technical_analysis import TechnicalAnalyzer

                analyzer = TechnicalAnalyzer(self.config)

                # Calculate indicators using the bot's configuration
                indicators = {}
                timestamps = [
                    datetime.fromtimestamp(c["timestamp"] / 1000).isoformat()
                    for c in candles
                ]

                # RSI
                if len(close_prices) >= self.config.rsi_period:
                    rsi_values = analyzer.calculate_rsi(
                        close_prices, self.config.rsi_period
                    )
                    indicators["rsi"] = rsi_values

                # EMAs
                if len(close_prices) >= max(
                    self.config.ema_short, self.config.ema_long
                ):
                    ema_short = analyzer.calculate_ema(
                        close_prices, self.config.ema_short
                    )
                    ema_long = analyzer.calculate_ema(
                        close_prices, self.config.ema_long
                    )
                    indicators["ema_short"] = ema_short
                    indicators["ema_long"] = ema_long

                # MACD
                if len(close_prices) >= 26:  # MACD needs at least 26 periods
                    macd_line, signal_line, histogram = analyzer.calculate_macd(
                        close_prices
                    )
                    indicators["macd_line"] = macd_line
                    indicators["macd_signal"] = signal_line
                    indicators["macd_histogram"] = histogram

                # Bollinger Bands
                if len(close_prices) >= self.config.bollinger_period:
                    bb_upper, bb_middle, bb_lower = analyzer.calculate_bollinger_bands(
                        close_prices,
                        self.config.bollinger_period,
                        self.config.bollinger_std,
                    )
                    indicators["bb_upper"] = bb_upper
                    indicators["bb_middle"] = bb_middle
                    indicators["bb_lower"] = bb_lower

                # Create candlestick chart data with technical indicators
                chart_data = {
                    "timestamps": timestamps,
                    "open": [float(c["open"]) for c in candles],
                    "high": high_prices,
                    "low": low_prices,
                    "close": close_prices,
                    "volume": volumes,
                    "timeframe": timeframe,
                    "interval": interval,
                    "indicators": indicators,
                    "config": {
                        "rsi_period": self.config.rsi_period,
                        "rsi_oversold": self.config.rsi_oversold,
                        "rsi_overbought": self.config.rsi_overbought,
                        "ema_short": self.config.ema_short,
                        "ema_long": self.config.ema_long,
                        "bollinger_period": self.config.bollinger_period,
                        "bollinger_std": self.config.bollinger_std,
                    },
                }

                return jsonify({"success": True, "data": chart_data})

            except Exception as e:
                logger.error(f"Error in get_price_chart: {e}")
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/api/portfolio")
        def get_portfolio():
            """Get portfolio information"""
            try:
                if self.config.dry_run:
                    return jsonify(
                        {
                            "success": True,
                            "data": {
                                "dry_run": True,
                                "message": "Bot running in simulation mode",
                            },
                        }
                    )

                balance_data = self.client.get_balances()
                balances = {}

                for balance in balance_data.get("balance", []):
                    currency = balance["asset"]
                    balances[currency] = {
                        "available": float(balance["balance"]),
                        "reserved": float(balance["reserved"]),
                        "total": float(balance["balance"]) + float(balance["reserved"]),
                    }

                return jsonify({"success": True, "data": balances})

            except Exception as e:
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/api/trades")
        def get_trades():
            """Get recent trades"""
            try:
                # Read from trades history file if exists
                trades = []
                if os.path.exists("trading_bot.log"):
                    # Parse recent trades from log (simplified)
                    trades = self._parse_trades_from_log()

                return jsonify({"success": True, "data": trades})

            except Exception as e:
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/health")
        def health_check():
            """Health check endpoint for Docker"""
            return jsonify(
                {"status": "healthy", "timestamp": datetime.now().isoformat()}
            )

        @self.app.route("/api/bot_status")
        def get_bot_status():
            """Get bot status"""
            try:
                # Check if bot log file exists and is recent
                bot_running = False
                last_activity = None

                if os.path.exists("trading_bot.log"):
                    stat = os.stat("trading_bot.log")
                    last_activity = datetime.fromtimestamp(stat.st_mtime)

                    # Consider bot running if log was updated in last 5 minutes
                    if datetime.now() - last_activity < timedelta(minutes=5):
                        bot_running = True

                return jsonify(
                    {
                        "success": True,
                        "data": {
                            "running": bot_running,
                            "last_activity": (
                                last_activity.isoformat() if last_activity else None
                            ),
                            "config": {
                                "trading_pair": self.config.trading_pair,
                                "dry_run": self.config.dry_run,
                                "max_position_size": self.config.max_position_size_percent,
                            },
                        },
                    }
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)})

        @self.app.route("/api/toggle_mode", methods=["POST"])
        def toggle_trading_mode():
            """Toggle between dry run and live trading mode"""
            try:
                data = request.get_json()
                new_dry_run = data.get("dry_run", True)

                # Update the config
                self.config.dry_run = new_dry_run

                # Update environment variable for current session
                os.environ["DRY_RUN"] = str(new_dry_run).lower()

                # Try to write to .env file to persist the change (if writable)
                env_file_path = ".env"
                env_updated = False
                try:
                    if os.path.exists(env_file_path):
                        # Read existing .env file
                        with open(env_file_path, "r") as f:
                            lines = f.readlines()

                        # Update or add DRY_RUN setting
                        dry_run_found = False
                        for i, line in enumerate(lines):
                            if line.strip().startswith("DRY_RUN="):
                                lines[i] = f"DRY_RUN={str(new_dry_run).lower()}\n"
                                dry_run_found = True
                                break

                        # If DRY_RUN not found, add it
                        if not dry_run_found:
                            lines.append(f"DRY_RUN={str(new_dry_run).lower()}\n")

                        # Write back to .env file
                        with open(env_file_path, "w") as f:
                            f.writelines(lines)
                        env_updated = True

                except (OSError, IOError) as e:
                    # File system is read-only or other write error
                    logger.warning(f"Could not persist to .env file: {e}")
                    env_updated = False

                mode_text = "simulation" if new_dry_run else "live trading"
                logger.info(f"Trading mode changed to: {mode_text}")

                # Prepare response message
                if env_updated:
                    message = f"Mode changed to {mode_text}"
                else:
                    message = f"Mode changed to {mode_text} (session only - restart will reset)"

                return jsonify(
                    {
                        "success": True,
                        "message": message,
                        "dry_run": new_dry_run,
                        "persisted": env_updated,
                    }
                )

            except Exception as e:
                logger.error(f"Error toggling trading mode: {e}")
                return jsonify({"success": False, "error": str(e)})

    def _parse_trades_from_log(self):
        """Parse recent trades from log file"""
        trades = []
        try:
            with open("trading_bot.log", "r") as f:
                lines = f.readlines()

            # Look for trade-related log entries
            for line in reversed(lines[-100:]):  # Last 100 lines
                if "Trade recorded:" in line or "[SIMULATED] Trade recorded:" in line:
                    # Parse trade information (simplified)
                    parts = line.split(" - ")
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        message = parts[-1].strip()

                        # Extract trade details
                        if "BUY" in message or "SELL" in message:
                            trades.append(
                                {
                                    "timestamp": timestamp,
                                    "message": message,
                                    "simulated": "[SIMULATED]" in message,
                                }
                            )

                if len(trades) >= 10:  # Limit to 10 recent trades
                    break

        except Exception as e:
            logger.error(f"Error parsing trades from log: {e}")

        return trades

    def run(self, host="0.0.0.0", port=5001, debug=False):
        """Run the dashboard"""
        logger.info(f"Starting dashboard on http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


# Create dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XBTMYR Trading Bot Dashboard</title>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
        @media (min-width: 1200px) {
            .dashboard-grid {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            min-height: 200px;
            display: flex;
            flex-direction: column;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }
        .card h3 {
            margin-top: 0;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 12px;
            font-size: 1.2em;
            font-weight: 600;
        }
        .card-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .status-indicator {
            display: inline-block;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.6; }
            100% { opacity: 1; }
        }
        .status-running { background-color: #4CAF50; }
        .status-stopped { background-color: #f44336; }
        .price-display {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            text-align: center;
            margin: 20px 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 12px 0;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
            font-size: 0.95em;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-label {
            font-weight: 500;
            color: #666;
        }
        .metric-value {
            font-weight: 600;
            color: #333;
        }
        .trades-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .trade-item {
            padding: 8px;
            margin: 5px 0;
            border-radius: 5px;
            background-color: #f8f9fa;
            font-size: 0.9em;
        }
        .simulated {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
        }
        .chart-container {
            grid-column: 1 / -1;
            height: calc(100vh - 400px);
            min-height: 600px;
            max-height: 900px;
        }

        #tradingview-chart {
            width: 100%;
            height: 500px;
            min-height: 500px;
        }
        .chart-controls {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .control-group label {
            font-size: 0.9em;
            font-weight: 500;
            color: #555;
        }
        .control-group select {
            padding: 8px 12px;
            border: 2px solid #e1e5e9;
            border-radius: 6px;
            font-size: 0.9em;
            background: white;
            cursor: pointer;
            transition: border-color 0.2s ease;
        }
        .control-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            transition: background 0.2s ease;
            height: fit-content;
            margin-top: 20px;
        }
        .refresh-btn:hover {
            background: #5a67d8;
        }
        .chart-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .chart-title h3 {
            margin: 0;
        }
        
        /* Toggle Switch Styles */
        .mode-toggle-container {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #f0f0f0;
        }
        
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
            margin-bottom: 10px;
        }
        
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ffc107;
            transition: .4s;
            border-radius: 34px;
        }
        
        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .toggle-slider {
            background-color: #4CAF50;
        }
        
        input:checked + .toggle-slider:before {
            transform: translateX(26px);
        }
        
        .toggle-labels {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85em;
            margin-top: 5px;
        }
        
        .toggle-label-left,
        .toggle-label-right {
            font-weight: 500;
        }
        
        .toggle-label-left {
            color: #ffc107;
        }
        
        .toggle-label-right {
            color: #4CAF50;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 XBTMYR Trading Bot Dashboard</h1>
        <p>Real-time monitoring and performance tracking</p>
    </div>

    <div class="dashboard-grid">
        <!-- Bot Status -->
        <div class="card">
            <h3>Bot Status</h3>
            <div id="bot-status">
                <span class="status-indicator status-stopped"></span>
                <span>Loading...</span>
            </div>
            <div id="bot-config"></div>
            <div class="mode-toggle-container">
                <label class="toggle-switch">
                    <input type="checkbox" id="mode-toggle" onchange="toggleTradingMode()">
                    <span class="toggle-slider"></span>
                </label>
                <div class="toggle-labels">
                    <span class="toggle-label-left">🎭 Simulation</span>
                    <span class="toggle-label-right">💰 Live</span>
                </div>
            </div>
        </div>

        <!-- Current Price -->
        <div class="card">
            <h3>Current Market</h3>
            <div class="price-display" id="current-price">Loading...</div>
            <div id="market-metrics"></div>
        </div>

        <!-- Portfolio -->
        <div class="card">
            <h3>Portfolio</h3>
            <div id="portfolio-data">Loading...</div>
        </div>

        <!-- Recent Trades -->
        <div class="card">
            <h3>Recent Trades</h3>
            <div class="trades-list" id="recent-trades">Loading...</div>
        </div>

        <!-- TradingView Chart -->
        <div class="card chart-container">
            <div class="chart-title">
                <h3>TradingView Chart</h3>
                <button class="refresh-btn" onclick="refreshTradingViewChart()">Refresh</button>
            </div>
            <div class="chart-controls">
                <div class="control-group">
                    <label for="chart-type-select">Chart Type:</label>
                    <select id="chart-type-select" onchange="updateTradingViewChart()">
                        <option value="1">Candlestick</option>
                        <option value="0">Bars</option>
                        <option value="3">Line</option>
                        <option value="9">Area</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="interval-select">Interval:</label>
                    <select id="interval-select" onchange="updateTradingViewChart()">
                        <option value="1">1 Minute</option>
                        <option value="5" selected>5 Minutes</option>
                        <option value="15">15 Minutes</option>
                        <option value="30">30 Minutes</option>
                        <option value="60">1 Hour</option>
                        <option value="240">4 Hours</option>
                        <option value="1D">1 Day</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="theme-select">Theme:</label>
                    <select id="theme-select" onchange="updateTradingViewChart()">
                        <option value="light" selected>Light</option>
                        <option value="dark">Dark</option>
                    </select>
                </div>
            </div>
            <div id="tradingview-chart"></div>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setInterval(updateDashboard, 30000);

        // TradingView widget instance
        let tradingViewWidget = null;

        // Initial load
        updateDashboard();
        initializeTradingViewChart();

        function updateDashboard() {
            updateBotStatus();
            updateMarketData();
            updatePortfolio();
            updateTrades();
        }

        function updateBotStatus() {
            fetch('/api/bot_status')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const statusEl = document.getElementById('bot-status');
                        const configEl = document.getElementById('bot-config');
                        const toggleEl = document.getElementById('mode-toggle');
                        
                        const status = data.data.running ? 'Running' : 'Stopped';
                        const statusClass = data.data.running ? 'status-running' : 'status-stopped';
                        
                        statusEl.innerHTML = `
                            <span class="status-indicator ${statusClass}"></span>
                            <span>${status}</span>
                        `;
                        
                        configEl.innerHTML = `
                            <div class="metric">
                                <span class="metric-label">Trading Pair:</span>
                                <span class="metric-value">${data.data.config.trading_pair}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Mode:</span>
                                <span class="metric-value">${data.data.config.dry_run ? '🎭 Simulation' : '💰 Live'}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Position Size:</span>
                                <span class="metric-value">${data.data.config.max_position_size}%</span>
                            </div>
                        `;
                        
                        // Update toggle switch state (checked = live trading, unchecked = simulation)
                        toggleEl.checked = !data.data.config.dry_run;
                    }
                })
                .catch(error => console.error('Error updating bot status:', error));
        }

        function updateMarketData() {
            fetch('/api/market_data')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const priceEl = document.getElementById('current-price');
                        const metricsEl = document.getElementById('market-metrics');
                        
                        priceEl.textContent = `${data.data.price.toLocaleString()} MYR`;
                        
                        metricsEl.innerHTML = `
                            <div class="metric">
                                <span class="metric-label">💰 Bid:</span>
                                <span class="metric-value">${data.data.bid.toLocaleString()} MYR</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">💸 Ask:</span>
                                <span class="metric-value">${data.data.ask.toLocaleString()} MYR</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">📊 24h Volume:</span>
                                <span class="metric-value">${data.data.volume.toFixed(2)} BTC</span>
                            </div>
                        `;
                    }
                })
                .catch(error => console.error('Error updating market data:', error));
        }

        function updatePortfolio() {
            fetch('/api/portfolio')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const portfolioEl = document.getElementById('portfolio-data');
                        
                        if (data.data.dry_run) {
                            portfolioEl.innerHTML = `
                                <div style="text-align: center; color: #ffc107;">
                                    <p>🎭 ${data.data.message}</p>
                                </div>
                            `;
                        } else {
                            let html = '';
                            for (const [currency, balance] of Object.entries(data.data)) {
                                html += `
                                    <div class="metric">
                                        <span>${currency}:</span>
                                        <span>${balance.total.toFixed(6)}</span>
                                    </div>
                                `;
                            }
                            portfolioEl.innerHTML = html;
                        }
                    }
                })
                .catch(error => console.error('Error updating portfolio:', error));
        }

        function updateTrades() {
            fetch('/api/trades')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const tradesEl = document.getElementById('recent-trades');
                        
                        if (data.data.length === 0) {
                            tradesEl.innerHTML = '<p>No recent trades</p>';
                        } else {
                            let html = '';
                            data.data.forEach(trade => {
                                const className = trade.simulated ? 'trade-item simulated' : 'trade-item';
                                html += `
                                    <div class="${className}">
                                        <div>${trade.timestamp}</div>
                                        <div>${trade.message}</div>
                                    </div>
                                `;
                            });
                            tradesEl.innerHTML = html;
                        }
                    }
                })
                .catch(error => console.error('Error updating trades:', error));
        }

        function initializeTradingViewChart() {
            // Initialize TradingView widget
            const chartType = parseInt(document.getElementById('chart-type-select').value);
            const interval = document.getElementById('interval-select').value;
            const theme = document.getElementById('theme-select').value;

            tradingViewWidget = new TradingView.widget({
                "width": "100%",
                "height": 500,
                "symbol": "BITSTAMP:BTCUSD", // Using Bitcoin as proxy since XBTMYR might not be available
                "interval": interval,
                "timezone": "Etc/UTC",
                "theme": theme,
                "style": chartType.toString(),
                "locale": "en",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "hide_top_toolbar": false,
                "hide_legend": false,
                "save_image": false,
                "container_id": "tradingview-chart",
                "studies": [
                    "RSI@tv-basicstudies",
                    "MACD@tv-basicstudies",
                    "BB@tv-basicstudies",
                    "EMA@tv-basicstudies"
                ],
                "overrides": {
                    "paneProperties.background": "#ffffff",
                    "paneProperties.vertGridProperties.color": "#e1e3e6",
                    "paneProperties.horzGridProperties.color": "#e1e3e6",
                    "symbolWatermarkProperties.transparency": 90,
                    "scalesProperties.textColor": "#333333"
                }
            });
        }

        function updateTradingViewChart() {
            // Remove existing widget
            if (tradingViewWidget) {
                document.getElementById('tradingview-chart').innerHTML = '';
            }

            // Reinitialize with new settings
            initializeTradingViewChart();
        }

        function refreshTradingViewChart() {
            // Refresh the chart data
            updateTradingViewChart();

            // Fetch indicator data to display alongside TradingView chart
            fetch('/api/chart_data')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // TradingView chart is already initialized and will show technical indicators
                        console.log('Chart data received successfully');

                        // Display current indicator values if available
                        if (data.data.indicators) {
                            displayIndicatorValues(data.data.indicators, data.data.config);
                        }

                    } else {
                        // Handle error case
                        console.error('Error fetching chart data:', data.error);
                        displayChartError(data.error);
                    }
                })
                .catch(error => {
                    console.error('Error updating chart:', error);
                    displayChartError('Failed to fetch chart data');
                });
        }

        function displayChartError(errorMessage) {
            document.getElementById('tradingview-chart').innerHTML = `
                <div style="text-align: center; padding: 50px; color: #666;">
                    <h4>Unable to load chart</h4>
                    <p>${errorMessage}</p>
                    <button onclick="refreshTradingViewChart()" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        Retry
                    </button>
                </div>
            `;
        }

        function displayIndicatorValues(indicators, config) {
            const currentValues = [];

            // Handle both array format (from old API) and direct value format (from new API)
            if (indicators.current_rsi !== undefined) {
                currentValues.push(`RSI: ${indicators.current_rsi?.toFixed(1) || 'N/A'}`);
            } else if (indicators.rsi && indicators.rsi.length > 0) {
                const currentRSI = indicators.rsi[indicators.rsi.length - 1];
                currentValues.push(`RSI: ${currentRSI?.toFixed(1) || 'N/A'}`);
            }

            if (indicators.current_ema_short !== undefined) {
                currentValues.push(`EMA${config.ema_short}: ${indicators.current_ema_short?.toFixed(2) || 'N/A'}`);
            } else if (indicators.ema_short && indicators.ema_short.length > 0) {
                const currentEMAShort = indicators.ema_short[indicators.ema_short.length - 1];
                currentValues.push(`EMA${config.ema_short}: ${currentEMAShort?.toFixed(2) || 'N/A'}`);
            }

            if (indicators.current_ema_long !== undefined) {
                currentValues.push(`EMA${config.ema_long}: ${indicators.current_ema_long?.toFixed(2) || 'N/A'}`);
            } else if (indicators.ema_long && indicators.ema_long.length > 0) {
                const currentEMALong = indicators.ema_long[indicators.ema_long.length - 1];
                currentValues.push(`EMA${config.ema_long}: ${currentEMALong?.toFixed(2) || 'N/A'}`);
            }

            if (indicators.macd_line && indicators.macd_line.length > 0) {
                const currentMACD = indicators.macd_line[indicators.macd_line.length - 1];
                currentValues.push(`MACD: ${currentMACD?.toFixed(4) || 'N/A'}`);
            }

            // Display current values
            if (currentValues.length > 0) {
                // Remove existing indicator display
                const existingDisplay = document.querySelector('.indicator-values');
                if (existingDisplay) {
                    existingDisplay.remove();
                }

                const valuesHtml = `
                    <div class="indicator-values" style="background: rgba(255,255,255,0.95); padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 0.9em;">
                        <strong>Current Indicators:</strong> ${currentValues.join(' | ')}
                    </div>
                `;
                document.getElementById('tradingview-chart').insertAdjacentHTML('afterend', valuesHtml);
            }
        }

        function toggleTradingMode() {
            const toggleEl = document.getElementById('mode-toggle');
            const newDryRun = !toggleEl.checked; // If checked = live, so dry_run = false
            
            // Send request to toggle mode
            fetch('/api/toggle_mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    dry_run: newDryRun
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const message = `✅ ${data.message}`;
                    
                    // Create a temporary notification
                    const notification = document.createElement('div');
                    notification.innerHTML = message;
                    notification.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #4CAF50;
                        color: white;
                        padding: 15px 20px;
                        border-radius: 5px;
                        z-index: 1000;
                        font-weight: 500;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    `;
                    
                    document.body.appendChild(notification);
                    
                    // Remove notification after 3 seconds
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.parentNode.removeChild(notification);
                        }
                    }, 3000);
                    
                    // Refresh the dashboard to show updated status
                    setTimeout(() => {
                        updateDashboard();
                    }, 500);
                    
                } else {
                    // Show error message
                    alert(`❌ Error: ${data.error}`);
                    
                    // Revert toggle state
                    toggleEl.checked = !newDryRun;
                }
            })
            .catch(error => {
                console.error('Error toggling mode:', error);
                alert('❌ Network error while changing mode');
                
                // Revert toggle state
                toggleEl.checked = !newDryRun;
            });
        }
    </script>
</body>
</html>
"""


def create_dashboard_files():
    """Create dashboard template files"""

    # Create templates directory (support both paths for compatibility)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("trading-bot/templates", exist_ok=True)

    # Write dashboard template to both locations for compatibility
    with open("templates/dashboard.html", "w") as f:
        f.write(DASHBOARD_HTML)
    with open("trading-bot/templates/dashboard.html", "w") as f:
        f.write(DASHBOARD_HTML)


if __name__ == "__main__":
    create_dashboard_files()

    config = TradingConfig()
    dashboard = TradingDashboard(config)
    dashboard.run(debug=True)
