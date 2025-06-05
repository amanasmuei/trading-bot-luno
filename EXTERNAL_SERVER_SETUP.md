# External Server Dashboard Setup Guide

## Problem
The dashboard was not accessible from external servers because it was binding to `127.0.0.1` (localhost only) instead of `0.0.0.0` (all interfaces).

## ✅ Fixed Solutions

### 1. **Default Host Binding Fixed**
The dashboard now binds to `0.0.0.0` by default, allowing external access.

### 2. **Container Communication Fixed**
The dashboard can now properly connect to the bot in different deployment scenarios:
- **Docker Compose**: Uses container names for communication
- **Separate containers**: Uses environment variables
- **Local development**: Falls back to localhost

### 3. **Environment Variable Configuration**
You can now control both dashboard and bot connection via environment variables:

```bash
# In your .env file
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=5003
BOT_HOST=localhost  # or container name in Docker
BOT_PORT=5002
```

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended)
```bash
# Fix permissions first (important for external servers)
./fix_permissions.sh

# Start the enhanced bot with dashboard
docker-compose up -d

# Check logs
docker-compose logs -f luno-dashboard
docker-compose logs -f luno-enhanced-bot
```

**Access URLs:**
- Dashboard: `http://YOUR_SERVER_IP:5003`
- Bot Health: `http://YOUR_SERVER_IP:5002/health`

### Option 2: Manual Docker Run
```bash
# Build the image
docker build -t trading-bot .

# Run the enhanced bot
docker run -d --name trading-bot \
  --env-file .env \
  -p 5002:5002 \
  trading-bot python -m src.bot.enhanced_trading_bot

# Build dashboard image
docker build -f Dockerfile.dashboard -t trading-dashboard .

# Run the dashboard
docker run -d --name trading-dashboard \
  --env-file .env \
  -p 5003:5003 \
  trading-dashboard
```

### Option 3: Python Direct Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run enhanced bot
python -m src.bot.enhanced_trading_bot &

# Run dashboard
python run_enhanced_dashboard.py
```

## 🔧 Firewall Configuration

### Ubuntu/Debian
```bash
# Allow dashboard port
sudo ufw allow 5003/tcp
sudo ufw allow 5002/tcp

# Check status
sudo ufw status
```

### CentOS/RHEL
```bash
# Allow dashboard port
sudo firewall-cmd --permanent --add-port=5003/tcp
sudo firewall-cmd --permanent --add-port=5002/tcp
sudo firewall-cmd --reload
```

### Cloud Provider Security Groups
Make sure to open ports 5002 and 5003 in your cloud provider's security groups:
- **AWS**: EC2 Security Groups
- **Google Cloud**: VPC Firewall Rules
- **Azure**: Network Security Groups
- **DigitalOcean**: Cloud Firewalls

## 🔍 Troubleshooting

### 1. Check if Dashboard is Running
```bash
# Check if port is listening
netstat -tlnp | grep :5003
# or
ss -tlnp | grep :5003
```

### 2. Check Docker Container Status
```bash
# List running containers
docker ps

# Check container logs
docker logs luno-dashboard
docker logs luno-enhanced-bot
```

### 3. Test Local Access First
```bash
# Test from the server itself
curl http://localhost:5003/health
curl http://localhost:5002/health
```

### 4. Test External Access
```bash
# From another machine
curl http://YOUR_SERVER_IP:5003/health
```

## 📊 Dashboard Features

Once accessible, the dashboard provides:

1. **Real-time Bot Status**
   - Running/Stopped status
   - Configuration display
   - Mode toggle (Simulation/Live)

2. **Market Data**
   - Current BTC/MYR price
   - Bid/Ask spreads
   - 24h volume

3. **Portfolio Tracking**
   - Current balances
   - Portfolio value

4. **Trading History**
   - Recent trades
   - Performance metrics

5. **TradingView Charts**
   - Interactive price charts
   - Technical indicators
   - Multiple timeframes

## 🔐 Security Considerations

### 1. Use Reverse Proxy (Recommended)
```nginx
# Nginx configuration
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Enable HTTPS
```bash
# Using Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

### 3. Basic Authentication
Add basic auth to your reverse proxy or use environment variables:
```bash
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your_secure_password
```

## 📝 Environment Variables Reference

```bash
# API Configuration
LUNO_API_KEY=your_api_key
LUNO_API_SECRET=your_api_secret

# Trading Configuration
TRADING_PAIR=XBTMYR
DRY_RUN=true

# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=5003

# Bot Configuration
BOT_CHECK_INTERVAL=30
```

## 🆘 Common Issues

### Issue: "Connection Refused"
**Solution:** Check if the dashboard is actually running and bound to 0.0.0.0

### Issue: "Timeout"
**Solution:** Check firewall rules and security groups

### Issue: "Dashboard Shows No Data"
**Solution:** Ensure the trading bot is running and accessible on port 5002

### Issue: "Permission Denied" for Log Files
**Problem:** You see warnings like:
```
⚠️  Warning: Cannot write to log file: [Errno 13] Permission denied: '/app/logs/trading_bot.log'
```

**Solution:** Run the permission fix script before starting containers:
```bash
./fix_permissions.sh
docker-compose down
docker-compose up -d
```

### Issue: "Permission Denied" for Ports
**Solution:** Check if ports are available and not used by other services

## 📞 Support

If you continue to have issues:
1. Check the container logs: `docker logs luno-dashboard`
2. Verify network connectivity: `telnet YOUR_SERVER_IP 5003`
3. Ensure all environment variables are set correctly
4. Check if other services are using the same ports
