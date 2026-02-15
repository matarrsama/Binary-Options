const axios = require('axios');

exports.handler = async (event, context) => {
  try {
    // Check backend service health
    const backendUrl = process.env.BACKEND_SERVICE_URL || 'http://localhost:3001';
    
    let backendStatus = 'unknown';
    try {
      const response = await axios.get(`${backendUrl}/health`, { timeout: 5000 });
      backendStatus = response.data.status === 'ok' ? 'healthy' : 'unhealthy';
    } catch (error) {
      backendStatus = 'unreachable';
    }

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
      body: JSON.stringify({
        status: 'ok',
        timestamp: new Date().toISOString(),
        services: {
          frontend: 'healthy',
          backend: backendStatus,
          netlify: 'healthy'
        }
      })
    };

  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
      body: JSON.stringify({
        status: 'error',
        message: error.message
      })
    };
  }
};
