"""
Pocket Option service for managing WebSocket connection and market data.
"""
import logging
import asyncio
import os
from typing import Optional, Callable
from pocket_option import PocketOptionClient
from pocket_option.constants import Regions
from pocket_option.models import AuthorizationData, SuccessAuthEvent, UpdateCloseValueItem, Asset
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
        self.client = PocketOptionClient()
        self.on_market_data = on_market_data
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = Config.MAX_RECONNECT_ATTEMPTS
        self.reconnect_delay = Config.RECONNECT_DELAY_SECONDS
        self.subscribed_assets = set()
        
        # Set up event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up event handlers for WebSocket events"""
        
        @self.client.on.connect
        async def on_connect(data: None):
            """Handle connection event"""
            logger.info("WebSocket connected")
            self.is_connected = True
            
            # Authenticate with SSID
            try:
                # Extract UID from SSID if needed (you may need to adjust this)
                # For now, using a placeholder - you'll need to get the actual UID
                await self.client.emit.auth(
                    AuthorizationData.model_validate({
                        "session": Config.POCKET_OPTION_SSID,
                        "isDemo": 1,  # Use demo account
                        "uid": 0,  # This needs to be extracted from your account
                        "platform": 2,
                        "isFastHistory": True,
                        "isOptimized": True,
                    })
                )
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
        
        @self.client.on.success_auth
        async def on_success_auth(data: SuccessAuthEvent):
            """Handle successful authentication"""
            logger.info(f"✅ Successfully authenticated with ID: {data.id}")
            logger.info(f"Auth data: {data}")
            self.reconnect_attempts = 0
            
            # Subscribe to all available assets
            await self.subscribe_to_markets()
        
        @self.client.on.disconnect
        async def on_disconnect(data):
            """Handle disconnection"""
            logger.warning("WebSocket disconnected")
            self.is_connected = False
            await self._handle_reconnection()
        
        @self.client.on.update_close_value
        async def on_update_close_value(assets: list[UpdateCloseValueItem]):
            """Handle real-time price updates"""
            logger.info(f"📊 Received update_close_value event with {len(assets)} assets")
            if self.on_market_data and assets:
                # Convert to our format
                for asset in assets:
                    asset_id = asset.asset.value if hasattr(asset.asset, 'value') else str(asset.asset)
                    data = {
                        'id': asset_id,
                        'name': asset_id,
                        'price': asset.value,
                        'payout': getattr(asset, 'payout', 0),
                        'is_open': True,
                    }
                    logger.info(f"Processing market data for {asset_id}: price={asset.value}")
                    await self.on_market_data(data)
        
        # CRITICAL: The actual event is 'updateAssets', not 'update_close_value'
        # This handler processes the raw asset data from Pocket Option
        @self.client.on.updateAssets
        async def on_update_assets(data):
            """Handle asset updates from Pocket Option"""
            logger.info(f"🎯 Received updateAssets event with data type: {type(data)}")
            
            # The data comes as a list of asset arrays
            # Each asset array contains: [id, symbol, name, type, ?, payout, ...]
            if self.on_market_data and data:
                try:
                    # Parse the asset data - it's a list of lists
                    for asset_array in data:
                        if len(asset_array) >= 6:
                            asset_id = asset_array[1]  # Symbol like "EURUSD_otc"
                            asset_name = asset_array[2]  # Human-readable name
                            payout = asset_array[5]  # Payout percentage
                            
                            # We need to get the actual price from somewhere
                            # For now, let's log what we're receiving
                            logger.info(f"📦 Asset update: {asset_id} ({asset_name}), payout={payout}%")
                            
                            # Note: updateAssets gives us asset metadata, not live prices
                            # We still need update_close_value for actual price updates
                            
                except Exception as e:
                    logger.error(f"Error parsing updateAssets data: {e}")
                    logger.debug(f"Raw data: {data[:2] if len(data) > 2 else data}")  # Log first 2 items
    
    async def connect(self):
        """Connect to Pocket Option WebSocket"""
        try:
            logger.info("Connecting to Pocket Option...")
            
            # Connect to WebSocket (using demo region)
            await self.client.connect(Regions.DEMO)
            
            logger.info("Connection initiated")
            
        except Exception as e:
            logger.error(f"Failed to connect to Pocket Option: {e}")
            await self._handle_reconnection()
    
    async def subscribe_to_markets(self):
        """Subscribe to all available market pairs"""
        try:
            if not self.is_connected:
                logger.warning("Cannot subscribe: not connected")
                return
            
            # Map of common asset names to Asset enum values
            # Using OTC versions for better availability
            asset_mapping = {
                "EURUSD_otc": Asset.EURUSD_otc,
                "GBPUSD_otc": Asset.GBPUSD_otc,
                "USDJPY_otc": Asset.USDJPY_otc,
                "AUDUSD_otc": Asset.AUDUSD_otc,
                "USDCAD_otc": Asset.USDCAD_otc,
                "EURJPY_otc": Asset.EURJPY_otc,
                "GBPJPY_otc": Asset.GBPJPY_otc,
                "EURGBP_otc": Asset.EURGBP_otc,
                "AUDJPY_otc": Asset.AUDJPY_otc,
                "NZDUSD_otc": Asset.NZDUSD_otc,
            }
            
            logger.info(f"Subscribing to {len(asset_mapping)} market pairs...")
            
            for asset_name, asset_enum in asset_mapping.items():
                try:
                    # Subscribe to asset updates using the correct API
                    await self.client.emit.subscribe_to_asset(asset_enum)
                    self.subscribed_assets.add(asset_name)
                    logger.info(f"✅ Subscribed to {asset_name}")
                except Exception as e:
                    logger.warning(f"❌ Failed to subscribe to {asset_name}: {e}")
            
            logger.info(f"Successfully subscribed to {len(self.subscribed_assets)} market pairs")
            
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
    
    async def disconnect(self):
        """Disconnect from Pocket Option"""
        try:
            if self.client:
                # Close the connection
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
            if not self.is_connected:
                return None
            
            # Return basic info for subscribed assets
            if asset_id in self.subscribed_assets:
                return {"id": asset_id, "name": asset_id, "subscribed": True}
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get asset info for {asset_id}: {e}")
            return None
