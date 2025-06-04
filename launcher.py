#!/usr/bin/env python3
"""
🚀 Luno Trading Bot - Simple Launcher
====================================

Easy launcher for the trading bot with a simple menu interface.
Perfect for non-technical users!
"""

import os
import sys
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header():
    """Print the launcher header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("🚀 LUNO TRADING BOT LAUNCHER")
    print("=" * 40)
    print(f"{Colors.END}")


def check_setup():
    """Check if the bot is properly set up"""
    env_file = Path(".env")
    if not env_file.exists():
        return False, "No .env configuration file found"

    # Check if API keys are configured
    try:
        with open(env_file, "r") as f:
            content = f.read()
            if (
                "your_luno_api_key_here" in content
                or "your_luno_api_secret_here" in content
            ):
                return False, "API credentials not configured"
        return True, "Setup complete"
    except Exception as e:
        return False, f"Error checking setup: {e}"


def run_setup():
    """Run the setup wizard"""
    print(f"\n{Colors.BLUE}Running setup wizard...{Colors.END}")
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


def start_bot(dry_run=True):
    """Start the trading bot"""
    run_script = Path("scripts/run_bot.py")

    if not run_script.exists():
        print(f"{Colors.RED}❌ Bot script not found at {run_script}{Colors.END}")
        return False

    try:
        mode = "dry-run" if dry_run else "live"
        mode_text = "SIMULATION" if dry_run else "LIVE TRADING"

        print(f"\n{Colors.BLUE}Starting bot in {mode_text} mode...{Colors.END}")

        if dry_run:
            subprocess.run([sys.executable, str(run_script), "--dry-run"], check=True)
        else:
            print(f"{Colors.RED}⚠️  WARNING: Starting in LIVE TRADING mode!{Colors.END}")
            confirm = input(
                "Are you sure? This involves real money! (yes/no): "
            ).lower()
            if confirm == "yes":
                subprocess.run([sys.executable, str(run_script)], check=True)
            else:
                print(f"{Colors.GREEN}✅ Cancelled for safety{Colors.END}")
                return False

        return True

    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Bot failed to start: {e}{Colors.END}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Bot stopped by user{Colors.END}")
        return True


def show_menu():
    """Show the main menu"""
    print(f"\n{Colors.WHITE}What would you like to do?{Colors.END}")
    print(f"  1. 🔧 Setup/Configure Bot")
    print(f"  2. 🎮 Start Bot (Simulation Mode)")
    print(f"  3. 💰 Start Bot (Live Trading)")
    print(f"  4. 📊 Open Dashboard")
    print(f"  5. 📖 View Documentation")
    print(f"  6. 🧪 Test Configuration")
    print(f"  7. ❌ Exit")
    print()


def open_dashboard():
    """Open the dashboard in browser"""
    import webbrowser

    try:
        webbrowser.open("http://localhost:5001")
        print(f"{Colors.GREEN}✅ Dashboard opened in browser{Colors.END}")
        print(f"{Colors.CYAN}URL: http://localhost:5001{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Could not open browser: {e}{Colors.END}")
        print(f"{Colors.CYAN}Please manually open: http://localhost:5001{Colors.END}")


def view_docs():
    """Show documentation information"""
    print(f"\n{Colors.BLUE}📖 Documentation{Colors.END}")
    print(f"{Colors.WHITE}Available documentation:{Colors.END}")
    print(f"  • README.md - Main documentation")
    print(f"  • docs/QUICK_START.md - Quick start guide")
    print(f"  • docs/README.md - Detailed documentation")
    print()
    print(f"{Colors.CYAN}💡 Pro tip: Start with the Quick Start guide!{Colors.END}")


def test_config():
    """Test the current configuration"""
    print(f"\n{Colors.BLUE}🧪 Testing configuration...{Colors.END}")
    test_script = Path("tests/test_api_credentials.py")

    if not test_script.exists():
        print(f"{Colors.RED}❌ Test script not found{Colors.END}")
        return False

    try:
        subprocess.run([sys.executable, str(test_script)], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Configuration test failed{Colors.END}")
        return False


def main():
    """Main launcher loop"""
    print_header()

    # Check setup status
    is_setup, setup_message = check_setup()

    if is_setup:
        print(f"{Colors.GREEN}✅ Bot is configured and ready to use!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  Setup required: {setup_message}{Colors.END}")
        print(f"{Colors.CYAN}💡 Choose option 1 to set up your bot{Colors.END}")

    while True:
        show_menu()

        try:
            choice = input(
                f"{Colors.WHITE}Enter your choice (1-7): {Colors.END}"
            ).strip()

            if choice == "1":
                run_setup()
                # Recheck setup after running wizard
                is_setup, setup_message = check_setup()

            elif choice == "2":
                if not is_setup:
                    print(
                        f"{Colors.RED}❌ Please complete setup first (option 1){Colors.END}"
                    )
                else:
                    start_bot(dry_run=True)

            elif choice == "3":
                if not is_setup:
                    print(
                        f"{Colors.RED}❌ Please complete setup first (option 1){Colors.END}"
                    )
                else:
                    start_bot(dry_run=False)

            elif choice == "4":
                open_dashboard()

            elif choice == "5":
                view_docs()

            elif choice == "6":
                if not is_setup:
                    print(
                        f"{Colors.RED}❌ Please complete setup first (option 1){Colors.END}"
                    )
                else:
                    test_config()

            elif choice == "7":
                print(f"\n{Colors.GREEN}👋 Goodbye! Happy trading!{Colors.END}")
                break

            else:
                print(
                    f"{Colors.YELLOW}⚠️  Invalid choice. Please enter 1-7.{Colors.END}"
                )

        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}👋 Goodbye! Happy trading!{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")


if __name__ == "__main__":
    main()
