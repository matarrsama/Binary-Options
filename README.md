# Pocket Option Live Market Data

A full-stack web application displaying live Pocket Option market pairs with real-time price updates.

## Architecture

- **Frontend**: React (deployed on Netlify)
- **Backend Service**: Persistent Node.js service with PocketOption API integration
- **Real-time Database**: Firebase Realtime Database
- **Serverless**: Netlify Functions for REST endpoints

## Data Flow

```
Pocket Option WebSocket 
→ Persistent Backend Service 
→ Firebase Realtime Database 
→ Frontend (via Firebase listeners)
→ UI Updates
```

## Project Structure

```
├── frontend/          # React application
├── backend-service/   # Persistent Node.js service
├── netlify-functions/ # Netlify serverless functions
├── firebase/         # Firebase configuration
└── docs/            # Documentation
```

## Environment Variables

### Backend Service
- `POCKET_OPTION_SSID`: Pocket Option session token
- `FIREBASE_PROJECT_ID`: Firebase project ID
- `FIREBASE_PRIVATE_KEY`: Firebase private key
- `FIREBASE_CLIENT_EMAIL`: Firebase client email

### Frontend
- `REACT_APP_FIREBASE_API_KEY`: Firebase API key
- `REACT_APP_FIREBASE_AUTH_DOMAIN`: Firebase auth domain
- `REACT_APP_FIREBASE_DATABASE_URL`: Firebase database URL
- `REACT_APP_FIREBASE_PROJECT_ID`: Firebase project ID

## Getting Started

1. Set up Firebase project and Realtime Database
2. Configure environment variables
3. Start backend service
4. Deploy frontend to Netlify
