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
    
    async def connect(self):
        """Connect to Pocket Option WebSocket with handshake auth"""
        if self.is_connected:
            return
            
        try:
            # Select region based on demo flag
            # Regions.DEMO = wss://demo-api-eu.po.market
            # Regions.EUROPA = wss://api-eu.po.market
            region = Regions.DEMO if Config.POCKET_OPTION_IS_DEMO else Regions.EUROPA
            
            logger.info(f"Connecting to Pocket Option Region: {region} (isDemo={Config.POCKET_OPTION_IS_DEMO})")
            
            # VERSION STAMP: 2026-02-16-v9 (Atomic Debug & Log Expansion)
            # Pattern: No auth in handshake to avoid protocol interference
            await self.client.connect(url=region)
            logger.info(f"✅ WebSocket connection initiated to {region} (V9)")
            
        except Exception as e:
            logger.error(f"Failed to initiate connection: {e}")
            await self._handle_reconnection()

    def _setup_event_handlers(self):
        """Set up event handlers for WebSocket events"""
        
        # Track if we've already sent auth for this connection
        self._auth_sent = False

        @self.client.on.connect
        async def on_connect(data: None):
            """Handle connection event - V9 Atomic Auth"""
            logger.info(f"✅ WebSocket connected. Handshake data: {data}")
            self.is_connected = True
            
            try:
                # V9 STRATEGY: One single, clean payload matching browser exactly.
                # No triple-bagging, no handshake.
                raw_auth_payload = {
                    "sessionToken": Config.POCKET_OPTION_SSID,
                    "isDemo": 1 if Config.POCKET_OPTION_IS_DEMO else 0,
                    "uid": str(Config.POCKET_OPTION_UID), 
                    "platform": 2,
                    "lang": "en",
                    "isFastHistory": True,
                    "isOptimized": True,
                }
                
                logger.info(f"🚀 Emitting V9 Atomic Auth (UID={Config.POCKET_OPTION_UID})...")
                
                # Use underlying SIO for raw control backup
                sio = getattr(self.client, '_sio', None) or getattr(self.client, 'sio', None)
                if sio:
                    await sio.emit("auth", raw_auth_payload)
                    logger.info("📡 V9 Atomic 'auth' emission sent via SIO.")
                
            except Exception as e:
                logger.error(f"❌ V9 Auth emission failed: {e}")

        # Hook underlying Socket.IO for total diagnostics
        try:
            import json as json_lib
            sio = getattr(self.client, '_sio', None) or getattr(self.client, 'sio', None)
            if sio:
                @sio.on('*')
                async def catch_all(event, data):
                    # ALL EVENTS logging in V9
                    decoded_data = data
                    if isinstance(data, (bytes, bytearray)):
                        try: decoded_data = json_lib.loads(data)
                        except: decoded_data = f"BYTES[{len(data)}]"
                    
                    logger.info(f"� [DEBUG V9] Event: '{event}' | Data: {str(decoded_data)[:1000]}")
        except Exception: pass

        @self.client.on.success_auth
        async def on_success_auth(data: SuccessAuthEvent):
            """Handle successful authentication"""
            logger.info(f"🎉 AUTH SUCCESS! ID: {data.id}")
            self.reconnect_attempts = 0
            
            # Initialize session loaders as per official example
            try:
                await self.client.emit.indicator_load()
                await self.client.emit.favorite_load()
                await self.client.emit.price_alert_load()
            except Exception as e:
                logger.warning(f"Metadata load failed: {e}")
                
            # Subscribe after initialization
            await self.subscribe_to_markets()

        @self.client.on.update_close_value
        async def on_update_close_value(assets: list[UpdateCloseValueItem]):
            """Handle real-time price updates"""
            logger.info(f"📊 PRICE DATA: {len(assets)} items")
            if self.on_market_data:
                for asset in assets:
                    try:
                        asset_id = str(asset.asset.value) if hasattr(asset.asset, 'value') else str(asset.asset)
                        await self.on_market_data({
                            'id': asset_id,
                            'name': asset_id,
                            'price': asset.value,
                            'payout': getattr(asset, 'payout', 0),
                            'is_open': True,
                        })
                    except Exception: pass

        @self.client.on.update_assets
        async def on_update_assets(assets):
            """Handle asset metadata updates"""
            logger.debug(f"📋 Metadata received: {len(assets)} assets")

        @self.client.on.disconnect
        async def on_disconnect(data):
            """Handle disconnection"""
            logger.warning(f"⚠️ DISCONNECTED. Data: {data}")
            self.is_connected = False
            self._auth_sent = False
            self.subscribed_assets.clear()
            await self._handle_reconnection()

    async def subscribe_to_markets(self):
        """Subscribe to all available market pairs and activate their streams"""
        try:
            if not self.is_connected:
                logger.warning("Cannot subscribe: not connected")
                return
            
            # Wait for auth and metadata loaders to settle
            await asyncio.sleep(3)
            
            # Use specific assets from enum for safety
            from pocket_option.models import ChangeAssetRequest
            
            # Focused list for testing stabilization
            asset_list = [
                Asset.EURUSD_otc, Asset.GBPUSD_otc, Asset.USDJPY_otc,
                Asset.AUDUSD_otc, Asset.USDCAD_otc, Asset.EURJPY_otc,
                Asset.GBPJPY_otc, Asset.EURGBP_otc, Asset.AUDJPY_otc,
                Asset.NZDUSD_otc
            ]
            
            logger.info(f"Subscribing to {len(asset_list)} market pairs...")
            
            for asset in asset_list:
                try:
                    asset_name = asset.name if hasattr(asset, 'name') else str(asset)
                    logger.info(f"Activating {asset_name}...")
                    
                    # 1. Subscribe to the symbol
                    await self.client.emit.subscribe_to_asset(asset)
                    
                    # 2. Change to the asset to trigger stream (Mandatory in some SDK versions)
                    await self.client.emit.change_asset(ChangeAssetRequest(asset=asset, period=60))
                    
                    # 3. Market sentiment (Optional but useful for data flow)
                    await self.client.emit.subscribe_for_market_sentiment(asset)
                    
                    self.subscribed_assets.add(asset_name)
                    logger.info(f"✅ Protocol sequence completed for {asset_name}")
                    
                except Exception as e:
                    logger.warning(f"❌ Failed to activate {asset}: {e}")
            
            logger.info(f"Successfully initiated V5 protocol for {len(self.subscribed_assets)} assets")
            
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
