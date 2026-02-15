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
                logger.info("Attempting authentication...")
                logger.info(f"Using UID: {Config.POCKET_OPTION_UID}, isDemo: {Config.POCKET_OPTION_IS_DEMO}")
                
                auth_data = {
                    "session": Config.POCKET_OPTION_SSID,
                    "isDemo": 1 if Config.POCKET_OPTION_IS_DEMO else 0,
                    "uid": Config.POCKET_OPTION_UID,
                    "platform": 2,
                    "isFastHistory": True,
                    "isOptimized": True,
                }
                
                await self.client.emit.auth(AuthorizationData.model_validate(auth_data))
                logger.info("Authentication request sent")
                
                # Proactively subscribe to markets after sending auth, just in case success_auth event is missed
                logger.info("Proactively starting market subscriptions...")
                await self.subscribe_to_markets()
                
            except Exception as e:
                logger.error(f"Authentication flow error: {e}", exc_info=True)
        
        @self.client.on.success_auth
        async def on_success_auth(data: SuccessAuthEvent):
            """Handle successful authentication"""
            logger.info("🎉 SUCCESS_AUTH EVENT RECEIVED")
            logger.info(f"Successfully authenticated with ID: {data.id}")
            self.reconnect_attempts = 0
            
            # Re-subscribe to ensure we're getting data on the authenticated session
            await self.subscribe_to_markets()
        
        # generic error handler
        @self.client.on.error
        async def on_error(data):
            logger.error(f"❌ WebSocket Error: {data}")

        @self.client.on.disconnect
        async def on_disconnect(data):
            """Handle disconnection"""
            logger.warning(f"⚠️ WebSocket disconnected. Data: {data}")
            self.is_connected = False
            await self._handle_reconnection()
        
        @self.client.on.update_close_value
        async def on_update_close_value(assets: list[UpdateCloseValueItem]):
            """Handle real-time price updates"""
            logger.info(f"📊 RECEIVED PRICE UPDATE: {len(assets)} assets")
            if self.on_market_data and assets:
                for asset in assets:
                    try:
                        # Improved ID extraction
                        asset_id = str(asset.asset.value) if hasattr(asset.asset, 'value') else str(asset.asset)
                        data = {
                            'id': asset_id,
                            'name': asset_id,
                            'price': asset.value,
                            'payout': getattr(asset, 'payout', 0),
                            'is_open': True,
                        }
                        logger.debug(f"💰 Price Update: {asset_id} = {asset.value}")
                        await self.on_market_data(data)
                    except Exception as e:
                        logger.error(f"Error processing asset update: {e}")
        
        @self.client.on.update_assets
        async def on_update_assets(assets):
            """Handle asset metadata updates"""
            logger.info(f"📋 Received {len(assets)} asset metadata updates")
        
        # Try to add a generic event logger to see ALL events
        try:
            async def on_any_event(event_name, *args, **kwargs):
                """Log ALL events - NO FILTERS"""
                logger.info(f"🔔 RAW EVENT: '{event_name}'")
                if args:
                    logger.debug(f"   Data: {str(args[0])[:1000]}")
            
            if hasattr(self.client.on, 'any'):
                self.client.on.any(on_any_event)
                logger.info("✅ Registered 'any' event handler (Aggressive)")
        except Exception as e:
            logger.warning(f"Could not register 'any' event handler: {e}")

    
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
            
            # Wait a moment for auth to be processed on server side
            await asyncio.sleep(2)
            
            # Map of common asset names to Asset enum values
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
                    # Attempt subscription using the raw value (string) as well as the enum
                    # Some versions of the API/library prefer strings
                    asset_value = asset_enum.value if hasattr(asset_enum, 'value') else str(asset_enum)
                    
                    logger.info(f"Attempting subscription to {asset_name} (value: {asset_value})")
                    await self.client.emit.subscribe_to_asset(asset_enum)
                    self.subscribed_assets.add(asset_name)
                    logger.info(f"✅ Subscribed to {asset_name}")
                except Exception as e:
                    logger.warning(f"❌ Failed to subscribe to {asset_name}: {e}")
            
            logger.info(f"Successfully initiated subscription for {len(self.subscribed_assets)} market pairs")
            
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
