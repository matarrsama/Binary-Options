"""
Data processor for handling market data updates with throttling.
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from config import Config

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes and throttles market data updates"""
    
    def __init__(self, firebase_service):
        """
        Initialize data processor.
        
        Args:
            firebase_service: FirebaseService instance for writing data
        """
        self.firebase_service = firebase_service
        self.throttle_seconds = Config.UPDATE_THROTTLE_SECONDS
        
        # Track last update time for each pair
        self.last_update_time: Dict[str, float] = {}
        
        # Buffer for pending updates
        self.pending_updates: Dict[str, Dict[str, Any]] = {}
        
        # Start background task for processing buffered updates
        self._processing_task = None
    
    def start(self):
        """Start the background processing task"""
        if self._processing_task is None:
            self._processing_task = asyncio.create_task(self._process_buffered_updates())
            logger.info("Data processor started")
    
    async def stop(self):
        """Stop the background processing task"""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            logger.info("Data processor stopped")
    
    async def process_pair_update(self, pair_id: str, data: Dict[str, Any]):
        """
        Process a market pair update with throttling.
        
        Args:
            pair_id: Unique identifier for the pair
            data: Raw market data from Pocket Option
        """
        try:
            # Normalize the data
            normalized_data = self._normalize_data(pair_id, data)
            
            # Check if we should update immediately or buffer
            current_time = datetime.utcnow().timestamp()
            last_update = self.last_update_time.get(pair_id, 0)
            
            if current_time - last_update >= self.throttle_seconds:
                # Update immediately
                await self.firebase_service.update_pair(pair_id, normalized_data)
                self.last_update_time[pair_id] = current_time
            else:
                # Buffer the update
                self.pending_updates[pair_id] = normalized_data
                
        except Exception as e:
            logger.error(f"Failed to process pair update for {pair_id}: {e}")
    
    def _normalize_data(self, pair_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw market data into consistent format.
        
        Args:
            pair_id: Unique identifier for the pair
            data: Raw market data
            
        Returns:
            Normalized data dictionary
        """
        # Extract relevant fields from Pocket Option data
        # The exact structure depends on the PocketOption API response
        normalized = {
            'id': pair_id,
            'name': data.get('name', pair_id),
            'price': float(data.get('price', 0)),
            'payout': int(data.get('payout', 0)),
            'category': self._determine_category(pair_id),
            'isOpen': data.get('is_open', True),
        }
        
        return normalized
    
    def _determine_category(self, pair_id: str) -> str:
        """
        Determine the category of a trading pair based on its ID.
        
        Args:
            pair_id: Unique identifier for the pair
            
        Returns:
            Category string (forex, crypto, commodities, stocks)
        """
        pair_upper = pair_id.upper()
        
        # Crypto pairs
        if any(crypto in pair_upper for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'ADA', 'DOT', 'DOGE']):
            return 'crypto'
        
        # Forex pairs (currency codes)
        forex_currencies = ['EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']
        if any(curr in pair_upper for curr in forex_currencies):
            return 'forex'
        
        # Commodities
        if any(comm in pair_upper for comm in ['GOLD', 'SILVER', 'OIL', 'GAS', 'XAU', 'XAG']):
            return 'commodities'
        
        # Default to stocks
        return 'stocks'
    
    async def _process_buffered_updates(self):
        """Background task to process buffered updates periodically"""
        while True:
            try:
                await asyncio.sleep(self.throttle_seconds)
                
                if self.pending_updates:
                    # Get all pending updates
                    updates_to_process = dict(self.pending_updates)
                    self.pending_updates.clear()
                    
                    # Update in batch
                    await self.firebase_service.update_pairs_batch(updates_to_process)
                    
                    # Update last update times
                    current_time = datetime.utcnow().timestamp()
                    for pair_id in updates_to_process.keys():
                        self.last_update_time[pair_id] = current_time
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in buffered updates processing: {e}")
