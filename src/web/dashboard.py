"""
Web Dashboard for Trading Bot Monitoring
"""

import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import plotly.graph_objs as go
import plotly.utils
from threading import Thread
import logging

from src.config.settings import TradingConfig
from src.api.luno_client import LunoAPIClient

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates")


class TradingDashboard:
    """Web dashboard for monitoring trading bot"""

    def __init__(self, config: TradingConfig):
        self.config = config
        self.client = LunoAPIClient(config.api_key, config.api_secret)
        self.app = app

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route("/")
        def dashboard():
            return render_template("dashboard.html")

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

        @self.app.route("/api/price_chart")
        def get_price_chart():
            """Get price chart data"""
            try:
                # Get timeframe and duration from query parameters
                timeframe = request.args.get("timeframe", "7d")  # Default 7 days
                candle_duration = int(
                    request.args.get("duration", "3600")
                )  # Default 1h candles

                # Map timeframes to days and appropriate candle durations
                timeframe_map = {
                    "1h": {"days": 1 / 24, "duration": 300},  # 1 hour, 5min candles
                    "4h": {"days": 4 / 24, "duration": 300},  # 4 hours, 5min candles
                    "1d": {"days": 1, "duration": 900},  # 1 day, 15min candles
                    "3d": {"days": 3, "duration": 3600},  # 3 days, 1h candles
                    "7d": {"days": 7, "duration": 3600},  # 7 days, 1h candles
                    "30d": {"days": 30, "duration": 14400},  # 30 days, 4h candles
                    "90d": {"days": 90, "duration": 86400},  # 90 days, 1d candles
                }

                if timeframe in timeframe_map:
                    days = timeframe_map[timeframe]["days"]
                    candle_duration = timeframe_map[timeframe]["duration"]
                else:
                    days = 7
                    candle_duration = 3600

                since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

                # DEBUG: Log the calculated timestamp and request details
                logger.info(f"DEBUG: Requesting candles for {self.config.trading_pair}")
                logger.info(f"DEBUG: Since timestamp: {since}")
                logger.info(f"DEBUG: Since date: {datetime.fromtimestamp(since/1000)}")
                logger.info(f"DEBUG: Current time: {datetime.now()}")

                # Try to get candles data with fallback strategy
                candles_data = None
                candles = []

                # First attempt with selected timeframe
                try:
                    candles_data = self.client.get_candles(
                        self.config.trading_pair, candle_duration, since
                    )
                    candles = candles_data.get("candles", [])
                    logger.info(
                        f"DEBUG: Successfully got {len(candles)} candles from 7 days ago"
                    )
                except Exception as e:
                    logger.warning(f"DEBUG: 7-day request failed: {e}")

                    # Fallback 1: Try 1 day ago
                    try:
                        since_1day = int(
                            (datetime.now() - timedelta(days=1)).timestamp() * 1000
                        )
                        logger.info(
                            f"DEBUG: Trying fallback with 1 day ago: {since_1day}"
                        )
                        candles_data = self.client.get_candles(
                            self.config.trading_pair, candle_duration, since_1day
                        )
                        candles = candles_data.get("candles", [])
                        logger.info(f"DEBUG: Fallback 1-day got {len(candles)} candles")
                    except Exception as e2:
                        logger.warning(f"DEBUG: 1-day fallback failed: {e2}")

                        # Fallback 2: Try 12 hours ago
                        try:
                            since_12h = int(
                                (datetime.now() - timedelta(hours=12)).timestamp()
                                * 1000
                            )
                            logger.info(
                                f"DEBUG: Trying fallback with 12 hours ago: {since_12h}"
                            )
                            candles_data = self.client.get_candles(
                                self.config.trading_pair, candle_duration, since_12h
                            )
                            candles = candles_data.get("candles", [])
                            logger.info(
                                f"DEBUG: Fallback 12-hour got {len(candles)} candles"
                            )
                        except Exception as e3:
                            logger.error(f"DEBUG: All fallback attempts failed: {e3}")
                            candles = []

                # Create chart data
                chart_data = {
                    "timestamps": [
                        datetime.fromtimestamp(c["timestamp"] / 1000).isoformat()
                        for c in candles
                    ],
                    "prices": [float(c["close"]) for c in candles],
                    "volumes": [float(c["volume"]) for c in candles],
                    "highs": [float(c["high"]) for c in candles],
                    "lows": [float(c["low"]) for c in candles],
                    "opens": [float(c["open"]) for c in candles],
                }

                return jsonify({"success": True, "data": chart_data})

            except Exception as e:
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

    def run(self, host="127.0.0.1", port=5000, debug=False):
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
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
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
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card h3 {
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-running { background-color: #4CAF50; }
        .status-stopped { background-color: #f44336; }
        .price-display {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            text-align: center;
            margin: 20px 0;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
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
            height: 400px;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            float: right;
        }
        .refresh-btn:hover {
            background: #5a67d8;
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

        <!-- Price Chart -->
        <div class="card chart-container">
            <h3>
                Price Chart (7-day)
                <button class="refresh-btn" onclick="updateChart()">Refresh</button>
            </h3>
            <div id="price-chart"></div>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setInterval(updateDashboard, 30000);
        
        // Initial load
        updateDashboard();
        updateChart();

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
                        
                        const status = data.data.running ? 'Running' : 'Stopped';
                        const statusClass = data.data.running ? 'status-running' : 'status-stopped';
                        
                        statusEl.innerHTML = `
                            <span class="status-indicator ${statusClass}"></span>
                            <span>${status}</span>
                        `;
                        
                        configEl.innerHTML = `
                            <div class="metric">
                                <span>Trading Pair:</span>
                                <span>${data.data.config.trading_pair}</span>
                            </div>
                            <div class="metric">
                                <span>Mode:</span>
                                <span>${data.data.config.dry_run ? 'Simulation' : 'Live'}</span>
                            </div>
                            <div class="metric">
                                <span>Position Size:</span>
                                <span>${data.data.config.max_position_size}%</span>
                            </div>
                        `;
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
                                <span>Bid:</span>
                                <span>${data.data.bid.toLocaleString()} MYR</span>
                            </div>
                            <div class="metric">
                                <span>Ask:</span>
                                <span>${data.data.ask.toLocaleString()} MYR</span>
                            </div>
                            <div class="metric">
                                <span>24h Volume:</span>
                                <span>${data.data.volume.toFixed(2)} BTC</span>
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

        function updateChart() {
            fetch('/api/price_chart')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const chartData = [{
                            x: data.data.timestamps,
                            y: data.data.prices,
                            type: 'scatter',
                            mode: 'lines',
                            name: 'Price',
                            line: { color: '#667eea', width: 2 }
                        }];

                        const layout = {
                            title: 'XBTMYR Price Movement',
                            xaxis: { title: 'Time' },
                            yaxis: { title: 'Price (MYR)' },
                            margin: { t: 50, r: 50, b: 50, l: 80 }
                        };

                        Plotly.newPlot('price-chart', chartData, layout, {responsive: true});
                    }
                })
                .catch(error => console.error('Error updating chart:', error));
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
