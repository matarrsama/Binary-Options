"""
Firebase service for managing Firestore connections and data writes.
"""
import logging
from datetime import datetime
from typing import Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore
from config import Config

logger = logging.getLogger(__name__)


class FirebaseService:
    """Manages Firebase Firestore connection and data operations"""
    
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with credentials"""
        try:
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(Config.GOOGLE_APPLICATION_CREDENTIALS)
            firebase_admin.initialize_app(cred, {
                'projectId': Config.FIREBASE_PROJECT_ID,
            })
            
            # Get Firestore client
            self.db = firestore.client()
            logger.info("Firebase Admin SDK initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    async def update_pair(self, pair_id: str, data: Dict[str, Any]):
        """
        Update a market pair in Firestore.
        
        Args:
            pair_id: Unique identifier for the pair (e.g., 'EURUSD')
            data: Dictionary containing pair data (name, price, payout, category, etc.)
        """
        try:
            # Add timestamp
            data['lastUpdate'] = firestore.SERVER_TIMESTAMP
            data['timestamp'] = int(datetime.utcnow().timestamp())
            
            # Update document in Firestore
            doc_ref = self.db.collection('pairs').document(pair_id)
            doc_ref.set(data, merge=True)
            
            logger.debug(f"Updated pair {pair_id}: {data.get('price')}")
            
        except Exception as e:
            logger.error(f"Failed to update pair {pair_id}: {e}")
    
    async def update_pairs_batch(self, pairs_data: Dict[str, Dict[str, Any]]):
        """
        Update multiple pairs in a batch operation.
        
        Args:
            pairs_data: Dictionary mapping pair_id to pair data
        """
        try:
            batch = self.db.batch()
            
            for pair_id, data in pairs_data.items():
                # Add timestamp
                data['lastUpdate'] = firestore.SERVER_TIMESTAMP
                data['timestamp'] = int(datetime.utcnow().timestamp())
                
                # Add to batch
                doc_ref = self.db.collection('pairs').document(pair_id)
                batch.set(doc_ref, data, merge=True)
            
            # Commit batch
            batch.commit()
            logger.debug(f"Updated {len(pairs_data)} pairs in batch")
            
        except Exception as e:
            logger.error(f"Failed to update pairs batch: {e}")
    
    async def get_pair(self, pair_id: str) -> Dict[str, Any]:
        """
        Get a market pair from Firestore.
        
        Args:
            pair_id: Unique identifier for the pair
            
        Returns:
            Dictionary containing pair data or None if not found
        """
        try:
            doc_ref = self.db.collection('pairs').document(pair_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get pair {pair_id}: {e}")
            return None
    
    async def get_all_pairs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all market pairs from Firestore.
        
        Returns:
            Dictionary mapping pair_id to pair data
        """
        try:
            pairs_ref = self.db.collection('pairs')
            docs = pairs_ref.stream()
            
            pairs = {}
            for doc in docs:
                pairs[doc.id] = doc.to_dict()
            
            return pairs
            
        except Exception as e:
            logger.error(f"Failed to get all pairs: {e}")
            return {}
