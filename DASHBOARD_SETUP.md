# Enhanced Trading Bot Dashboard Setup

## Overview

The Enhanced Trading Bot now includes a comprehensive dashboard system with multiple components:

1. **Enhanced Trading Bot** - Runs on port 5002 (health check)
2. **Enhanced Dashboard** - Runs on port 5003 (Streamlit web interface)
3. **Original Bot** - Runs on port 5001 (optional, for comparison)

## Quick Start with Docker Compose

### 1. Start Enhanced Bot with Dashboard

```bash
# Start the enhanced bot and dashboard
docker-compose up -d

# View logs
docker-compose logs -f luno-enhanced-bot
docker-compose logs -f luno-dashboard
```

### 2. Access the Dashboard

- **Enhanced Dashboard**: http://localhost:5003
- **Bot Health Check**: http://localhost:5002/health
- **Dashboard Health Check**: http://localhost:8502/health

### 3. Start Original Bot (Optional)

```bash
# Start original bot for comparison
docker-compose --profile original up -d luno-original-bot
```

## Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
pip install streamlit plotly pandas numpy requests
```

### 2. Start Enhanced Bot

```bash
python -m src.bot.enhanced_trading_bot
```

### 3. Start Dashboard

```bash
streamlit run src/dashboard/enhanced_dashboard.py --server.port=5003
```

## Dashboard Features

### 🤖 Bot Status
- Real-time bot health monitoring
- Daily trade count and P&L
- Detailed bot status information

### 📊 Performance Metrics
- Total trades and win rate
- Total return and profit factor
- Performance tracking over time

### 💼 Recent Trades
- Latest trade executions
- Trade details including confidence and strength
- Historical trade analysis

### 📈 Trading Charts
- Performance over time
- Win rate trends
- Return analysis

## Troubleshooting

### Dashboard Not Loading

1. **Check Bot Status**:
   ```bash
   curl http://localhost:5002/health
   ```

2. **Check Dashboard Health**:
   ```bash
   curl http://localhost:8502/health
   ```

3. **View Container Logs**:
   ```bash
   docker-compose logs luno-enhanced-bot
   docker-compose logs luno-dashboard
   ```

### Port Conflicts

If you have port conflicts, you can modify the ports in `docker-compose.yml`:

```yaml
services:
  luno-enhanced-bot:
    ports:
      - "5002:5002"  # Change first number to different port
  
  luno-dashboard:
    ports:
      - "5003:5003"  # Change first number to different port
```

### No Trading Data

If the dashboard shows "No trading reports found":

1. The bot needs to run for some time to generate reports
2. Check if the `enhanced_reports` directory exists
3. Ensure the bot has proper API credentials in `.env`

## Configuration

### Environment Variables

Create a `.env` file with:

```env
LUNO_API_KEY=your_api_key_here
LUNO_API_SECRET=your_api_secret_here
TRADING_PAIR=XBTMYR
DRY_RUN=true
```

### Dashboard Settings

The dashboard automatically refreshes and connects to:
- Bot health server: `http://localhost:5002`
- Trading reports: `./enhanced_reports/`

## Docker Compose Services

### Enhanced Bot (`luno-enhanced-bot`)
- **Image**: Built from `Dockerfile.enhanced`
- **Port**: 5002 (health check)
- **Volumes**: logs, enhanced_reports, .env
- **Health Check**: HTTP GET to `/health`

### Dashboard (`luno-dashboard`)
- **Image**: Built from `Dockerfile.dashboard`
- **Port**: 5003 (web interface)
- **Volumes**: enhanced_reports (read-only), .env
- **Health Check**: HTTP GET to `/health` on port 8502
- **Depends On**: luno-enhanced-bot

### Original Bot (`luno-original-bot`)
- **Profile**: `original` (optional)
- **Port**: 5001
- **Use**: Comparison with enhanced strategy

## Monitoring

### Health Checks

All services include health checks:
- **Enhanced Bot**: `http://localhost:5002/health`
- **Dashboard**: `http://localhost:8502/health`
- **Original Bot**: `http://localhost:5001/health`

### Logs

View real-time logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f luno-enhanced-bot
docker-compose logs -f luno-dashboard
```

### Performance Reports

The enhanced bot generates detailed reports in `enhanced_reports/`:
- JSON format with comprehensive metrics
- Automatic generation after trading sessions
- Accessible through the dashboard

## Security Notes

- The dashboard runs in read-only mode for trading reports
- API credentials are mounted as read-only
- All services run as non-root users
- Health checks don't expose sensitive information

## Support

If you encounter issues:

1. Check the logs for error messages
2. Verify your `.env` file configuration
3. Ensure all required ports are available
4. Check Docker container status: `docker-compose ps`
