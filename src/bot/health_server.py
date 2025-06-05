"""
Simple health check server for Docker containers
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple health check HTTP handler"""

    def __init__(self, *args, bot_status=None, **kwargs):
        self.bot_status = bot_status or {}
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            self.send_health_response()
        elif self.path == "/status":
            self.send_status_response()
        else:
            self.send_response(404)
            self.end_headers()

    def send_health_response(self):
        """Send basic health check response"""
        try:
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "enhanced-trading-bot",
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(health_data).encode())

        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.send_response(500)
            self.end_headers()

    def send_status_response(self):
        """Send detailed status response"""
        try:
            status_data = {
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "service": "enhanced-trading-bot",
                "bot_status": getattr(self, "bot_status", {}),
                "version": "Enhanced v2.0",
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(status_data, default=str).encode())

        except Exception as e:
            logger.error(f"Status check error: {e}")
            self.send_response(500)
            self.end_headers()

    def log_message(self, format, *args):
        """Override to suppress HTTP logs"""
        pass


class HealthCheckServer:
    """Health check server for Docker containers"""

    def __init__(self, port=5002, bot_status=None):
        self.port = port
        self.bot_status = bot_status or {}
        self.server = None
        self.thread = None
        self.running = False

    def start(self):
        """Start the health check server"""
        try:
            # Create handler with bot status
            handler = lambda *args, **kwargs: HealthCheckHandler(
                *args, bot_status=self.bot_status, **kwargs
            )

            self.server = HTTPServer(("0.0.0.0", self.port), handler)
            self.thread = threading.Thread(
                target=self.server.serve_forever, daemon=True
            )
            self.thread.start()
            self.running = True

            logger.info(f"Health check server started on port {self.port}")

        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")

    def stop(self):
        """Stop the health check server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            logger.info("Health check server stopped")

    def update_status(self, status_data):
        """Update bot status for health checks"""
        self.bot_status.update(status_data)
