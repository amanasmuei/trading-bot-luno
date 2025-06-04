# 🚀 Quick Start Guide - XBTMYR Trading Bot

## 30-Second Setup

1. **Setup Environment**
   ```bash
   cd trading-bot
   ./setup.sh
   ```

2. **Configure API Keys**
   ```bash
   nano .env
   # Add your Luno API credentials
   ```

3. **Test Installation**
   ```bash
   python3 test_bot.py
   ```

4. **Run Bot (Simulation)**
   ```bash
   python3 run_bot.py --dry-run
   ```

5. **View Dashboard**
   Open: http://localhost:5001

## Commands Reference

### Basic Commands
```bash
# Setup everything
./setup.sh

# Test installation
python3 test_bot.py

# Run in simulation mode
python3 run_bot.py --dry-run

# Run bot only (no dashboard)
python3 run_bot.py --bot-only --dry-run

# Run dashboard only
python3 run_bot.py --dashboard-only

# Live trading (REAL MONEY!)
python3 run_bot.py --live
```

### Configuration Commands
```bash
# Custom position size (1% instead of 2%)
python3 run_bot.py --dry-run --max-position-size 1.0

# Custom stop loss (2% instead of 1.5%)
python3 run_bot.py --dry-run --stop-loss 2.0

# Different trading pair
python3 run_bot.py --dry-run --trading-pair ETHZAR

# Custom dashboard port
python3 run_bot.py --dashboard-port 8080
```

## ⚠️ Safety Checklist

Before using live trading:

- [ ] ✅ Tested in dry-run mode
- [ ] ✅ Verified API credentials work
- [ ] ✅ Understood risk management settings
- [ ] ✅ Set small position sizes (1-2%)
- [ ] ✅ Monitored bot behavior for several days
- [ ] ✅ Have emergency stop procedure ready

## 🏆 Success Checklist

Your bot is working correctly if you see:

- [ ] ✅ Bot status shows "Running" in dashboard
- [ ] ✅ Current price updates every minute
- [ ] ✅ Technical indicators display properly
- [ ] ✅ No error messages in logs
- [ ] ✅ Portfolio shows correct balances (live mode)

## 🆘 Troubleshooting

### Bot Won't Start
```bash
# Check dependencies
pip3 install -r requirements.txt

# Check API credentials
grep LUNO_API .env

# Check logs
tail -f trading_bot.log
```

### Dashboard Not Loading
```bash
# Try different port
python3 run_bot.py --dashboard-port 5001

# Check if something is using port 5001
lsof -i :5001
```

### API Errors
1. Verify Luno API credentials
2. Check API permissions
3. Ensure account has sufficient balance
4. Check network connectivity

## 📊 Expected Behavior

### In Dry Run Mode
- Bot analyzes market every 60 seconds
- Shows "[DRY RUN]" prefix on all trades
- No real money transactions
- All signals and analysis work normally

### In Live Mode
- Same analysis as dry run
- Real API calls to Luno
- Actual trades executed
- Money at risk - use carefully!

## 📈 Performance Monitoring

### Key Metrics to Watch
- **Daily trades**: Should not exceed configured limit
- **Win rate**: Aim for >60% in backtesting
- **Risk per trade**: Never exceed 2% of portfolio
- **Drawdown**: Stop if exceeding 10% loss

### Files to Monitor
- `trading_bot.log` - All bot activity
- `trading_report_*.json` - Performance reports
- Dashboard at http://localhost:5001

## 🎯 Next Steps

1. **Week 1**: Run in dry mode, observe signals
2. **Week 2**: Start with tiny live positions (0.5%)
3. **Week 3**: Gradually increase if performing well
4. **Ongoing**: Monitor, adjust, improve

## 🔥 Pro Tips

- Start small and scale up slowly
- Monitor the bot daily for first month
- Keep detailed records of performance
- Don't override the bot's decisions emotionally
- Have a stop-loss plan for the entire bot
- Back up your configuration regularly

---

**Remember: This is your money at risk. Trade responsibly!** 💰⚠️