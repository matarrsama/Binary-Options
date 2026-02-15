require('dotenv').config();
const PocketOptionService = require('./services/pocketOptionService');
const logger = require('./config/logger');

const pocketOptionService = new PocketOptionService();

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  await pocketOptionService.disconnect();
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully');
  await pocketOptionService.disconnect();
  process.exit(0);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Health check endpoint (if you want to add Express later)
const http = require('http');
const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    const status = pocketOptionService.getConnectionStatus();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      service: 'pocket-option-backend',
      timestamp: new Date().toISOString(),
      connection: status
    }));
  } else {
    res.writeHead(404);
    res.end();
  }
});

const PORT = process.env.PORT || 3001;

// Start the service
async function start() {
  try {
    // Start HTTP server for health checks
    server.listen(PORT, () => {
      logger.info(`Health check server running on port ${PORT}`);
    });

    // Connect to Pocket Option WebSocket
    await pocketOptionService.connect();
    
    logger.info('Pocket Option backend service started successfully');
  } catch (error) {
    logger.error('Failed to start service:', error);
    process.exit(1);
  }
}

start();
