# Luno Trading Bot - Docker Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory with proper permissions
RUN mkdir -p logs && chmod 755 logs

# Create logs directory and set permissions before switching user
RUN mkdir -p /app/logs /app/enhanced_reports && \
    useradd -m -u 1000 trader && \
    chown -R trader:trader /app

USER trader

# Expose dashboard port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Default command (dry run mode for safety)
CMD ["python", "scripts/run_bot.py", "--dry-run"]
