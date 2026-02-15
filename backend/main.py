"""
Main application entry point.
Connects to Pocket Option WebSocket and streams market data to Firebase Firestore.
"""
import asyncio
import logging
import signal
import sys
from services.pocket_option_service import PocketOptionService
from services.firebase_service import FirebaseService
from services.data_processor import DataProcessor
from health_server import HealthCheckServer
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class MarketDataService:
    """Main service orchestrator"""
    
    def __init__(self):
        """Initialize all services"""
        self.firebase_service = FirebaseService()
        self.data_processor = DataProcessor(self.firebase_service)
        self.pocket_option_service = PocketOptionService(
            on_market_data=self.handle_market_data
        )
        self.health_server = HealthCheckServer(
            self.pocket_option_service,
            self.firebase_service
        )
        self.is_running = False
    
    async def handle_market_data(self, data):
        """
        Handle incoming market data from Pocket Option.
        
        Args:
            data: Market data from Pocket Option WebSocket
        """
        try:
            # Process different types of market data
            if isinstance(data, dict):
                # Single pair update
                pair_id = data.get('id') or data.get('name')
                if pair_id:
                    await self.data_processor.process_pair_update(pair_id, data)
            
            elif isinstance(data, list):
                # Multiple pairs update
                for item in data:
                    pair_id = item.get('id') or item.get('name')
                    if pair_id:
                        await self.data_processor.process_pair_update(pair_id, item)
            
        except Exception as e:
            logger.error(f"Error handling market data: {e}")
    
    async def start(self):
        """Start all services"""
        try:
            logger.info("Starting Market Data Service...")
            
            # Start data processor
            self.data_processor.start()
            
            # Start health check server
            await self.health_server.start()
            
            # Connect to Pocket Option
            await self.pocket_option_service.connect()
            
            # Subscribe to all markets
            await self.pocket_option_service.subscribe_to_markets()
            
            self.is_running = True
            logger.info("Market Data Service started successfully")
            
            # Keep the service running
            while self.is_running:
                await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Error starting service: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop all services gracefully"""
        logger.info("Stopping Market Data Service...")
        self.is_running = False
        
        # Stop data processor
        await self.data_processor.stop()
        
        # Disconnect from Pocket Option
        await self.pocket_option_service.disconnect()
        
        # Stop health server
        await self.health_server.stop()
        
        logger.info("Market Data Service stopped")


# Global service instance
service = None


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig}, shutting down...")
    if service:
        asyncio.create_task(service.stop())


async def main():
    """Main entry point"""
    global service
    
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Create and start service
        service = MarketDataService()
        await service.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if service:
            await service.stop()


if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())
