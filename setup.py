#!/usr/bin/env python3
"""
🚀 Luno Trading Bot - Universal Setup
====================================

The ultimate setup script that gives you all options:
- Quick install
- Interactive launcher
- Docker deployment
- Traditional setup

Choose your preferred method!
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
    """Print the main header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("🚀 LUNO TRADING BOT - UNIVERSAL SETUP")
    print("=" * 60)
    print(f"{Colors.END}")
    print(f"{Colors.WHITE}Welcome! Choose your preferred setup method:{Colors.END}")
    print()


def show_setup_options():
    """Show all available setup options"""
    print(f"{Colors.YELLOW}📦 SETUP OPTIONS:{Colors.END}")
    print()

    print(f"{Colors.GREEN}1. 🚀 Quick Install (Recommended for beginners){Colors.END}")
    print(f"   • One-command setup")
    print(f"   • Automatic dependency installation")
    print(f"   • Guided configuration")
    print(f"   • Ready to use in 5 minutes")
    print()

    print(f"{Colors.BLUE}2. 🎮 Interactive Launcher (Best user experience){Colors.END}")
    print(f"   • User-friendly menu interface")
    print(f"   • Easy bot management")
    print(f"   • Built-in testing and validation")
    print(f"   • Perfect for daily use")
    print()

    print(f"{Colors.PURPLE}3. 🧙‍♂️ Setup Wizard (Advanced configuration){Colors.END}")
    print(f"   • Detailed configuration options")
    print(f"   • API validation")
    print(f"   • Custom trading parameters")
    print(f"   • Full control over settings")
    print()

    print(f"{Colors.CYAN}4. 🐳 Docker Deployment (Production ready){Colors.END}")
    print(f"   • Containerized deployment")
    print(f"   • Easy scaling and management")
    print(f"   • Perfect for cloud deployment")
    print(f"   • Isolated environment")
    print()

    print(f"{Colors.WHITE}5. 🛠️  Traditional Setup (Manual control){Colors.END}")
    print(f"   • Step-by-step manual setup")
    print(f"   • Full control over each step")
    print(f"   • Educational approach")
    print(f"   • For experienced users")
    print()

    print(f"{Colors.YELLOW}6. 📖 View Documentation{Colors.END}")
    print(f"7. ❌ Exit")
    print()


def run_quick_install():
    """Run the quick installer"""
    print(f"\n{Colors.GREEN}🚀 Running Quick Install...{Colors.END}")

    installer = Path("install.py")
    if not installer.exists():
        print(f"{Colors.RED}❌ Quick installer not found{Colors.END}")
        return False

    try:
        subprocess.run([sys.executable, str(installer)], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Quick install failed{Colors.END}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Install cancelled{Colors.END}")
        return False


def run_launcher():
    """Run the interactive launcher"""
    print(f"\n{Colors.BLUE}🎮 Starting Interactive Launcher...{Colors.END}")

    launcher = Path("launcher.py")
    if not launcher.exists():
        print(f"{Colors.RED}❌ Launcher not found{Colors.END}")
        return False

    try:
        subprocess.run([sys.executable, str(launcher)], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Launcher failed{Colors.END}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Launcher cancelled{Colors.END}")
        return False


def run_setup_wizard():
    """Run the setup wizard"""
    print(f"\n{Colors.PURPLE}🧙‍♂️ Starting Setup Wizard...{Colors.END}")

    wizard = Path("setup_wizard.py")
    if not wizard.exists():
        print(f"{Colors.RED}❌ Setup wizard not found{Colors.END}")
        return False

    try:
        subprocess.run([sys.executable, str(wizard)], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Setup wizard failed{Colors.END}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Setup cancelled{Colors.END}")
        return False


def run_docker_setup():
    """Run Docker setup"""
    print(f"\n{Colors.CYAN}🐳 Starting Docker Setup...{Colors.END}")

    docker_setup = Path("docker_setup.py")
    if not docker_setup.exists():
        print(f"{Colors.RED}❌ Docker setup not found{Colors.END}")
        return False

    try:
        subprocess.run([sys.executable, str(docker_setup)], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}❌ Docker setup failed{Colors.END}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Docker setup cancelled{Colors.END}")
        return False


def run_traditional_setup():
    """Run traditional setup"""
    print(f"\n{Colors.WHITE}🛠️  Traditional Setup Instructions:{Colors.END}")
    print()
    print(f"{Colors.YELLOW}Step 1: Install Dependencies{Colors.END}")
    print(f"   ./scripts/setup.sh")
    print()
    print(f"{Colors.YELLOW}Step 2: Configure API Keys{Colors.END}")
    print(f"   cp .env.example .env")
    print(f"   # Edit .env with your Luno API credentials")
    print()
    print(f"{Colors.YELLOW}Step 3: Test Installation{Colors.END}")
    print(f"   python tests/test_bot.py")
    print()
    print(f"{Colors.YELLOW}Step 4: Run Bot{Colors.END}")
    print(f"   python scripts/run_bot.py --dry-run")
    print()
    print(f"{Colors.YELLOW}Step 5: View Dashboard{Colors.END}")
    print(f"   Open: http://localhost:5001")
    print()

    choice = input(
        f"{Colors.WHITE}Would you like to run the setup script now? (y/n): {Colors.END}"
    ).lower()
    if choice in ["y", "yes"]:
        setup_script = Path("scripts/setup.sh")
        if setup_script.exists():
            try:
                subprocess.run(["bash", str(setup_script)], check=True)
                return True
            except subprocess.CalledProcessError:
                print(f"{Colors.RED}❌ Setup script failed{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Setup script not found{Colors.END}")
            return False

    return True


def show_documentation():
    """Show documentation information"""
    print(f"\n{Colors.YELLOW}📖 Available Documentation:{Colors.END}")
    print()
    print(f"{Colors.GREEN}Quick Start:{Colors.END}")
    print(f"   • EASY_SETUP.md - Super easy setup guide")
    print(f"   • docs/QUICK_START.md - Traditional quick start")
    print()
    print(f"{Colors.BLUE}Detailed Documentation:{Colors.END}")
    print(f"   • README.md - Main documentation")
    print(f"   • docs/README.md - Complete documentation")
    print()
    print(f"{Colors.PURPLE}Configuration:{Colors.END}")
    print(f"   • .env.example - Configuration template")
    print(f"   • src/config/settings.py - Advanced settings")
    print()
    print(f"{Colors.CYAN}Testing:{Colors.END}")
    print(f"   • tests/test_bot.py - Bot functionality tests")
    print(f"   • tests/test_api_credentials.py - API tests")
    print()


def main():
    """Main setup function"""
    print_header()

    while True:
        show_setup_options()

        try:
            choice = input(
                f"{Colors.WHITE}Enter your choice (1-7): {Colors.END}"
            ).strip()

            if choice == "1":
                if run_quick_install():
                    print(f"\n{Colors.GREEN}🎉 Quick install completed!{Colors.END}")
                    print(
                        f"{Colors.CYAN}💡 You can now use: python launcher.py{Colors.END}"
                    )

            elif choice == "2":
                run_launcher()

            elif choice == "3":
                if run_setup_wizard():
                    print(f"\n{Colors.GREEN}🎉 Setup wizard completed!{Colors.END}")

            elif choice == "4":
                run_docker_setup()

            elif choice == "5":
                run_traditional_setup()

            elif choice == "6":
                show_documentation()

            elif choice == "7":
                print(f"\n{Colors.GREEN}👋 Happy trading! 🚀💰{Colors.END}")
                break

            else:
                print(
                    f"{Colors.YELLOW}⚠️  Invalid choice. Please enter 1-7.{Colors.END}"
                )

        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}👋 Goodbye!{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")


if __name__ == "__main__":
    main()
