#!/usr/bin/env python3
"""
Advanced Trading Bot Launcher
Professional launcher with comprehensive features and enhanced capabilities
"""

import sys
import subprocess
import os
from pathlib import Path
import json
import time
import webbrowser


class Colors:
    """ANSI color codes for terminal output"""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    END = "\033[0m"


def print_header():
    """Print the enhanced application header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                🚀 ADVANCED LUNO TRADING BOT 🚀               ║")
    print("║           Next-Generation Cryptocurrency Trading             ║")
    print("║        Multi-Pair • Multi-Timeframe • AI-Enhanced           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    print(f"{Colors.WHITE}🔥 Enhanced Features: Portfolio Management | Advanced Analytics | Smart Notifications{Colors.END}")


def check_setup():
    """Check if the bot is properly set up"""
    env_file = Path(".env")
    config_exists = env_file.exists()

    if config_exists:
        # Check if required variables are set
        try:
            with open(env_file, "r") as f:
                content = f.read()
                has_api_key = "LUNO_API_KEY=" in content and len(
                    content.split("LUNO_API_KEY=")[1].split("\n")[0].strip()
                ) > 0
                has_api_secret = "LUNO_API_SECRET=" in content and len(
                    content.split("LUNO_API_SECRET=")[1].split("\n")[0].strip()
                ) > 0

                if has_api_key and has_api_secret:
                    return True, "Bot is configured and ready!"
                else:
                    return False, "API credentials are missing or empty"
        except Exception:
            return False, "Error reading configuration file"
    else:
        return False, "Configuration file (.env) not found"


def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import numpy
        import pandas
        import requests
        import flask
        import plotly
        return True, "All dependencies are installed"
    except ImportError as e:
        return False, f"Missing dependency: {str(e)}"


def run_setup():
    """Run the enhanced setup wizard"""
    print(f"\n{Colors.BLUE}Running enhanced setup wizard...{Colors.END}")
    setup_wizard = Path("setup_wizard.py")

    if not setup_wizard.exists():
        print(f"{Colors.RED}❌ Setup wizard not found{Colors.END}")
        return False

    try:
        subprocess.run([sys.executable, str(setup_wizard)], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Setup failed{Colors.END}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Setup cancelled{Colors.END}")
        return False


def start_bot(mode="simulation"):
    """Start the advanced trading bot"""
    
    # Choose the appropriate bot script
    if mode == "advanced":
        run_script = Path("scripts/run_advanced_bot.py")
    else:
        run_script = Path("scripts/run_bot.py")

    if not run_script.exists():
        print(f"{Colors.RED}❌ Bot script not found at {run_script}{Colors.END}")
        return False

    try:
        if mode == "simulation":
            mode_text = "SIMULATION"
            print(f"\n{Colors.BLUE}Starting bot in {mode_text} mode...{Colors.END}")
            subprocess.run([sys.executable, str(run_script), "--dry-run"], check=True)
        elif mode == "live":
            mode_text = "LIVE TRADING"
            print(f"\n{Colors.RED}⚠️  WARNING: Starting in {mode_text} mode!{Colors.END}")
            confirm = input("Are you sure? This involves real money! (yes/no): ").lower()
            if confirm == "yes":
                subprocess.run([sys.executable, str(run_script)], check=True)
            else:
                print(f"{Colors.GREEN}✅ Cancelled for safety{Colors.END}")
                return False
        elif mode == "advanced":
            mode_text = "ADVANCED MULTI-PAIR"
            print(f"\n{Colors.CYAN}Starting {mode_text} mode...{Colors.END}")
            subprocess.run([sys.executable, str(run_script), "--advanced"], check=True)

        return True

    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Bot failed to start: {e}{Colors.END}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Bot stopped by user{Colors.END}")
        return True


def show_main_menu():
    """Show the enhanced main menu"""
    print(f"\n{Colors.WHITE}{Colors.BOLD}🎯 MAIN MENU{Colors.END}")
    print(f"{Colors.WHITE}═══════════════════════════════════════{Colors.END}")
    print(f"  {Colors.CYAN}1.{Colors.END} 🔧 Setup & Configuration")
    print(f"  {Colors.GREEN}2.{Colors.END} 🎮 Start Bot (Simulation)")
    print(f"  {Colors.YELLOW}3.{Colors.END} 💰 Start Bot (Live Trading)")
    print(f"  {Colors.MAGENTA}4.{Colors.END} 🚀 Start Advanced Bot (Multi-Pair)")
    print(f"  {Colors.BLUE}5.{Colors.END} 📊 Dashboard & Analytics")
    print(f"  {Colors.CYAN}6.{Colors.END} 🧪 Testing & Optimization")
    print(f"  {Colors.WHITE}7.{Colors.END} 📖 Documentation & Help")
    print(f"  {Colors.RED}8.{Colors.END} ❌ Exit")
    print()


def show_dashboard_menu():
    """Show dashboard options"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}📊 DASHBOARD & ANALYTICS{Colors.END}")
    print(f"{Colors.WHITE}═══════════════════════════════════════{Colors.END}")
    print(f"  {Colors.CYAN}1.{Colors.END} 📈 Live Trading Dashboard")
    print(f"  {Colors.GREEN}2.{Colors.END} 📊 Enhanced Analytics Dashboard")
    print(f"  {Colors.YELLOW}3.{Colors.END} 🔍 Backtesting Dashboard")
    print(f"  {Colors.MAGENTA}4.{Colors.END} 📱 Portfolio Manager")
    print(f"  {Colors.WHITE}5.{Colors.END} ⬅️  Back to Main Menu")
    print()


def show_testing_menu():
    """Show testing and optimization options"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}🧪 TESTING & OPTIMIZATION{Colors.END}")
    print(f"{Colors.WHITE}═══════════════════════════════════════{Colors.END}")
    print(f"  {Colors.CYAN}1.{Colors.END} 🔍 Test API Configuration")
    print(f"  {Colors.GREEN}2.{Colors.END} 📈 Run Backtesting")
    print(f"  {Colors.YELLOW}3.{Colors.END} ⚙️  Strategy Optimization")
    print(f"  {Colors.MAGENTA}4.{Colors.END} 📊 Performance Analysis")
    print(f"  {Colors.BLUE}5.{Colors.END} 🎯 Multi-Timeframe Analysis")
    print(f"  {Colors.WHITE}6.{Colors.END} ⬅️  Back to Main Menu")
    print()


def open_dashboard(dashboard_type="basic"):
    """Open the specified trading dashboard"""
    
    dashboard_scripts = {
        "basic": "run_dashboard.py",
        "enhanced": "run_enhanced_dashboard.py", 
        "backtest": "run_backtest_dashboard.py",
        "portfolio": "run_portfolio_dashboard.py"
    }
    
    script_name = dashboard_scripts.get(dashboard_type, "run_dashboard.py")
    dashboard_script = Path(script_name)

    if not dashboard_script.exists():
        print(f"{Colors.RED}❌ Dashboard script not found: {script_name}{Colors.END}")
        return False

    try:
        print(f"\n{Colors.BLUE}Opening {dashboard_type} dashboard...{Colors.END}")
        subprocess.Popen([sys.executable, str(dashboard_script)])
        print(f"{Colors.GREEN}✅ Dashboard started! Check your browser at http://localhost:5000{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to start dashboard: {e}{Colors.END}")
        return False


def run_backtesting():
    """Run backtesting analysis"""
    backtest_script = Path("run_backtest.py")
    
    if not backtest_script.exists():
        print(f"{Colors.RED}❌ Backtest script not found{Colors.END}")
        return False
    
    try:
        print(f"\n{Colors.BLUE}Running backtesting analysis...{Colors.END}")
        subprocess.run([sys.executable, str(backtest_script)], check=True)
        print(f"{Colors.GREEN}✅ Backtesting completed!{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Backtesting failed: {e}{Colors.END}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Backtesting cancelled{Colors.END}")
        return False


def run_strategy_optimization():
    """Run strategy parameter optimization"""
    print(f"\n{Colors.BLUE}Starting strategy optimization...{Colors.END}")
    print(f"{Colors.YELLOW}This may take several minutes depending on parameters.{Colors.END}")
    
    try:
        # Import and run optimization
        from src.backtesting.strategy_optimizer import StrategyOptimizer, ParameterRange
        from src.backtesting.backtest_engine import BacktestConfig
        from src.config.enhanced_settings import EnhancedTradingConfig
        from datetime import datetime, timedelta
        
        # Create optimization configuration
        backtest_config = BacktestConfig(
            start_date=datetime.now() - timedelta(days=90),
            end_date=datetime.now(),
            initial_capital=10000.0,
            trading_pair="XBTMYR"
        )
        
        base_config = EnhancedTradingConfig()
        optimizer = StrategyOptimizer(base_config, backtest_config)
        
        # Get default parameter ranges
        param_ranges = optimizer.get_default_parameter_ranges()
        
        # Run optimization
        results = optimizer.optimize_parameters(param_ranges, max_combinations=50)
        
        print(f"{Colors.GREEN}✅ Optimization completed!{Colors.END}")
        print(f"Best score: {results.best_score:.4f}")
        print(f"Best parameters: {results.best_config}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Optimization failed: {e}{Colors.END}")
        return False


def view_documentation():
    """Open documentation in browser"""
    docs_url = "https://amanasmuei.github.io/trading-bot-luno/"
    try:
        webbrowser.open(docs_url)
        print(f"{Colors.GREEN}✅ Documentation opened in browser{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to open documentation: {e}{Colors.END}")
        return False


def test_configuration():
    """Test the bot configuration"""
    test_script = Path("tests/test_api_credentials.py")

    if not test_script.exists():
        print(f"{Colors.RED}❌ Test script not found{Colors.END}")
        return False

    try:
        print(f"\n{Colors.BLUE}Testing configuration...{Colors.END}")
        result = subprocess.run(
            [sys.executable, str(test_script)], capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Configuration test passed!{Colors.END}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"{Colors.RED}❌ Configuration test failed!{Colors.END}")
            if result.stderr:
                print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"{Colors.RED}❌ Failed to run test: {e}{Colors.END}")
        return False


def main():
    """Main launcher loop"""
    print_header()

    # Check setup status
    is_setup, setup_message = check_setup()
    deps_ok, deps_message = check_dependencies()

    if is_setup:
        print(f"{Colors.GREEN}✅ Bot is configured and ready to use!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  {setup_message}{Colors.END}")
        print(f"{Colors.BLUE}💡 Run setup first to configure your bot{Colors.END}")

    if not deps_ok:
        print(f"{Colors.YELLOW}⚠️  {deps_message}{Colors.END}")
        print(f"{Colors.BLUE}💡 Run: pip install -r requirements.txt{Colors.END}")

    current_menu = "main"

    while True:
        if current_menu == "main":
            show_main_menu()
        elif current_menu == "dashboard":
            show_dashboard_menu()
        elif current_menu == "testing":
            show_testing_menu()

        try:
            if current_menu == "main":
                choice = input(f"{Colors.WHITE}Enter your choice (1-8): {Colors.END}").strip()
            else:
                choice = input(f"{Colors.WHITE}Enter your choice (1-6): {Colors.END}").strip()

            # Main menu handling
            if current_menu == "main":
                if choice == "1":
                    run_setup()
                    is_setup, setup_message = check_setup()
                elif choice == "2":
                    if is_setup:
                        start_bot("simulation")
                    else:
                        print(f"{Colors.RED}❌ Please run setup first (option 1){Colors.END}")
                elif choice == "3":
                    if is_setup:
                        start_bot("live")
                    else:
                        print(f"{Colors.RED}❌ Please run setup first (option 1){Colors.END}")
                elif choice == "4":
                    if is_setup:
                        start_bot("advanced")
                    else:
                        print(f"{Colors.RED}❌ Please run setup first (option 1){Colors.END}")
                elif choice == "5":
                    current_menu = "dashboard"
                elif choice == "6":
                    current_menu = "testing"
                elif choice == "7":
                    view_documentation()
                elif choice == "8":
                    print(f"\n{Colors.GREEN}👋 Goodbye! Happy trading!{Colors.END}")
                    break
                else:
                    print(f"{Colors.RED}❌ Invalid choice. Please try again.{Colors.END}")

            # Dashboard menu handling
            elif current_menu == "dashboard":
                if choice == "1":
                    open_dashboard("basic")
                elif choice == "2":
                    open_dashboard("enhanced")
                elif choice == "3":
                    open_dashboard("backtest")
                elif choice == "4":
                    open_dashboard("portfolio")
                elif choice == "5":
                    current_menu = "main"
                else:
                    print(f"{Colors.RED}❌ Invalid choice. Please try again.{Colors.END}")

            # Testing menu handling
            elif current_menu == "testing":
                if choice == "1":
                    if is_setup:
                        test_configuration()
                    else:
                        print(f"{Colors.RED}❌ Please run setup first{Colors.END}")
                elif choice == "2":
                    if is_setup:
                        run_backtesting()
                    else:
                        print(f"{Colors.RED}❌ Please run setup first{Colors.END}")
                elif choice == "3":
                    if is_setup:
                        run_strategy_optimization()
                    else:
                        print(f"{Colors.RED}❌ Please run setup first{Colors.END}")
                elif choice == "4":
                    print(f"{Colors.BLUE}Performance analysis feature coming soon!{Colors.END}")
                elif choice == "5":
                    print(f"{Colors.BLUE}Multi-timeframe analysis feature coming soon!{Colors.END}")
                elif choice == "6":
                    current_menu = "main"
                else:
                    print(f"{Colors.RED}❌ Invalid choice. Please try again.{Colors.END}")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}👋 Goodbye! Happy trading!{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ An error occurred: {e}{Colors.END}")

        # Small delay before showing menu again
        time.sleep(0.5)


if __name__ == "__main__":
    main()
