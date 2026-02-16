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
            
            # Prepare handshake auth data
            # Mask sensitive data for log safety
            ssid_masked = f"{Config.POCKET_OPTION_SSID[:5]}...{Config.POCKET_OPTION_SSID[-5:]}" if Config.POCKET_OPTION_SSID else "MISSING"
            logger.info(f"Diagnostic: SSID={ssid_masked}, UID={Config.POCKET_OPTION_UID}, isDemo={Config.POCKET_OPTION_IS_DEMO}")
            
            auth_data = {
                "session": Config.POCKET_OPTION_SSID,
                "isDemo": 1 if Config.POCKET_OPTION_IS_DEMO else 0,
                "uid": Config.POCKET_OPTION_UID,
                "platform": 2, # Reverting to 2 (Standard Web) for V4
                "isFastHistory": True,
                "isOptimized": True,
            }
            
            # VERSION STAMP: 2026-02-16-v4 (Handshake + Post-Connect + Platform 2)
            auth_model = AuthorizationData.model_validate(auth_data)
            auth_dict = auth_model.model_dump(mode='json', by_alias=True)
            
            await self.client.connect(url=region, auth=auth_dict)
            logger.info(f"✅ WebSocket handshake initiated (Platform 2, isDemo={Config.POCKET_OPTION_IS_DEMO})")
            
        except Exception as e:
            logger.error(f"Failed to initiate connection: {e}")
            await self._handle_reconnection()

    def _setup_event_handlers(self):
        """Set up event handlers for WebSocket events"""
        
        # Track if we've already sent auth for this connection
        self._auth_sent = False

        @self.client.on.connect
        async def on_connect(data: None):
            """Handle connection event"""
            logger.info(f"✅ WebSocket connected. Handshake data: {data}")
            self.is_connected = True
            
            # Fallback: Emitting auth manually after connect
            try:
                auth_data = {
                    "session": Config.POCKET_OPTION_SSID,
                    "isDemo": 1 if Config.POCKET_OPTION_IS_DEMO else 0,
                    "uid": Config.POCKET_OPTION_UID,
                    "platform": 2, # Match handshake platform
                    "isFastHistory": True,
                    "isOptimized": True,
                }
                logger.info("🚀 Emitting manual auth fallback after connection...")
                await self.client.emit.auth(AuthorizationData.model_validate(auth_data))
            except Exception as e:
                logger.error(f"❌ Manual auth fallback failed: {e}")

        # Hook underlying Socket.IO for raw diagnostics - NO FILTERING in V4
        try:
            import json as json_lib
            sio = getattr(self.client, '_sio', None) or getattr(self.client, 'sio', None)
            if sio:
                @sio.on('*')
                async def catch_all(event, data):
                    # Robust data handling for bytes vs dict
                    decoded_data = data
                    if isinstance(data, (bytes, bytearray)):
                        try: decoded_data = json_lib.loads(data)
                        except: decoded_data = f"BYTES[{len(data)}]"
                    
                    # Discovery: Log any event that might be auth-related
                    ev_lower = event.lower()
                    if any(x in ev_lower for x in ["auth", "success", "error", "fail", "kick", "stream"]):
                         logger.info(f"🔑 CRITICAL EVENT: '{event}' | Data: {str(decoded_data)[:500]}")
                    else:
                        logger.info(f"🔔 RAW SIO: '{event}' | Data Tip: {str(decoded_data)[:100]}")
        except Exception: pass

        @self.client.on.success_auth
        async def on_success_auth(data: SuccessAuthEvent):
            """Handle successful authentication"""
            logger.info(f"🎉 AUTH SUCCESS! ID: {data.id}")
            self.reconnect_attempts = 0
            # Subscribe ONLY after auth is confirmed
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
