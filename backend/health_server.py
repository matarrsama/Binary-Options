"""
Health check HTTP server for monitoring service status.
Runs alongside the main WebSocket service.
"""
import logging
from aiohttp import web
from config import Config

logger = logging.getLogger(__name__)


class HealthCheckServer:
    """Simple HTTP server for health checks"""
    
    def __init__(self, pocket_option_service, firebase_service):
        """
        Initialize health check server.
        
        Args:
            pocket_option_service: PocketOptionService instance
            firebase_service: FirebaseService instance
        """
        self.pocket_option_service = pocket_option_service
        self.firebase_service = firebase_service
        self.app = web.Application()
        self.runner = None
        
        # Set up routes
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/', self.root)
    
    async def health_check(self, request):
        """Health check endpoint"""
        try:
            # Check Pocket Option connection status
            po_status = "connected" if self.pocket_option_service.is_connected else "disconnected"
            
            # Check Firebase connection
            fb_status = "connected" if self.firebase_service.db else "disconnected"
            
            # Overall health
            is_healthy = self.pocket_option_service.is_connected and self.firebase_service.db
            
            response_data = {
                "status": "healthy" if is_healthy else "unhealthy",
                "services": {
                    "pocket_option": po_status,
                    "firebase": fb_status
                },
                "reconnect_attempts": self.pocket_option_service.reconnect_attempts
            }
            
            status_code = 200 if is_healthy else 503
            
            return web.json_response(response_data, status=status_code)
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return web.json_response(
                {"status": "error", "message": str(e)},
                status=500
            )
    
    async def root(self, request):
        """Root endpoint"""
        return web.json_response({
            "service": "Pocket Option Market Data Service",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health"
            }
        })
    
    async def start(self):
        """Start the health check server"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            site = web.TCPSite(self.runner, '0.0.0.0', Config.HEALTH_CHECK_PORT)
            await site.start()
            
            logger.info(f"Health check server started on port {Config.HEALTH_CHECK_PORT}")
            
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
            raise
    
    async def stop(self):
        """Stop the health check server"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Health check server stopped")
