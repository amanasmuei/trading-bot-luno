# Docker Usage Guide - Enhanced Trading Bot

## Quick Start

### Option 1: Use the Setup Script (Recommended)
```bash
# Run the automated setup
python docker-setup-enhanced.py

# Follow the prompts to set up everything automatically
```

### Option 2: Manual Setup

1. **Setup directories and environment**:
```bash
mkdir -p logs enhanced_reports monitoring/grafana
cp .env.example .env  # Edit with your API keys
```

2. **Start the enhanced bot**:
```bash
docker compose -f docker-compose.enhanced.yml up -d
```

## Available Configurations

### 1. Enhanced Bot Only (Recommended)
```bash
# Start just the enhanced trading bot
docker compose -f docker-compose.enhanced.yml up -d

# Access points:
# - Bot Dashboard: http://localhost:5002
# - Enhanced Dashboard: http://localhost:5003
```

### 2. Enhanced + Original (Comparison)
```bash
# Start both enhanced and original bots for comparison
docker compose -f docker-compose.enhanced.yml --profile original up -d

# Access points:
# - Enhanced Bot: http://localhost:5002
# - Original Bot: http://localhost:5001
# - Enhanced Dashboard: http://localhost:5003
```

### 3. With Redis Caching
```bash
# Start with Redis for improved performance
docker compose -f docker-compose.enhanced.yml --profile with-cache up -d
```

### 4. With Monitoring
```bash
# Start with Grafana monitoring
docker compose -f docker-compose.enhanced.yml --profile monitoring up -d

# Access Grafana: http://localhost:3000 (admin/admin123)
```

### 5. Full Setup (Everything)
```bash
# Start everything: enhanced bot, original bot, Redis, and monitoring
docker compose -f docker-compose.enhanced.yml \
  --profile original \
  --profile with-cache \
  --profile monitoring \
  up -d
```

## Management Commands

### View Logs
```bash
# All services
docker compose -f docker-compose.enhanced.yml logs -f

# Specific service
docker compose -f docker-compose.enhanced.yml logs -f luno-enhanced-bot
```

### Check Status
```bash
docker compose -f docker-compose.enhanced.yml ps
```

### Restart Services
```bash
# Restart all
docker compose -f docker-compose.enhanced.yml restart

# Restart specific service
docker compose -f docker-compose.enhanced.yml restart luno-enhanced-bot
```

### Stop Services
```bash
# Stop all services
docker compose -f docker-compose.enhanced.yml down

# Stop and remove volumes
docker compose -f docker-compose.enhanced.yml down -v
```

### Update and Rebuild
```bash
# Pull latest code and rebuild
git pull
docker compose -f docker-compose.enhanced.yml build
docker compose -f docker-compose.enhanced.yml up -d
```

## Environment Configuration

### Required Environment Variables
```bash
# In your .env file:
LUNO_API_KEY=your_api_key_here
LUNO_API_SECRET=your_api_secret_here
TRADING_PAIR=XBTMYR
```

### Enhanced Strategy Settings
```bash
# Strategy configuration
TRADING_STRATEGY=enhanced
BOT_MODE=enhanced
DRY_RUN=true  # Start safely in simulation mode

# Risk management
MAX_POSITION_SIZE_PERCENT=1.5
BASE_STOP_LOSS_PERCENT=3.0
MIN_RISK_REWARD_RATIO=1.5
MAX_DAILY_TRADES=5

# Confidence thresholds
MIN_CONFIDENCE_BUY=0.6
MIN_CONFIDENCE_SELL=0.6
```

## Troubleshooting

### Port Conflicts
If ports are already in use, modify the ports in `docker-compose.enhanced.yml`:
```yaml
ports:
  - "5004:5002"  # Change 5002 to 5004
```

### Permission Issues
```bash
# Fix log file permissions
sudo chown -R $USER:$USER logs enhanced_reports
```

### View Container Status
```bash
# Check if containers are running
docker ps

# Check container logs for errors
docker logs luno-enhanced-bot
```

### Reset Everything
```bash
# Stop and remove everything
docker compose -f docker-compose.enhanced.yml down -v
docker system prune -f

# Start fresh
python docker-setup-enhanced.py
```

## Migration from Existing Setup

### From Original Docker Compose
1. **Backup your current setup**:
```bash
cp docker-compose.yml docker-compose.yml.backup
cp .env .env.backup
```

2. **Keep original running** (if desired):
```bash
# Your existing bot continues on port 5001
docker compose up -d
```

3. **Start enhanced bot alongside**:
```bash
# Enhanced bot starts on port 5002
docker compose -f docker-compose.enhanced.yml up -d
```

4. **Compare performance** for a few days

5. **Switch completely** when satisfied:
```bash
# Stop original
docker compose down

# Use enhanced as primary
docker compose -f docker-compose.enhanced.yml up -d
```

## Performance Monitoring

### Check Logs
```bash
# Enhanced bot logs
tail -f logs/enhanced_trading_bot.log

# Container logs
docker compose -f docker-compose.enhanced.yml logs -f luno-enhanced-bot
```

### Performance Reports
Enhanced bot generates detailed reports in `enhanced_reports/` directory:
- Daily performance summaries
- Trade analysis
- Signal distribution
- Risk metrics

### Dashboard Access
- **Enhanced Bot**: http://localhost:5002
- **Enhanced Dashboard**: http://localhost:5003  
- **Grafana Monitoring**: http://localhost:3000

## Safety Tips

1. **Always start in DRY_RUN mode**
2. **Test with small amounts first**
3. **Monitor logs regularly**
4. **Keep API keys secure**
5. **Regular backups of configuration**

## Support

If you encounter issues:
1. Check logs for error messages
2. Verify environment variables
3. Ensure API keys are correct
4. Check port availability
5. Review the main documentation

The enhanced strategy should provide better performance than the original while maintaining safety through improved risk management.
