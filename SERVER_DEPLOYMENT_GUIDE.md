# 🚀 Enhanced Trading Bot Server Deployment Guide

This guide helps you deploy the Enhanced Trading Bot on a server with proper IP configuration for external access.

## 📋 Quick Fix for Health Check URL Issue

If you're seeing `http://localhost:5003/health` in your dashboard instead of your server's IP, follow these steps:

### 1. Set Environment Variables

Create or update your `.env` file with proper server configuration:

```bash
# Copy the example file
cp .env.server.example .env

# Edit with your server details
nano .env
```

**Required changes in `.env`:**
```env
# Your server's public IP address
SERVER_IP=YOUR_ACTUAL_SERVER_IP

# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=5003

# Bot Configuration  
BOT_HOST=localhost
BOT_PORT=5002
```

### 2. Restart the Dashboard

After updating the environment variables:

```bash
# If running directly
python run_enhanced_dashboard.py

# If running with Docker
docker-compose -f docker-compose.enhanced.yml restart luno-dashboard
```

### 3. Verify the Fix

The dashboard sidebar should now show:
- **Health Check:** `http://YOUR_SERVER_IP:5003/health`
- **Bot Health Check:** `http://localhost:5002/health`

---

## 🏗️ Complete Server Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.9+
- Docker & Docker Compose (optional but recommended)
- Open ports: 5002 (bot), 5003 (dashboard)

### Deployment Options

#### Option 1: Docker Deployment (Recommended)

1. **Clone and Setup**
```bash
git clone <your-repo-url>
cd xbtmyr-trading-bot

# Copy and configure environment
cp .env.server.example .env
nano .env  # Update with your details
```

2. **Build and Run**
```bash
# Build and start services
docker-compose -f docker-compose.enhanced.yml up -d

# Check status
docker-compose -f docker-compose.enhanced.yml ps
```

3. **Access Dashboard**
```bash
# Your dashboard will be available at:
http://YOUR_SERVER_IP:5003
```

#### Option 2: Direct Python Deployment

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.server.example .env
nano .env  # Update with your server IP and credentials
```

3. **Run Services**
```bash
# Terminal 1: Start the trading bot
python -m src.bot.enhanced_trading_bot

# Terminal 2: Start the dashboard
python run_enhanced_dashboard.py
```

### Firewall Configuration

**Ubuntu/Debian:**
```bash
# Allow dashboard access
sudo ufw allow 5003/tcp

# Allow bot API access (optional, for external monitoring)
sudo ufw allow 5002/tcp

# Enable firewall
sudo ufw enable
```

**CentOS/RHEL:**
```bash
# Allow dashboard access
sudo firewall-cmd --permanent --add-port=5003/tcp

# Allow bot API access (optional)
sudo firewall-cmd --permanent --add-port=5002/tcp

# Reload firewall
sudo firewall-cmd --reload
```

### Cloud Provider Specific Setup

#### AWS EC2

1. **Security Group Rules:**
   - Add inbound rule: Port 5003, Source: 0.0.0.0/0 (or restrict to your IP)
   - Add inbound rule: Port 5002, Source: Security Group ID (internal only)

2. **Get Public IP:**
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

#### DigitalOcean Droplet

1. **Firewall (if enabled):**
```bash
# Allow dashboard
sudo ufw allow 5003

# Check droplet IP
curl -4 icanhazip.com
```

#### Google Cloud Platform

1. **Firewall Rules:**
```bash
# Create firewall rule for dashboard
gcloud compute firewall-rules create allow-trading-dashboard \
    --allow tcp:5003 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow trading bot dashboard"
```

### Reverse Proxy Setup (Production)

For production deployments, use nginx or Apache as a reverse proxy:

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/trading-bot
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://localhost:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/HTTPS Setup (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d YOUR_DOMAIN

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Monitoring and Logs

#### Check Service Status
```bash
# Docker deployment
docker-compose -f docker-compose.enhanced.yml logs -f

# Direct deployment
tail -f logs/enhanced_trading_bot.log
```

#### Health Checks
```bash
# Check bot health
curl http://localhost:5002/health

# Check dashboard health
curl http://localhost:5003/health
```

### Troubleshooting

#### Common Issues

1. **"Connection refused" errors:**
   - Check if services are running: `docker ps` or `ps aux | grep python`
   - Verify ports are open: `netstat -tlnp | grep :5003`

2. **Still seeing localhost URLs:**
   - Verify `.env` file has correct `DASHBOARD_HOST=0.0.0.0`
   - Restart the dashboard service
   - Clear browser cache

3. **Bot can't connect to dashboard:**
   - Check `BOT_HOST` and `BOT_PORT` in `.env`
   - Ensure both services are on same network (Docker)

4. **External access not working:**
   - Check firewall rules
   - Verify cloud provider security groups
   - Confirm server IP is public, not private

#### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SERVER_IP` | Your server's public IP | `203.0.113.1` |
| `DASHBOARD_HOST` | Dashboard bind address | `0.0.0.0` |
| `DASHBOARD_PORT` | Dashboard port | `5003` |
| `BOT_HOST` | Bot hostname/IP | `localhost` |
| `BOT_PORT` | Bot API port | `5002` |
| `DOCKER_ENV` | Running in Docker | `true`/`false` |

### Security Best Practices

1. **API Keys:**
   - Use environment variables, never hardcode
   - Rotate keys regularly
   - Use read-only keys when possible

2. **Network Security:**
   - Restrict dashboard access to known IPs
   - Use VPN for administrative access
   - Keep bot API internal-only

3. **System Security:**
   - Keep system updated: `sudo apt update && sudo apt upgrade`
   - Use fail2ban: `sudo apt install fail2ban`
   - Regular backups of trading data and logs

4. **Monitoring:**
   - Set up alerts for bot downtime
   - Monitor resource usage
   - Log all trading activities

### Performance Optimization

1. **Resource Allocation:**
   - Minimum 1GB RAM, 1 CPU core
   - SSD storage recommended
   - Monitor disk space for logs

2. **Network:**
   - Low latency connection to trading APIs
   - Stable internet connection
   - Consider using a CDN for dashboard assets

---

## 🆘 Support

If you encounter issues:

1. Check the logs first
2. Verify environment variables
3. Test network connectivity
4. Review firewall settings

For additional help, create an issue with:
- Your deployment method (Docker/Direct)
- Error messages and logs
- System information
- Network configuration

---

**Happy Trading! 📈**
