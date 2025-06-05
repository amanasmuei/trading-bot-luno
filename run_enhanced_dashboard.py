#!/usr/bin/env python3
"""
Simple Enhanced Dashboard Runner
Connects to the running enhanced trading bot and displays a web dashboard
"""

import os
import sys
import json
import requests
from datetime import datetime
from flask import Flask, render_template_string, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enhanced bot endpoints - configurable via environment variables
BOT_HOST = os.getenv("BOT_HOST", "localhost")
BOT_PORT = os.getenv("BOT_PORT", "5002")

# Support Docker container names
if BOT_HOST == "localhost" and os.getenv("DOCKER_ENV"):
    BOT_HOST = "luno-enhanced-bot"  # Docker container name

BOT_HEALTH_URL = f"http://{BOT_HOST}:{BOT_PORT}/health"
BOT_STATUS_URL = f"http://{BOT_HOST}:{BOT_PORT}/status"

# Simple HTML template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Trading Bot Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #667eea;
        }
        .card h3 {
            margin-top: 0;
            color: #333;
        }
        .status-running {
            color: #28a745;
            font-weight: bold;
            font-size: 18px;
        }
        .status-offline {
            color: #dc3545;
            font-weight: bold;
            font-size: 18px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }
        .metric-label {
            font-weight: bold;
            color: #666;
        }
        .metric-value {
            color: #333;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 0;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .reports-section {
            margin-top: 30px;
        }
        .report-item {
            background: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            border-left: 3px solid #667eea;
        }
        .timestamp {
            color: #666;
            font-size: 14px;
        }
        .error {
            color: #dc3545;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced Trading Bot Dashboard</h1>
            <p>Real-time monitoring for your cryptocurrency trading bot</p>
            <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh</button>
        </div>

        <div class="status-grid">
            <div class="card">
                <h3>🤖 Bot Status</h3>
                <div id="bot-status">Loading...</div>
            </div>

            <div class="card">
                <h3>📊 Daily Metrics</h3>
                <div id="daily-metrics">Loading...</div>
            </div>

            <div class="card">
                <h3>⚡ System Health</h3>
                <div id="system-health">Loading...</div>
            </div>
        </div>

        <div class="reports-section">
            <h3>📈 Recent Reports</h3>
            <div id="reports-list">Loading...</div>
        </div>
    </div>

    <script>
        function refreshDashboard() {
            loadBotStatus();
            loadReports();
        }

        function loadBotStatus() {
            fetch('/api/bot_status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('bot-status');
                    const metricsDiv = document.getElementById('daily-metrics');
                    const healthDiv = document.getElementById('system-health');

                    if (data.success) {
                        statusDiv.innerHTML = '<div class="status-running">🟢 RUNNING</div>';
                        
                        const botData = data.data.bot_status || {};
                        metricsDiv.innerHTML = `
                            <div class="metric">
                                <span class="metric-label">Daily Trades:</span>
                                <span class="metric-value">${botData.daily_trades || 0}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Daily P&L:</span>
                                <span class="metric-value">${(botData.daily_pnl || 0).toFixed(2)}%</span>
                            </div>
                        `;

                        healthDiv.innerHTML = `
                            <div class="metric">
                                <span class="metric-label">Service:</span>
                                <span class="metric-value">${data.data.service || 'Unknown'}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Version:</span>
                                <span class="metric-value">${data.data.version || 'Unknown'}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Last Update:</span>
                                <span class="metric-value">${new Date(data.data.timestamp).toLocaleTimeString()}</span>
                            </div>
                        `;
                    } else {
                        statusDiv.innerHTML = '<div class="status-offline">🔴 OFFLINE</div>';
                        metricsDiv.innerHTML = '<div class="error">Bot is offline</div>';
                        healthDiv.innerHTML = '<div class="error">Unable to connect to bot</div>';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('bot-status').innerHTML = '<div class="status-offline">🔴 CONNECTION ERROR</div>';
                });
        }

        function loadReports() {
            fetch('/api/reports')
                .then(response => response.json())
                .then(data => {
                    const reportsDiv = document.getElementById('reports-list');
                    
                    if (data.success && data.reports.length > 0) {
                        let html = '';
                        data.reports.slice(0, 5).forEach(report => {
                            const metrics = report.performance_metrics || {};
                            html += `
                                <div class="report-item">
                                    <div class="timestamp">Generated: ${new Date(report.generated_at).toLocaleString()}</div>
                                    <div class="metric">
                                        <span class="metric-label">Total Trades:</span>
                                        <span class="metric-value">${metrics.total_trades || 0}</span>
                                    </div>
                                    <div class="metric">
                                        <span class="metric-label">Win Rate:</span>
                                        <span class="metric-value">${((metrics.win_rate || 0) * 100).toFixed(1)}%</span>
                                    </div>
                                    <div class="metric">
                                        <span class="metric-label">Total Return:</span>
                                        <span class="metric-value">${(metrics.total_return || 0).toFixed(2)}%</span>
                                    </div>
                                </div>
                            `;
                        });
                        reportsDiv.innerHTML = html;
                    } else {
                        reportsDiv.innerHTML = '<div class="error">No reports available yet. The bot needs to run for some time to generate reports.</div>';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('reports-list').innerHTML = '<div class="error">Error loading reports</div>';
                });
        }

        // Auto-refresh every 30 seconds
        setInterval(refreshDashboard, 30000);

        // Initial load
        refreshDashboard();
    </script>
</body>
</html>
"""


@app.route("/")
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_TEMPLATE)


@app.route("/api/bot_status")
def bot_status():
    """Get bot status from the enhanced trading bot"""
    try:
        response = requests.get(BOT_STATUS_URL, timeout=5)
        if response.status_code == 200:
            return jsonify({"success": True, "data": response.json()})
        else:
            return jsonify({"success": False, "error": f"HTTP {response.status_code}"})
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/reports")
def reports():
    """Get trading reports"""
    try:
        reports_list = []
        reports_dir = "enhanced_reports"

        if os.path.exists(reports_dir):
            for filename in sorted(os.listdir(reports_dir), reverse=True)[:10]:
                if filename.endswith(".json"):
                    filepath = os.path.join(reports_dir, filename)
                    try:
                        with open(filepath, "r") as f:
                            report = json.load(f)
                            reports_list.append(report)
                    except Exception as e:
                        logger.error(f"Error reading report {filename}: {e}")

        return jsonify({"success": True, "reports": reports_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "enhanced-dashboard",
        }
    )


def main():
    """Main function"""
    print("🚀 Starting Enhanced Trading Bot Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5003")
    print("🔗 Bot health check: http://localhost:5002/health")
    print("⏯️  Press Ctrl+C to stop the dashboard")

    # Check if bot is running
    try:
        response = requests.get(BOT_HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Enhanced trading bot is running and accessible")
        else:
            print("⚠️  Warning: Enhanced trading bot may not be running properly")
    except:
        print("❌ Error: Cannot connect to enhanced trading bot")
        print("   Make sure the enhanced bot is running on port 5002")

    # Start the dashboard
    app.run(host="0.0.0.0", port=5003, debug=False)


if __name__ == "__main__":
    main()
