const axios = require('axios');

exports.handler = async (event, context) => {
  // Only allow GET requests
  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
      body: JSON.stringify({
        error: 'Method not allowed'
      })
    };
  }

  try {
    // This would typically fetch from a cache or database
    // For now, return a simple response
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
      body: JSON.stringify({
        message: 'Pairs data available through Firebase Realtime Database',
        firebaseUrl: process.env.REACT_APP_FIREBASE_DATABASE_URL,
        note: 'Connect directly to Firebase for real-time data'
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
        error: 'Failed to fetch pairs data',
        message: error.message
      })
    };
  }
};
