# 🚀 XBTMYR Trading Bot

An advanced cryptocurrency trading bot for the XBTMYR (Bitcoin to Malaysian Ringgit) trading pair on Luno exchange. This bot uses sophisticated technical analysis and risk management to automate trading decisions.

## ✨ Features

### 🔍 Technical Analysis
- **RSI (Relative Strength Index)** - Momentum oscillator for overbought/oversold conditions
- **EMA Cross Strategy** - 9/21 Exponential Moving Average crossover signals
- **MACD** - Moving Average Convergence Divergence for trend analysis
- **Bollinger Bands** - Volatility and price level analysis
- **Volume Analysis** - Confirms price movements with volume data
- **Support/Resistance Levels** - Key price levels from market analysis

### 💼 Risk Management
- **Position Sizing** - Configurable maximum position size (default: 2% of portfolio)
- **Stop Loss** - Automatic stop loss orders (default: 1.5%)
- **Take Profit** - Automatic profit taking (default: 3%)
- **Daily Trade Limits** - Maximum trades per day to prevent overtrading
- **Portfolio Protection** - Real-time balance monitoring

### 🌐 Web Dashboard
- **Real-time Monitoring** - Live price feeds and bot status
- **Interactive Charts** - Price movements and technical indicators
- **Trade History** - Complete log of all trades and decisions
- **Portfolio Overview** - Current balances and performance
- **Performance Analytics** - P&L tracking and statistics

### 🛡️ Safety Features
- **Dry Run Mode** - Test strategies without real money
- **API Security** - Secure credential management
- **Error Handling** - Robust error recovery and logging
- **Graceful Shutdown** - Clean exit with order cancellation

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- 2GB RAM minimum
- Stable internet connection
- Luno account with API access

### Python Dependencies
```
flask==2.3.3
plotly==5.17.0
numpy==1.24.3
pandas==2.0.3
requests==2.31.0
python-dotenv==1.0.0
schedule==1.2.0
websocket-client==1.6.4
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the trading bot files
cd trading-bot

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Setup environment
python run_bot.py --setup

# Edit the .env file with your credentials
nano .env
```

Add your Luno API credentials to the `.env` file:
```env
LUNO_API_KEY=your_api_key_here
LUNO_API_SECRET=your_api_secret_here
DRY_RUN=true
```

### 3. Run the Bot

#### Simulation Mode (Recommended for testing)
```bash
# Run bot with dashboard in simulation mode
python run_bot.py --dry-run

# Or run only the bot
python run_bot.py --bot-only --dry-run
```

#### Live Trading Mode (Use with caution!)
```bash
# Run bot with real trading
python run_bot.py --live
```

#### Dashboard Only
```bash
# Run only the web dashboard for monitoring
python run_bot.py --dashboard-only
```

## 🎛️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LUNO_API_KEY` | Your Luno API key | Required |
| `LUNO_API_SECRET` | Your Luno API secret | Required |
| `DRY_RUN` | Enable simulation mode | `true` |
| `MAX_POSITION_SIZE_PERCENT` | Max position size | `2.0` |
| `STOP_LOSS_PERCENT` | Stop loss percentage | `1.5` |
| `TAKE_PROFIT_PERCENT` | Take profit percentage | `3.0` |
| `MAX_DAILY_TRADES` | Maximum trades per day | `3` |
| `CHECK_INTERVAL` | Check interval in seconds | `60` |

### Command Line Options

```bash
python run_bot.py [OPTIONS]

Options:
  --bot-only              Run only the trading bot (no dashboard)
  --dashboard-only        Run only the web dashboard (no trading)
  --setup                 Setup environment and configuration files
  --dry-run              Run in simulation mode (no real trades)
  --live                 Run in live trading mode (real money!)
  --trading-pair PAIR    Trading pair (default: XBTMYR)
  --max-position-size %  Maximum position size percentage
  --stop-loss %          Stop loss percentage
  --take-profit %        Take profit percentage
  --check-interval SEC   Check interval in seconds
  --dashboard-host HOST  Dashboard host (default: 127.0.0.1)
  --dashboard-port PORT  Dashboard port (default: 5001)
```

## 📊 Trading Strategy

### Signal Generation

The bot uses a multi-factor approach to generate trading signals:

#### Buy Signals (All conditions must be met)
- Price breaks above resistance level with volume
- RSI not overbought (< 70)
- EMA bullish crossover (9 > 21)
- MACD bullish (MACD > Signal)
- Volume above average

#### Sell Signals (All conditions must be met)
- Price breaks below support level with volume
- RSI not oversold (> 30)
- EMA bearish crossover (9 < 21)
- MACD bearish (MACD < Signal)
- Volume above average

#### Wait Conditions
- Price in consolidation range (455,000 - 465,000 MYR)
- Low volume
- Mixed technical signals
- RSI in neutral zone

### Key Price Levels (Based on Analysis)

**Resistance Levels:**
- 463,000 MYR (Minor)
- 465,000 MYR (Key)
- 468,000 MYR (Strong)
- 475,000 MYR (Major)

**Support Levels:**
- 458,000 MYR (Minor)
- 455,000 MYR (Key)
- 453,000 MYR (Strong)
- 445,000 MYR (Major)

## 🌐 Web Dashboard

Access the dashboard at `http://localhost:5001` when running.

### Dashboard Features

1. **Bot Status** - Real-time bot status and configuration
2. **Current Market** - Live price and market metrics
3. **Portfolio** - Current balances and positions
4. **Recent Trades** - Trade history and performance
5. **Price Chart** - Interactive 7-day price chart with technical indicators

### Dashboard Screenshots

The dashboard provides:
- Real-time price monitoring
- Technical indicator visualization
- Trade execution logs
- Portfolio performance tracking
- Bot health monitoring

## 📁 File Structure

```
trading-bot/
├── config.py              # Configuration and settings
├── technical_analysis.py  # Technical analysis engine
├── luno_client.py         # Luno API client and portfolio management
├── trading_bot.py         # Main trading bot engine
├── web_dashboard.py       # Web dashboard application
├── run_bot.py             # Main launcher script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── README.md              # This file
└── templates/
    └── dashboard.html     # Dashboard HTML template
```

## 🔒 Security Best Practices

### API Security
- Store API credentials in environment variables only
- Never commit credentials to version control
- Use read-only API keys when possible
- Regularly rotate API keys

### Trading Security
- Always start with dry run mode
- Use small position sizes initially
- Set appropriate stop losses
- Monitor bot performance regularly

### System Security
- Keep Python and dependencies updated
- Use secure hosting environments
- Monitor system logs regularly
- Have emergency stop procedures

## 📈 Performance Monitoring

### Logging
The bot generates comprehensive logs in `trading_bot.log`:
- Trade executions
- Technical analysis results
- Error messages
- Performance metrics

### Reports
Performance reports are automatically generated as JSON files:
- Trade history
- P&L calculations
- Bot configuration
- Performance statistics

## ⚠️ Risk Warnings

### Financial Risks
- **Cryptocurrency trading involves substantial risk of loss**
- **Past performance does not guarantee future results**
- **Only trade with money you can afford to lose**
- **The bot is provided for educational purposes**

### Technical Risks
- Market conditions can change rapidly
- Technical analysis is not always accurate
- API outages can affect trading
- Software bugs may cause unexpected behavior

### Recommended Risk Management
- Start with simulation mode
- Use small position sizes (1-2%)
- Set conservative stop losses
- Monitor bot performance daily
- Have manual override capabilities

## 🐛 Troubleshooting

### Common Issues

#### Bot Won't Start
```bash
# Check API credentials
python -c "import os; print(os.getenv('LUNO_API_KEY'))"

# Check dependencies
pip install -r requirements.txt

# Check logs
tail -f trading_bot.log
```

#### Dashboard Not Loading
```bash
# Check if port is available
netstat -an | grep 5001

# Try different port
python run_bot.py --dashboard-port 5001
```

#### API Errors
- Verify API credentials
- Check Luno API status
- Ensure sufficient account permissions
- Check network connectivity

### Log Analysis
```bash
# View recent logs
tail -n 100 trading_bot.log

# Search for errors
grep ERROR trading_bot.log

# Monitor real-time
tail -f trading_bot.log
```

## 🔧 Development

### Adding New Indicators
1. Modify `technical_analysis.py`
2. Add indicator calculation method
3. Update signal generation logic
4. Test with dry run mode

### Customizing Strategy
1. Edit signal conditions in `TechnicalAnalyzer.generate_signals()`
2. Adjust confidence thresholds
3. Modify risk management parameters
4. Update configuration in `config.py`

### Dashboard Customization
1. Modify `templates/dashboard.html`
2. Add new API endpoints in `web_dashboard.py`
3. Update chart configurations
4. Add new monitoring widgets

## 📞 Support

### Getting Help
- Review this README thoroughly
- Check the log files for errors
- Test in dry run mode first
- Verify all configuration settings

### Disclaimer
This trading bot is provided as-is for educational and research purposes. The creators are not responsible for any financial losses incurred through its use. Always trade responsibly and within your risk tolerance.

## 📄 License

This software is provided for educational purposes only. Use at your own risk.

---

**Remember: Never invest more than you can afford to lose!** 🚨