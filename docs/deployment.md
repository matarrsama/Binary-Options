# Deployment Guide

## Overview

This application consists of three main components:
1. **Frontend** - React app deployed on Netlify
2. **Backend Service** - Persistent Node.js service (deployed on Railway/Render/VPS)
3. **Firebase** - Realtime Database for data synchronization

## Prerequisites

- Node.js 18+
- Firebase project with Realtime Database
- Pocket Option account with SSID token
- Netlify account
- Railway/Render/VPS for backend service

## Step 1: Firebase Setup

1. Create a new Firebase project at https://console.firebase.google.com
2. Enable Realtime Database
3. Go to Project Settings > Service Accounts
4. Generate a new private key and save it
5. Set up database security rules using `firebase/database.rules.json`

## Step 2: Backend Service Deployment

### Option A: Railway
1. Fork this repository and connect to Railway
2. Set environment variables:
   ```
   POCKET_OPTION_SSID=your_ssid_token
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
   FIREBASE_CLIENT_EMAIL=your-service-account@project-id.iam.gserviceaccount.com
   FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
   ```
3. Deploy and note the service URL

### Option B: Render
1. Connect repository to Render
2. Create a new Web Service
3. Set the same environment variables as above
4. Deploy and note the service URL

### Option C: VPS
```bash
# Clone and setup
git clone <your-repo>
cd pocket-option-live-data/backend-service
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Start with PM2
npm install -g pm2
pm2 start src/index.js --name pocket-option-backend
pm2 startup
pm2 save
```

## Step 3: Frontend Deployment on Netlify

1. Connect your repository to Netlify
2. Set build settings:
   - Build command: `cd frontend && npm run build`
   - Publish directory: `frontend/build`
3. Set environment variables in Netlify:
   ```
   REACT_APP_FIREBASE_API_KEY=your_api_key
   REACT_APP_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
   REACT_APP_FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
   REACT_APP_FIREBASE_PROJECT_ID=your-project-id
   REACT_APP_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   REACT_APP_FIREBASE_APP_ID=your_app_id
   BACKEND_SERVICE_URL=https://your-backend-service-url.com
   ```
4. Deploy

## Step 4: Verification

1. Check backend health: `https://your-backend-url.com/health`
2. Check Netlify functions: `https://your-app.netlify.app/api/health`
3. Open the app and verify live data is flowing

## Environment Variables Summary

### Backend Service
- `POCKET_OPTION_SSID`: Pocket Option session token
- `FIREBASE_PROJECT_ID`: Firebase project ID
- `FIREBASE_PRIVATE_KEY`: Firebase service account private key
- `FIREBASE_CLIENT_EMAIL`: Firebase service account email
- `FIREBASE_DATABASE_URL`: Firebase Realtime Database URL
- `PORT`: Service port (default: 3001)
- `LOG_LEVEL`: Logging level (info/debug/error)
- `UPDATE_THROTTLE_MS`: Throttle delay for Firebase updates (default: 1000)

### Frontend (Netlify)
- `REACT_APP_FIREBASE_API_KEY`: Firebase web API key
- `REACT_APP_FIREBASE_AUTH_DOMAIN`: Firebase auth domain
- `REACT_APP_FIREBASE_DATABASE_URL`: Firebase database URL
- `REACT_APP_FIREBASE_PROJECT_ID`: Firebase project ID
- `REACT_APP_FIREBASE_STORAGE_BUCKET`: Firebase storage bucket
- `REACT_APP_FIREBASE_MESSAGING_SENDER_ID`: Firebase messaging sender ID
- `REACT_APP_FIREBASE_APP_ID`: Firebase app ID
- `BACKEND_SERVICE_URL`: Backend service URL for health checks

## Monitoring

### Backend Service
- Check logs: `pm2 logs pocket-option-backend`
- Health endpoint: `/health`
- Monitor Firebase Realtime Database usage

### Frontend
- Netlify provides built-in monitoring
- Check Firebase console for database usage
- Monitor WebSocket connections through browser dev tools

## Troubleshooting

### Common Issues

1. **No data appearing**
   - Check backend service logs
   - Verify Pocket Option SSID token is valid
   - Check Firebase security rules
   - Verify Firebase service account permissions

2. **WebSocket connection issues**
   - Ensure Pocket Option SSID is current
   - Check network connectivity
   - Verify WebSocket URL is correct

3. **Firebase permission errors**
   - Verify service account has Realtime Database admin permissions
   - Check database security rules
   - Ensure Firebase project ID matches

4. **Deployment issues**
   - Check all environment variables are set
   - Verify build commands are correct
   - Check deployment logs

### Getting Pocket Option SSID

1. Log into Pocket Option web platform
2. Open browser dev tools (F12)
3. Go to Application/Storage > Cookies
4. Find the `ssid` cookie value
5. Use this value as `POCKET_OPTION_SSID`

Note: SSID tokens expire and may need to be refreshed periodically.
