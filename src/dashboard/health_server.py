"""
Simple health check server for the dashboard
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DashboardHealthHandler(BaseHTTPRequestHandler):
    """Health check handler for dashboard"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            self.send_health_response()
        else:
            self.send_response(404)
            self.end_headers()

    def send_health_response(self):
        """Send health check response"""
        try:
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "enhanced-dashboard",
                "version": "1.0",
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(health_data).encode())

        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.send_response(500)
            self.end_headers()

    def log_message(self, format, *args):
        """Override to suppress HTTP logs"""
        pass


class DashboardHealthServer:
    """Health check server for dashboard"""

    def __init__(self, port=8501):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False

    def start(self):
        """Start the health check server"""
        try:
            self.server = HTTPServer(("0.0.0.0", self.port), DashboardHealthHandler)
            self.thread = threading.Thread(
                target=self.server.serve_forever, daemon=True
            )
            self.thread.start()
            self.running = True

            logger.info(f"Dashboard health check server started on port {self.port}")

        except Exception as e:
            logger.error(f"Failed to start dashboard health check server: {e}")

    def stop(self):
        """Stop the health check server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            logger.info("Dashboard health check server stopped")


if __name__ == "__main__":
    # Start health server for testing
    server = DashboardHealthServer(port=8502)
    server.start()

    try:
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
