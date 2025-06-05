#!/usr/bin/env python3
"""
Launch the Backtesting Dashboard
Interactive Streamlit interface for backtesting and optimization
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def check_dependencies():
    """Check if required dependencies are installed"""
    
    required_packages = [
        "streamlit",
        "plotly",
        "pandas",
        "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print()
        print("📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def main():
    """Launch the backtesting dashboard"""
    
    print("🚀 Starting Trading Bot Backtesting Dashboard...")
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Get the dashboard script path
    dashboard_script = Path(__file__).parent / "src" / "backtesting" / "backtest_dashboard.py"
    
    if not dashboard_script.exists():
        print(f"❌ Dashboard script not found: {dashboard_script}")
        sys.exit(1)
    
    # Launch Streamlit
    try:
        print("📊 Launching Streamlit dashboard...")
        print("🌐 Dashboard will open in your browser automatically")
        print("⏹️  Press Ctrl+C to stop the dashboard")
        print()
        
        # Run streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_script),
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
