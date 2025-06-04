#!/usr/bin/env python3
"""
🚀 Luno Trading Bot - Interactive Setup Wizard
==============================================

This wizard will guide you through setting up the Luno Trading Bot
in just a few simple steps. No technical knowledge required!
"""

import os
import sys
import subprocess
import requests
from pathlib import Path
from typing import Tuple


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


class SetupWizard:
    """Interactive setup wizard for the Luno Trading Bot"""

    def __init__(self):
        self.config = {}
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.env_example = self.project_root / ".env.example"

    def print_header(self):
        """Print the welcome header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}")
        print("🚀 LUNO TRADING BOT SETUP WIZARD")
        print("=" * 50)
        print(f"{Colors.END}")
        print(
            f"{Colors.WHITE}Welcome! This wizard will help you set up your trading bot in 3 easy steps:{Colors.END}"
        )
        print(f"{Colors.YELLOW}  1. 📦 Install dependencies")
        print(f"  2. 🔑 Configure API credentials")
        print(f"  3. ⚙️  Set trading preferences{Colors.END}")
        print()

    def check_python(self) -> bool:
        """Check if Python 3.8+ is available"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                print(
                    f"{Colors.GREEN}✅ Python {version.major}.{version.minor}.{version.micro} found{Colors.END}"
                )
                return True
            else:
                print(
                    f"{Colors.RED}❌ Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}{Colors.END}"
                )
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Error checking Python version: {e}{Colors.END}")
            return False

    def install_dependencies(self) -> bool:
        """Install required Python packages"""
        print(f"\n{Colors.BLUE}📦 Installing dependencies...{Colors.END}")

        try:
            # Check if requirements.txt exists
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                print(f"{Colors.RED}❌ requirements.txt not found{Colors.END}")
                return False

            # Install packages
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(
                    f"{Colors.GREEN}✅ All dependencies installed successfully{Colors.END}"
                )
                return True
            else:
                print(f"{Colors.RED}❌ Failed to install dependencies:{Colors.END}")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"{Colors.RED}❌ Error installing dependencies: {e}{Colors.END}")
            return False

    def get_user_input(
        self, prompt: str, default: str = "", required: bool = True
    ) -> str:
        """Get user input with validation"""
        while True:
            if default:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()

            if user_input or not required:
                return user_input
            elif required:
                print(
                    f"{Colors.YELLOW}⚠️  This field is required. Please enter a value.{Colors.END}"
                )

    def validate_api_credentials(
        self, api_key: str, api_secret: str
    ) -> Tuple[bool, str]:
        """Validate Luno API credentials"""
        print(f"{Colors.BLUE}🔍 Validating API credentials...{Colors.END}")

        try:
            from requests.auth import HTTPBasicAuth

            # Test with a simple API call
            response = requests.get(
                "https://api.luno.com/api/1/balance",
                auth=HTTPBasicAuth(api_key, api_secret),
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                balances = data.get("balance", [])
                print(f"{Colors.GREEN}✅ API credentials are valid!{Colors.END}")
                print(
                    f"{Colors.CYAN}💰 Found {len(balances)} currency balances in your account{Colors.END}"
                )
                return True, "Valid credentials"
            elif response.status_code == 401:
                return False, "Invalid API credentials (401 Unauthorized)"
            else:
                return False, f"API error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def configure_api_credentials(self) -> bool:
        """Configure Luno API credentials"""
        print(f"\n{Colors.BLUE}🔑 API Credentials Setup{Colors.END}")
        print(
            f"{Colors.WHITE}You need Luno API credentials to use this bot.{Colors.END}"
        )
        print(f"{Colors.CYAN}📖 How to get API credentials:{Colors.END}")
        print(f"   1. Go to: https://www.luno.com/wallet/security/api_keys")
        print(
            f"   2. Create a new API key with 'Perm_R_Balance' and 'Perm_W_Orders' permissions"
        )
        print(f"   3. Copy the API Key and API Secret")
        print()

        # Get API credentials
        api_key = self.get_user_input("Enter your Luno API Key")
        api_secret = self.get_user_input("Enter your Luno API Secret")

        # Validate credentials
        is_valid, message = self.validate_api_credentials(api_key, api_secret)

        if is_valid:
            self.config["LUNO_API_KEY"] = api_key
            self.config["LUNO_API_SECRET"] = api_secret
            return True
        else:
            print(f"{Colors.RED}❌ {message}{Colors.END}")
            retry = self.get_user_input(
                "Would you like to try again? (y/n)", "y", False
            ).lower()
            if retry in ["y", "yes"]:
                return self.configure_api_credentials()
            return False

    def configure_trading_preferences(self) -> bool:
        """Configure trading preferences"""
        print(f"\n{Colors.BLUE}⚙️  Trading Preferences{Colors.END}")

        # Trading pair selection
        supported_pairs = {
            "1": ("XBTMYR", "Bitcoin/Malaysian Ringgit"),
            "2": ("XBTZAR", "Bitcoin/South African Rand"),
            "3": ("XBTEUR", "Bitcoin/Euro"),
            "4": ("ETHMYR", "Ethereum/Malaysian Ringgit"),
            "5": ("ETHZAR", "Ethereum/South African Rand"),
        }

        print(f"{Colors.WHITE}Select your preferred trading pair:{Colors.END}")
        for key, (pair, name) in supported_pairs.items():
            print(f"  {key}. {pair} - {name}")

        choice = self.get_user_input("Enter your choice (1-5)", "1")
        if choice in supported_pairs:
            pair, name = supported_pairs[choice]
            self.config["TRADING_PAIR"] = pair
            print(f"{Colors.GREEN}✅ Selected: {pair} - {name}{Colors.END}")
        else:
            self.config["TRADING_PAIR"] = "XBTMYR"

        # Risk management
        print(f"\n{Colors.WHITE}Risk Management Settings:{Colors.END}")

        position_size = self.get_user_input(
            "Maximum position size per trade (% of portfolio)", "2.0"
        )
        self.config["MAX_POSITION_SIZE_PERCENT"] = float(position_size)

        stop_loss = self.get_user_input("Stop loss percentage", "1.5")
        self.config["STOP_LOSS_PERCENT"] = float(stop_loss)

        take_profit = self.get_user_input("Take profit percentage", "3.0")
        self.config["TAKE_PROFIT_PERCENT"] = float(take_profit)

        # Trading mode
        print(f"\n{Colors.WHITE}Trading Mode:{Colors.END}")
        print(
            f"  1. Dry Run (Simulation) - {Colors.GREEN}Recommended for beginners{Colors.END}"
        )
        print(f"  2. Live Trading - {Colors.RED}Real money at risk!{Colors.END}")

        mode_choice = self.get_user_input("Select mode (1-2)", "1")
        self.config["DRY_RUN"] = "true" if mode_choice == "1" else "false"

        if mode_choice == "2":
            print(f"{Colors.RED}⚠️  WARNING: Live trading mode selected!{Colors.END}")
            confirm = self.get_user_input(
                "Are you sure? This involves real money! (yes/no)", "no"
            )
            if confirm.lower() != "yes":
                self.config["DRY_RUN"] = "true"
                print(
                    f"{Colors.GREEN}✅ Switched to dry run mode for safety{Colors.END}"
                )

        return True

    def save_configuration(self) -> bool:
        """Save configuration to .env file"""
        print(f"\n{Colors.BLUE}💾 Saving configuration...{Colors.END}")

        try:
            # Load template if it exists
            template_config = {}
            if self.env_example.exists():
                with open(self.env_example, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            template_config[key] = value

            # Update with user configuration
            template_config.update(self.config)

            # Write to .env file
            with open(self.env_file, "w") as f:
                f.write("# Luno Trading Bot Configuration\n")
                f.write("# Generated by Setup Wizard\n\n")

                # API credentials
                f.write("# Luno API Credentials\n")
                f.write(f"LUNO_API_KEY={template_config.get('LUNO_API_KEY', '')}\n")
                f.write(
                    f"LUNO_API_SECRET={template_config.get('LUNO_API_SECRET', '')}\n\n"
                )

                # Trading configuration
                f.write("# Trading Configuration\n")
                f.write(
                    f"TRADING_PAIR={template_config.get('TRADING_PAIR', 'XBTMYR')}\n"
                )
                f.write(
                    f"MAX_POSITION_SIZE_PERCENT={template_config.get('MAX_POSITION_SIZE_PERCENT', '2.0')}\n"
                )
                f.write(
                    f"STOP_LOSS_PERCENT={template_config.get('STOP_LOSS_PERCENT', '1.5')}\n"
                )
                f.write(
                    f"TAKE_PROFIT_PERCENT={template_config.get('TAKE_PROFIT_PERCENT', '3.0')}\n"
                )
                f.write(
                    f"MAX_DAILY_TRADES={template_config.get('MAX_DAILY_TRADES', '3')}\n\n"
                )

                # Bot operation
                f.write("# Bot Operation\n")
                f.write(f"DRY_RUN={template_config.get('DRY_RUN', 'true')}\n")
                f.write(
                    f"CHECK_INTERVAL={template_config.get('CHECK_INTERVAL', '60')}\n"
                )
                f.write(f"LOG_LEVEL={template_config.get('LOG_LEVEL', 'INFO')}\n\n")

                # Dashboard
                f.write("# Dashboard Configuration\n")
                f.write(
                    f"DASHBOARD_HOST={template_config.get('DASHBOARD_HOST', '127.0.0.1')}\n"
                )
                f.write(
                    f"DASHBOARD_PORT={template_config.get('DASHBOARD_PORT', '5001')}\n\n"
                )

                # Risk management
                f.write("# Risk Management\n")
                f.write(
                    f"ENABLE_STOP_LOSS={template_config.get('ENABLE_STOP_LOSS', 'true')}\n"
                )
                f.write(
                    f"ENABLE_TAKE_PROFIT={template_config.get('ENABLE_TAKE_PROFIT', 'true')}\n"
                )
                f.write(
                    f"MAX_DRAWDOWN_PERCENT={template_config.get('MAX_DRAWDOWN_PERCENT', '10.0')}\n\n"
                )

                # Technical analysis
                f.write("# Technical Analysis\n")
                f.write(f"RSI_PERIOD={template_config.get('RSI_PERIOD', '14')}\n")
                f.write(f"RSI_OVERSOLD={template_config.get('RSI_OVERSOLD', '30')}\n")
                f.write(
                    f"RSI_OVERBOUGHT={template_config.get('RSI_OVERBOUGHT', '70')}\n"
                )
                f.write(f"EMA_SHORT={template_config.get('EMA_SHORT', '9')}\n")
                f.write(f"EMA_LONG={template_config.get('EMA_LONG', '21')}\n")
                f.write(
                    f"BOLLINGER_PERIOD={template_config.get('BOLLINGER_PERIOD', '20')}\n"
                )
                f.write(
                    f"BOLLINGER_STD={template_config.get('BOLLINGER_STD', '2.0')}\n\n"
                )

                # Trading hours
                f.write("# Trading Hours\n")
                f.write(
                    f"TRADING_HOURS_START={template_config.get('TRADING_HOURS_START', '8')}\n"
                )
                f.write(
                    f"TRADING_HOURS_END={template_config.get('TRADING_HOURS_END', '22')}\n"
                )
                f.write(
                    f"TIMEZONE={template_config.get('TIMEZONE', 'Asia/Kuala_Lumpur')}\n"
                )

            print(f"{Colors.GREEN}✅ Configuration saved to .env{Colors.END}")
            return True

        except Exception as e:
            print(f"{Colors.RED}❌ Error saving configuration: {e}{Colors.END}")
            return False

    def test_installation(self) -> bool:
        """Test the bot installation"""
        print(f"\n{Colors.BLUE}🧪 Testing installation...{Colors.END}")

        try:
            # Test importing the bot modules
            sys.path.insert(0, str(self.project_root))

            # Test config loading
            from src.config.settings import TradingConfig

            config = TradingConfig()

            if config.api_key and config.api_secret:
                print(f"{Colors.GREEN}✅ Configuration loaded successfully{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Configuration not loaded properly{Colors.END}")
                return False

            # Test API client
            from src.api.luno_client import LunoClient

            LunoClient(config)  # Just test instantiation

            print(f"{Colors.GREEN}✅ All modules imported successfully{Colors.END}")
            return True

        except ImportError as e:
            print(f"{Colors.RED}❌ Import error: {e}{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Test failed: {e}{Colors.END}")
            return False

    def create_startup_scripts(self):
        """Create easy startup scripts"""
        print(f"\n{Colors.BLUE}📝 Creating startup scripts...{Colors.END}")

        # Create start_bot script
        if os.name == "nt":  # Windows
            script_content = """@echo off
echo Starting Luno Trading Bot...
python scripts/run_bot.py --dry-run
pause
"""
            script_path = self.project_root / "start_bot.bat"
        else:  # Unix-like
            script_content = """#!/bin/bash
echo "Starting Luno Trading Bot..."
python3 scripts/run_bot.py --dry-run
"""
            script_path = self.project_root / "start_bot.sh"

        try:
            with open(script_path, "w") as f:
                f.write(script_content)

            if os.name != "nt":
                os.chmod(script_path, 0o755)

            print(
                f"{Colors.GREEN}✅ Created startup script: {script_path.name}{Colors.END}"
            )

        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not create startup script: {e}{Colors.END}")

    def print_success_message(self):
        """Print success message and next steps"""
        print(f"\n{Colors.GREEN}{Colors.BOLD}")
        print("🎉 SETUP COMPLETE!")
        print("=" * 50)
        print(f"{Colors.END}")

        mode = (
            "DRY RUN (Simulation)"
            if self.config.get("DRY_RUN", "true") == "true"
            else "LIVE TRADING"
        )
        pair = self.config.get("TRADING_PAIR", "XBTMYR")

        print(f"{Colors.WHITE}Your trading bot is ready to go!{Colors.END}")
        print(f"{Colors.CYAN}📊 Trading Pair: {pair}{Colors.END}")
        print(f"{Colors.CYAN}🎮 Mode: {mode}{Colors.END}")
        print()

        print(f"{Colors.YELLOW}🚀 Quick Start Commands:{Colors.END}")
        if os.name == "nt":
            print(
                f"   {Colors.WHITE}start_bot.bat{Colors.END}                    # Start the bot"
            )
        else:
            print(
                f"   {Colors.WHITE}./start_bot.sh{Colors.END}                   # Start the bot"
            )
        print(
            f"   {Colors.WHITE}python scripts/run_bot.py --dry-run{Colors.END}  # Manual start"
        )
        print(
            f"   {Colors.WHITE}http://localhost:5001{Colors.END}               # View dashboard"
        )
        print()

        print(f"{Colors.YELLOW}📖 Important Notes:{Colors.END}")
        if self.config.get("DRY_RUN", "true") == "true":
            print(
                f"   • Bot is in {Colors.GREEN}SIMULATION MODE{Colors.END} - no real trades"
            )
            print(f"   • Monitor performance for a few days before going live")
        else:
            print(
                f"   • Bot is in {Colors.RED}LIVE MODE{Colors.END} - real money at risk!"
            )
            print(f"   • Start with small position sizes")
        print(f"   • Check the dashboard regularly at http://localhost:5001")
        print(f"   • Logs are saved in the 'logs' directory")
        print()

        print(f"{Colors.PURPLE}💡 Pro Tips:{Colors.END}")
        print(f"   • Always test in dry-run mode first")
        print(f"   • Monitor the bot daily for the first week")
        print(f"   • Keep your API credentials secure")
        print(f"   • Read the documentation in the 'docs' folder")
        print()

    def run(self):
        """Run the complete setup wizard"""
        try:
            self.print_header()

            # Step 1: Check Python
            if not self.check_python():
                print(f"{Colors.RED}❌ Setup failed: Python 3.8+ required{Colors.END}")
                return False

            # Step 2: Install dependencies
            if not self.install_dependencies():
                print(
                    f"{Colors.RED}❌ Setup failed: Could not install dependencies{Colors.END}"
                )
                return False

            # Step 3: Configure API credentials
            if not self.configure_api_credentials():
                print(
                    f"{Colors.RED}❌ Setup failed: Invalid API credentials{Colors.END}"
                )
                return False

            # Step 4: Configure trading preferences
            if not self.configure_trading_preferences():
                print(f"{Colors.RED}❌ Setup failed: Configuration error{Colors.END}")
                return False

            # Step 5: Save configuration
            if not self.save_configuration():
                print(
                    f"{Colors.RED}❌ Setup failed: Could not save configuration{Colors.END}"
                )
                return False

            # Step 6: Test installation
            if not self.test_installation():
                print(f"{Colors.YELLOW}⚠️  Setup completed but tests failed{Colors.END}")
                print(
                    f"{Colors.YELLOW}   You may need to check your configuration manually{Colors.END}"
                )

            # Step 7: Create startup scripts
            self.create_startup_scripts()

            # Step 8: Success message
            self.print_success_message()

            return True

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  Setup cancelled by user{Colors.END}")
            return False
        except Exception as e:
            print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
            return False


def main():
    """Main entry point"""
    wizard = SetupWizard()
    success = wizard.run()

    if not success:
        print(
            f"\n{Colors.RED}Setup failed. Please check the errors above and try again.{Colors.END}"
        )
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}Setup completed successfully! 🎉{Colors.END}")
        sys.exit(0)


if __name__ == "__main__":
    main()
