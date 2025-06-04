# 🚀 Super Easy Setup Guide

**Get your Luno Trading Bot running in under 5 minutes!**

## 🎯 Multiple Ways to Get Started

### Option 1: Universal Setup (All-in-One)
```bash
python setup.py        # All platforms
./setup.sh             # Linux/macOS
setup.bat              # Windows (double-click)
```
Choose from all available setup methods in one place!

### Option 2: One-Command Install (Easiest!)
```bash
python install.py
```
That's it! The installer will guide you through everything.

### Option 3: Interactive Launcher (Recommended)
```bash
python launcher.py
```
User-friendly menu interface - perfect for beginners!

### Option 4: Setup Wizard (Advanced)
```bash
python setup_wizard.py
```
Full-featured setup with detailed configuration options.

### Option 5: Docker Deployment (Production)
```bash
python docker_setup.py
```
Containerized deployment for production environments.

---

## 🏃‍♂️ Quick Start (30 seconds)

1. **Download the bot** (you've already done this!)

2. **Run the installer**:
   ```bash
   python install.py
   ```

3. **Follow the prompts** to:
   - Install dependencies automatically
   - Enter your Luno API credentials
   - Choose your trading preferences

4. **Start trading**:
   ```bash
   python launcher.py
   ```

5. **View your dashboard**: http://localhost:5001

**That's it! Your bot is running! 🎉**

---

## 📋 What You Need

### Before You Start
- **Python 3.8+** (check with `python --version`)
- **Luno Account** with API access
- **5 minutes** of your time

### Get Your API Credentials
1. Go to: https://www.luno.com/wallet/security/api_keys
2. Create a new API key with these permissions:
   - `Perm_R_Balance` (Read balance)
   - `Perm_W_Orders` (Place orders)
3. Copy your API Key and API Secret

---

## 🎮 Using the Launcher

The launcher gives you a simple menu:

```
🚀 LUNO TRADING BOT LAUNCHER
========================================

What would you like to do?
  1. 🔧 Setup/Configure Bot
  2. 🎮 Start Bot (Simulation Mode)
  3. 💰 Start Bot (Live Trading)
  4. 📊 Open Dashboard
  5. 📖 View Documentation
  6. 🧪 Test Configuration
  7. ❌ Exit
```

### First Time Users
1. Choose option **1** to set up your bot
2. Choose option **2** to start in simulation mode
3. Choose option **4** to view the dashboard

### Experienced Users
- Option **3** for live trading (real money!)
- Option **6** to test your configuration

---

## 🛡️ Safety Features

### Automatic Safety Checks
- ✅ **Dry run by default** - No real money at risk initially
- ✅ **API validation** - Checks your credentials before starting
- ✅ **Configuration validation** - Ensures everything is set up correctly
- ✅ **Multiple confirmations** - For live trading mode

### Built-in Protections
- 🔒 **Position size limits** (max 2% of portfolio per trade)
- 🔒 **Stop loss protection** (1.5% default)
- 🔒 **Daily trade limits** (max 3 trades per day)
- 🔒 **Drawdown protection** (stops at 10% loss)

---

## 🎯 Supported Trading Pairs

Choose from these popular pairs:
- **XBTMYR** - Bitcoin/Malaysian Ringgit
- **XBTZAR** - Bitcoin/South African Rand
- **XBTEUR** - Bitcoin/Euro
- **ETHMYR** - Ethereum/Malaysian Ringgit
- **ETHZAR** - Ethereum/South African Rand

*More pairs available in advanced configuration*

---

## 🚨 Troubleshooting

### "Python not found"
```bash
# Install Python 3.8+ from python.org
# Or use package manager:
brew install python3        # macOS
sudo apt install python3    # Ubuntu
```

### "API credentials invalid"
1. Double-check your API key and secret
2. Ensure API permissions are correct
3. Try regenerating your API credentials

### "Bot won't start"
```bash
# Test your configuration
python launcher.py
# Choose option 6 (Test Configuration)
```

### "Dashboard not loading"
- Check if something is using port 5001
- Try: http://127.0.0.1:5001 instead
- Restart the bot

---

## 💡 Pro Tips

### For Beginners
1. **Always start in simulation mode** - Test for at least a week
2. **Start small** - Use 1% position sizes initially
3. **Monitor daily** - Check the dashboard regularly
4. **Read the logs** - Understand what the bot is doing

### For Advanced Users
1. **Customize settings** - Edit .env file for fine-tuning
2. **Multiple pairs** - Run separate instances for different pairs
3. **Backtesting** - Analyze performance before going live
4. **Risk management** - Adjust stop losses based on volatility

---

## 📊 What to Expect

### In Simulation Mode
- 📈 **Real market analysis** - Same signals as live mode
- 🎮 **Fake trades** - No real money involved
- 📊 **Performance tracking** - See how you would have done
- 📝 **Full logging** - All activities recorded

### In Live Mode
- 💰 **Real trades** - Actual money at risk
- ⚡ **Instant execution** - Orders placed immediately
- 📊 **Real profits/losses** - Your account balance changes
- 🔔 **Notifications** - Important events logged

---

## 🎉 Success Checklist

Your bot is working correctly when you see:

- [ ] ✅ Setup completed without errors
- [ ] ✅ API credentials validated
- [ ] ✅ Bot starts in simulation mode
- [ ] ✅ Dashboard loads at http://localhost:5001
- [ ] ✅ Current price updates every minute
- [ ] ✅ Technical indicators display properly
- [ ] ✅ No error messages in logs

---

## 🆘 Need Help?

### Quick Fixes
```bash
# Reinstall dependencies
python install.py

# Reset configuration
rm .env
python setup_wizard.py

# Test everything
python launcher.py
# Choose option 6
```

### Documentation
- 📖 **README.md** - Main documentation
- 📖 **docs/QUICK_START.md** - Detailed quick start
- 📖 **docs/README.md** - Complete documentation

### Common Issues
1. **"Module not found"** → Run `python install.py`
2. **"API error"** → Check your Luno API credentials
3. **"Port in use"** → Something else is using port 5001
4. **"Permission denied"** → Check file permissions

---

## ⚠️ Important Disclaimers

- 🚨 **This bot involves financial risk** - Only use money you can afford to lose
- 🚨 **Start with simulation mode** - Test thoroughly before live trading
- 🚨 **Monitor regularly** - Don't leave the bot unattended for long periods
- 🚨 **Keep credentials secure** - Never share your API keys
- 🚨 **Understand the risks** - Cryptocurrency trading is highly volatile

---

## 🎯 Next Steps

1. **Complete setup** using one of the three methods above
2. **Run in simulation** for at least a week
3. **Monitor performance** and adjust settings
4. **Start live trading** with small amounts
5. **Scale up gradually** as you gain confidence

**Happy Trading! 🚀💰**
