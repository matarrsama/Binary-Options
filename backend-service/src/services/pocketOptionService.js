const WebSocket = require('ws');
const logger = require('../config/logger');
const { db } = require('../config/firebase');

class PocketOptionService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 5000; // 5 seconds
    this.updateThrottle = {};
    this.throttleDelay = parseInt(process.env.UPDATE_THROTTLE_MS) || 1000;
    this.isConnecting = false;
    this.isConnected = false;
  }

  async connect() {
    if (this.isConnecting || this.isConnected) {
      return;
    }

    this.isConnecting = true;
    logger.info('Connecting to Pocket Option WebSocket...');

    try {
      const wsUrl = process.env.POCKET_OPTION_WS_URL || 'wss://pocketoption.com/eu/v2';
      const ssid = process.env.POCKET_OPTION_SSID;

      if (!ssid) {
        throw new Error('POCKET_OPTION_SSID environment variable is required');
      }

      this.ws = new WebSocket(wsUrl, {
        headers: {
          'Cookie': `ssid=${ssid}`,
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });

      this.ws.on('open', () => {
        logger.info('Connected to Pocket Option WebSocket');
        this.isConnected = true;
        this.isConnecting = false;
        this.reconnectAttempts = 0;

        // Subscribe to asset data
        this.subscribeToAssets();
      });

      this.ws.on('message', (data) => {
        this.handleMessage(data);
      });

      this.ws.on('error', (error) => {
        logger.error('WebSocket error:', error);
        this.isConnected = false;
        this.isConnecting = false;
      });

      this.ws.on('close', (code, reason) => {
        logger.warn(`WebSocket closed: ${code} - ${reason}`);
        this.isConnected = false;
        this.isConnecting = false;
        this.handleReconnect();
      });

    } catch (error) {
      logger.error('Failed to connect to Pocket Option:', error);
      this.isConnecting = false;
      this.handleReconnect();
    }
  }

  subscribeToAssets() {
    if (!this.isConnected) return;

    // Subscribe to all available assets
    const subscribeMessage = {
      type: 'subscribe',
      channel: 'asset',
      params: {
        asset: 'all'
      }
    };

    this.ws.send(JSON.stringify(subscribeMessage));
    logger.info('Subscribed to all assets');
  }

  handleMessage(data) {
    try {
      const message = JSON.parse(data.toString());
      
      if (message.type === 'asset_data') {
        this.processAssetData(message.data);
      } else if (message.type === 'assets_list') {
        this.processAssetsList(message.data);
      }
    } catch (error) {
      logger.error('Error parsing WebSocket message:', error);
    }
  }

  async processAssetData(assetData) {
    if (!assetData || !assetData.asset) return;

    const { asset, price, payout, timestamp } = assetData;
    
    // Throttle updates to avoid excessive Firestore writes
    const now = Date.now();
    const lastUpdate = this.updateThrottle[asset] || 0;
    
    if (now - lastUpdate < this.throttleDelay) {
      return;
    }

    this.updateThrottle[asset] = now;

    try {
      // Update Firestore document
      const pairRef = db.collection('pairs').doc(asset);
      
      const updateData = {
        price: price,
        payout: payout || null,
        timestamp: timestamp || now,
        lastUpdate: now,
        name: asset
      };

      await pairRef.set(updateData, { merge: true });
      logger.debug(`Updated ${asset}: ${price}`);

    } catch (error) {
      logger.error(`Failed to update ${asset} in Firestore:`, error);
    }
  }

  async processAssetsList(assetsList) {
    if (!Array.isArray(assetsList)) return;

    logger.info(`Received ${assetsList.length} assets`);

    try {
      const batch = db.batch();
      const now = Date.now();

      assetsList.forEach(asset => {
        const pairRef = db.collection('pairs').doc(asset.name);
        batch.set(pairRef, {
          name: asset.name,
          category: asset.category || 'unknown',
          enabled: asset.enabled !== false,
          createdAt: now
        }, { merge: true });
      });

      // Update metadata
      const metadataRef = db.collection('metadata').doc('system');
      batch.set(metadataRef, {
        lastAssetsUpdate: now,
        totalAssets: assetsList.length
      }, { merge: true });

      await batch.commit();
      logger.info('Initialized assets in Firestore');

    } catch (error) {
      logger.error('Failed to initialize assets in Firestore:', error);
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      logger.error('Max reconnection attempts reached. Giving up.');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff

    logger.info(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  async disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.isConnecting = false;
    logger.info('Disconnected from Pocket Option WebSocket');
  }

  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      isConnecting: this.isConnecting,
      reconnectAttempts: this.reconnectAttempts
    };
  }
}

module.exports = PocketOptionService;
