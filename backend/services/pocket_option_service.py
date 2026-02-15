"""
Pocket Option service for managing WebSocket connection and market data.
"""
import logging
import asyncio
from typing import Optional, Callable
from pocketoptionapi.stable_api import PocketOption
from config import Config

logger = logging.getLogger(__name__)


class PocketOptionService:
    """Manages connection to Pocket Option and market data streaming"""
    
    def __init__(self, on_market_data: Optional[Callable] = None):
        """
        Initialize Pocket Option service.
        
        Args:
            on_market_data: Callback function for market data updates
        """
        self.api: Optional[PocketOption] = None
        self.on_market_data = on_market_data
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = Config.MAX_RECONNECT_ATTEMPTS
        self.reconnect_delay = Config.RECONNECT_DELAY_SECONDS
    
    async def connect(self):
        """Connect to Pocket Option WebSocket"""
        try:
            logger.info("Connecting to Pocket Option...")
            
            # Initialize PocketOption API with SSID token
            self.api = PocketOption(ssid=Config.POCKET_OPTION_SSID)
            
            # Connect to WebSocket
            await self.api.connect()
            
            # Set up event handlers
            self._setup_event_handlers()
            
            self.is_connected = True
            self.reconnect_attempts = 0
            logger.info("Successfully connected to Pocket Option")
            
        except Exception as e:
            logger.error(f"Failed to connect to Pocket Option: {e}")
            await self._handle_reconnection()
    
    def _setup_event_handlers(self):
        """Set up event handlers for WebSocket events"""
        if not self.api:
            return
        
        # Handle connection events
        @self.api.on("connect")
        def on_connect():
            logger.info("WebSocket connected")
            self.is_connected = True
        
        @self.api.on("disconnect")
        def on_disconnect():
            logger.warning("WebSocket disconnected")
            self.is_connected = False
            asyncio.create_task(self._handle_reconnection())
        
        @self.api.on("error")
        def on_error(error):
            logger.error(f"WebSocket error: {error}")
        
        # Handle market data updates
        @self.api.on("quotes")
        async def on_quotes(data):
            """Handle real-time price quotes"""
            if self.on_market_data:
                await self.on_market_data(data)
        
        @self.api.on("assets")
        async def on_assets(data):
            """Handle asset list updates"""
            logger.debug(f"Received assets update: {len(data)} assets")
            if self.on_market_data:
                await self.on_market_data(data)
    
    async def subscribe_to_markets(self):
        """Subscribe to all available market pairs"""
        try:
            if not self.api or not self.is_connected:
                logger.warning("Cannot subscribe: not connected")
                return
            
            # Get all available assets
            assets = await self.api.get_all_assets()
            logger.info(f"Found {len(assets)} available assets")
            
            # Subscribe to price updates for all assets
            for asset in assets:
                asset_id = asset.get('id') or asset.get('name')
                if asset_id:
                    await self.api.subscribe_quotes(asset_id)
                    logger.debug(f"Subscribed to {asset_id}")
            
            logger.info("Subscribed to all market pairs")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to markets: {e}")
    
    async def _handle_reconnection(self):
        """Handle automatic reconnection with exponential backoff"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached. Giving up.")
            return
        
        self.reconnect_attempts += 1
        delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
        
        logger.info(f"Reconnecting in {delay} seconds (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})...")
        await asyncio.sleep(delay)
        
        await self.connect()
        
        if self.is_connected:
            await self.subscribe_to_markets()
    
    async def disconnect(self):
        """Disconnect from Pocket Option"""
        try:
            if self.api:
                await self.api.close()
                self.is_connected = False
                logger.info("Disconnected from Pocket Option")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def get_asset_info(self, asset_id: str):
        """
        Get information about a specific asset.
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            Asset information dictionary
        """
        try:
            if not self.api or not self.is_connected:
                return None
            
            return await self.api.get_asset(asset_id)
            
        except Exception as e:
            logger.error(f"Failed to get asset info for {asset_id}: {e}")
            return None
