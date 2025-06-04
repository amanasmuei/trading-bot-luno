# 🤖 Luno Trading Bot - Professional Automated Trading Platform

[![GitHub stars](https://img.shields.io/github/stars/amanasmuei/trading-bot-luno?style=social)](https://github.com/amanasmuei/trading-bot-luno/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/amanasmuei/trading-bot-luno?style=social)](https://github.com/amanasmuei/trading-bot-luno/network)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/amanasmuei/trading-bot-luno)](https://github.com/amanasmuei/trading-bot-luno/issues)

> **Enterprise-grade automated trading bot for Luno cryptocurrency exchange**
> Advanced algorithms • Institutional-level risk management • Real-time market analysis

**🌟 Professional Features:**

- ✅ **15+ Trading Pairs** - Multi-currency support across major cryptocurrencies
- ✅ **Advanced Risk Management** - Bank-level security and position controls
- ✅ **Real-Time Analytics** - Live monitoring and performance tracking
- ✅ **100% Free & Open Source** - No subscription fees or hidden costs
- ✅ **Easy 5-Minute Setup** - Professional tools made simple

---

## 🌐 **[Live Demo & Documentation](https://amanasmuei.github.io/trading-bot-luno/)**

**Experience the power of professional trading automation:**

- 📊 [Interactive Dashboard Demo](https://amanasmuei.github.io/trading-bot-luno/dashboard-demo.html)
- 📖 [Complete Documentation](https://amanasmuei.github.io/trading-bot-luno/documentation.html)
- ⚡ [Quick Setup Guide](https://amanasmuei.github.io/trading-bot-luno/setup.html)

---

## 🪙 Supported Trading Pairs

### Bitcoin (XBT)
- **XBTMYR** - Bitcoin/Malaysian Ringgit
- **XBTZAR** - Bitcoin/South African Rand
- **XBTEUR** - Bitcoin/Euro
- **XBTGBP** - Bitcoin/British Pound
- **XBTNGN** - Bitcoin/Nigerian Naira
- **XBTUGX** - Bitcoin/Ugandan Shilling

### Ethereum (ETH)
- **ETHMYR** - Ethereum/Malaysian Ringgit
- **ETHZAR** - Ethereum/South African Rand
- **ETHXBT** - Ethereum/Bitcoin

### Litecoin (LTC)
- **LTCMYR** - Litecoin/Malaysian Ringgit
- **LTCZAR** - Litecoin/South African Rand
- **LTCXBT** - Litecoin/Bitcoin

### Bitcoin Cash (BCH)
- **BCHMYR** - Bitcoin Cash/Malaysian Ringgit
- **BCHZAR** - Bitcoin Cash/South African Rand
- **BCHXBT** - Bitcoin Cash/Bitcoin

## 📁 Project Structure

```text
luno-trading-bot/
├── src/                    # Main source code
│   ├── bot/               # Core trading bot logic
│   │   ├── trading_bot.py
│   │   └── technical_analysis.py
│   ├── api/               # API clients
│   │   └── luno_client.py
│   ├── web/               # Web dashboard
│   │   ├── dashboard.py
│   │   └── templates/
│   │       └── dashboard.html
│   └── config/            # Configuration
│       └── settings.py
├── tests/                 # Test files
│   ├── test_api_credentials.py
│   └── test_bot.py
├── scripts/               # Utility scripts
│   ├── run_bot.py
│   └── setup.sh
├── docs/                  # Documentation
│   ├── README.md
│   └── QUICK_START.md
├── logs/                  # Log files (gitignored)
├── requirements.txt
└── .env.example
```

## 🚀 Super Easy Setup (New!)

**Get started in under 5 minutes with our new easy setup tools:**

### Option 1: One-Command Install (Easiest!)
```bash
python install.py
```

### Option 2: Interactive Launcher (Recommended)
```bash
python launcher.py
```

### Option 3: Setup Wizard (Advanced)
```bash
python setup_wizard.py
```

**📖 For detailed instructions, see [EASY_SETUP.md](EASY_SETUP.md)**

---

## 🚀 Traditional Quick Start

1. **Setup Environment**
   ```bash
   ./scripts/setup.sh
   ```

2. **Configure API Keys**
   ```bash
   cp .env.example .env
   # Edit .env with your Luno API credentials
   ```

3. **Test Installation**
   ```bash
   python tests/test_bot.py
   ```

4. **Run Bot (Simulation)**
   ```bash
   # Default (XBTMYR)
   python scripts/run_bot.py --dry-run

   # Specify trading pair
   python scripts/run_bot.py --dry-run --trading-pair ETHZAR
   python scripts/run_bot.py --dry-run --trading-pair XBTEUR
   ```

5. **View Dashboard**
   Open: <http://localhost:5001>

## 📖 Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [Full Documentation](docs/README.md)

## 🛠️ Development

The project follows a clean, modular structure:

- **src/bot/**: Core trading logic and technical analysis
- **src/api/**: External API integrations (Luno)
- **src/web/**: Web dashboard for monitoring
- **src/config/**: Configuration management
- **tests/**: Comprehensive test suite
- **scripts/**: Utility scripts for running the bot

## 🔧 Configuration

All configuration is managed through environment variables and the `src/config/settings.py` file.

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
python tests/test_bot.py
python tests/test_api_credentials.py
```

## 📊 Features

- Advanced technical analysis
- Real-time web dashboard
- Risk management
- Dry-run simulation mode
- Comprehensive logging
- Clean, modular architecture

## ⚠️ Disclaimer

This bot is for educational purposes. Use at your own risk when trading with real money.
