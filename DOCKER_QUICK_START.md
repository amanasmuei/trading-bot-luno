# Docker Quick Start - Enhanced Trading Bot

## Fix Docker Issue and Start Enhanced Bot

The Docker setup has been fixed. Here's how to use it:

### 1. Quick Start (Easiest)
```bash
# Run the automated setup
python docker-setup-enhanced.py

# Choose option A to build and start immediately
```

### 2. Manual Start
```bash
# Build the enhanced bot image
docker build -f Dockerfile.enhanced -t luno-enhanced-bot .

# Start just the enhanced bot
docker compose -f docker-compose.enhanced.yml up -d

# Or start with your original bot for comparison
docker compose -f docker-compose.enhanced.yml --profile original up -d
```

### 3. Check Status
```bash
# View running containers
docker compose -f docker-compose.enhanced.yml ps

# View logs
docker compose -f docker-compose.enhanced.yml logs -f

# Check health (after container starts)
curl http://localhost:5002/health
```

### 4. Access Points
- **Enhanced Bot**: http://localhost:5002/health
- **Original Bot** (if running): http://localhost:5001/health

### 5. Environment Setup
Make sure your `.env` file has:
```bash
LUNO_API_KEY=your_api_key_here
LUNO_API_SECRET=your_api_secret_here
TRADING_PAIR=XBTMYR
DRY_RUN=true
```

### 6. Management Commands
```bash
# Stop all
docker compose -f docker-compose.enhanced.yml down

# Restart
docker compose -f docker-compose.enhanced.yml restart

# Update after code changes
docker compose -f docker-compose.enhanced.yml build
docker compose -f docker-compose.enhanced.yml up -d
```

## Fixed Issues:
- ✅ Removed dependency on missing dashboard Dockerfile
- ✅ Added proper health check endpoints
- ✅ Simplified Docker Compose configuration
- ✅ Enhanced bot runs independently

## Safety Note:
The enhanced bot starts in DRY_RUN mode by default. Monitor performance before enabling live trading.
