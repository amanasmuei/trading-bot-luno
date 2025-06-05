"""
Enhanced Trading Bot Dashboard using Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
import requests
import time
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Enhanced Trading Bot Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    .status-stopped {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)


class EnhancedDashboard:
    """Enhanced Trading Bot Dashboard"""

    def __init__(self):
        self.bot_health_url = "http://localhost:5002/health"
        self.bot_status_url = "http://localhost:5002/status"

    def check_bot_health(self) -> Dict:
        """Check if the enhanced trading bot is running"""
        try:
            response = requests.get(self.bot_health_url, timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "data": response.json()}
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"status": "offline", "error": str(e)}

    def get_bot_status(self) -> Dict:
        """Get detailed bot status"""
        try:
            response = requests.get(self.bot_status_url, timeout=5)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def load_trading_reports(self) -> List[Dict]:
        """Load recent trading reports"""
        reports = []
        reports_dir = "enhanced_reports"

        if os.path.exists(reports_dir):
            try:
                for filename in sorted(os.listdir(reports_dir), reverse=True)[:10]:
                    if filename.endswith(".json"):
                        filepath = os.path.join(reports_dir, filename)
                        with open(filepath, "r") as f:
                            report = json.load(f)
                            reports.append(report)
            except Exception as e:
                logger.error(f"Error loading reports: {e}")

        return reports

    def render_header(self):
        """Render dashboard header"""
        st.markdown(
            """
        <div class="main-header">
            <h1>🚀 Enhanced Trading Bot Dashboard</h1>
            <p>Advanced Cryptocurrency Trading Bot Monitoring</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def render_bot_status(self):
        """Render bot status section"""
        st.subheader("🤖 Bot Status")

        health = self.check_bot_health()
        status_data = self.get_bot_status()

        col1, col2, col3 = st.columns(3)

        with col1:
            if health["status"] == "healthy":
                st.markdown(
                    '<p class="status-running">🟢 RUNNING</p>', unsafe_allow_html=True
                )
            elif health["status"] == "unhealthy":
                st.markdown(
                    '<p class="status-warning">🟡 UNHEALTHY</p>', unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<p class="status-stopped">🔴 OFFLINE</p>', unsafe_allow_html=True
                )

        with col2:
            if status_data.get("success") and "data" in status_data:
                bot_data = status_data["data"].get("bot_status", {})
                st.metric("Daily Trades", bot_data.get("daily_trades", "N/A"))

        with col3:
            if status_data.get("success") and "data" in status_data:
                bot_data = status_data["data"].get("bot_status", {})
                daily_pnl = bot_data.get("daily_pnl", 0)
                st.metric(
                    "Daily P&L",
                    f"{daily_pnl:.2f}%",
                    delta=f"{daily_pnl:.2f}%" if daily_pnl != 0 else None,
                )

        # Show detailed status
        if status_data.get("success"):
            with st.expander("Detailed Status"):
                st.json(status_data["data"])
        else:
            st.error(
                f"Failed to get bot status: {status_data.get('error', 'Unknown error')}"
            )

    def render_performance_metrics(self):
        """Render performance metrics"""
        st.subheader("📊 Performance Metrics")

        reports = self.load_trading_reports()

        if not reports:
            st.warning(
                "No trading reports found. The bot may not have generated any reports yet."
            )
            return

        # Get latest report
        latest_report = reports[0]
        metrics = latest_report.get("performance_metrics", {})

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Trades", metrics.get("total_trades", 0))

        with col2:
            win_rate = metrics.get("win_rate", 0)
            st.metric("Win Rate", f"{win_rate:.1%}")

        with col3:
            total_return = metrics.get("total_return", 0)
            st.metric("Total Return", f"{total_return:.2f}%")

        with col4:
            profit_factor = metrics.get("profit_factor", 0)
            st.metric("Profit Factor", f"{profit_factor:.2f}")

    def render_recent_trades(self):
        """Render recent trades"""
        st.subheader("💼 Recent Trades")

        reports = self.load_trading_reports()

        if not reports:
            st.info("No trades data available")
            return

        # Combine trades from recent reports
        all_trades = []
        for report in reports[:3]:  # Last 3 reports
            trades = report.get("trades_history", [])
            all_trades.extend(trades)

        if not all_trades:
            st.info("No trades executed yet")
            return

        # Convert to DataFrame
        df = pd.DataFrame(all_trades)

        # Sort by timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp", ascending=False)

        # Display recent trades
        st.dataframe(
            df[
                ["timestamp", "action", "price", "volume", "confidence", "strength"]
            ].head(10),
            use_container_width=True,
        )

    def render_charts(self):
        """Render trading charts"""
        st.subheader("📈 Trading Analysis")

        reports = self.load_trading_reports()

        if not reports:
            st.info("No data available for charts")
            return

        # Performance over time chart
        if len(reports) > 1:
            performance_data = []
            for report in reversed(reports):
                metrics = report.get("performance_metrics", {})
                performance_data.append(
                    {
                        "date": report.get("generated_at", ""),
                        "total_return": metrics.get("total_return", 0),
                        "win_rate": metrics.get("win_rate", 0),
                        "total_trades": metrics.get("total_trades", 0),
                    }
                )

            df_perf = pd.DataFrame(performance_data)
            df_perf["date"] = pd.to_datetime(df_perf["date"])

            # Total return chart
            fig_return = px.line(
                df_perf,
                x="date",
                y="total_return",
                title="Total Return Over Time",
                labels={"total_return": "Total Return (%)", "date": "Date"},
            )
            st.plotly_chart(fig_return, use_container_width=True)

            # Win rate chart
            fig_winrate = px.line(
                df_perf,
                x="date",
                y="win_rate",
                title="Win Rate Over Time",
                labels={"win_rate": "Win Rate", "date": "Date"},
            )
            st.plotly_chart(fig_winrate, use_container_width=True)


def main():
    """Main dashboard function"""
    dashboard = EnhancedDashboard()

    # Render dashboard
    dashboard.render_header()

    # Auto-refresh
    if st.sidebar.button("🔄 Refresh"):
        st.rerun()

    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=False)

    # Main content
    dashboard.render_bot_status()
    st.divider()
    dashboard.render_performance_metrics()
    st.divider()
    dashboard.render_recent_trades()
    st.divider()
    dashboard.render_charts()

    # Sidebar info
    st.sidebar.markdown("### 📋 Dashboard Info")
    st.sidebar.info(
        """
    This dashboard monitors the Enhanced Trading Bot:
    - Real-time bot status
    - Performance metrics
    - Trade history
    - Analytics charts
    """
    )

    # Health check endpoint
    st.sidebar.markdown("### 🔗 Health Check")
    st.sidebar.code("http://localhost:5003/health")

    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main()
