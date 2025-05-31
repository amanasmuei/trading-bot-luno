#!/usr/bin/env python3
"""
🚀 Luno Trading Bot - One-Command Installer
==========================================

Super simple installer that sets up everything with one command:
python install.py

This is the easiest way to get started with the Luno Trading Bot!
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """One-command installer"""
    print("🚀 Luno Trading Bot - One-Command Installer")
    print("=" * 50)
    print()
    print("This will install and configure your trading bot in 3 easy steps:")
    print("1. Install dependencies")
    print("2. Configure your API credentials")
    print("3. Set up your trading preferences")
    print()
    
    # Check if setup wizard exists
    setup_wizard = Path(__file__).parent / "setup_wizard.py"
    if not setup_wizard.exists():
        print("❌ Setup wizard not found. Please ensure setup_wizard.py is in the same directory.")
        sys.exit(1)
    
    # Run the setup wizard
    try:
        result = subprocess.run([sys.executable, str(setup_wizard)], check=True)
        print("\n🎉 Installation completed successfully!")
        print("Your trading bot is ready to use!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed with error code: {e.returncode}")
        print("Please check the error messages above and try again.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Installation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
