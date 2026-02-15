# Development Guide

## Local Development Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- Firebase project
- Pocket Option SSID token

### 1. Clone and Install Dependencies

```bash
git clone <repository>
cd pocket-option-live-data
npm run install:all
```

### 2. Environment Setup

#### Backend Service
```bash
cd backend-service
cp .env.example .env
# Edit .env with your Firebase and Pocket Option credentials
```

#### Frontend
```bash
cd frontend
cp .env.example .env
# Edit .env with your Firebase web app credentials
```

### 3. Start Development Servers

#### Terminal 1: Backend Service
```bash
cd backend-service
npm run dev
```
The service will start on port 3001

#### Terminal 2: Frontend
```bash
cd frontend
npm start
```
The React app will start on port 3000

### 4. Firebase Setup

1. Go to Firebase Console
2. Create/Select your project
3. Enable Realtime Database
4. Set up security rules using `firebase/database.rules.json`

## Architecture Overview

```
┌─────────────────┐    WebSocket     ┌──────────────────┐    Firebase     ┌─────────────────┐
│ Pocket Option   │ ──────────────→  │ Backend Service  │ ─────────────→  │ Firebase RTDB   │
│ WebSocket API   │                  │ (Node.js)        │                 │                 │
└─────────────────┘                  └──────────────────┘                 └─────────────────┘
                                                                               │
                                                                               │ Firebase Listeners
                                                                               ▼
                                                                     ┌─────────────────┐
                                                                     │ Frontend        │
                                                                     │ (React)         │
                                                                     └─────────────────┘
```

## Key Components

### Backend Service (`backend-service/`)

- **PocketOptionService**: Handles WebSocket connection to Pocket Option
- **Firebase Integration**: Pushes live data to Firebase Realtime Database
- **Auto-reconnection**: Handles connection drops with exponential backoff
- **Throttling**: Prevents excessive Firebase writes

### Frontend (`frontend/`)

- **useFirebaseData**: Custom hook for Firebase real-time data
- **MarketPairsDashboard**: Main dashboard with all pairs
- **PairDetail**: Detailed view with price chart
- **SearchFilter**: Search and category filtering

### Netlify Functions (`netlify-functions/`)

- **Health Check**: Monitors service status
- **API Endpoints**: Additional serverless functionality

## Firebase Data Structure

```
{
  "pairs": {
    "EURUSD": {
      "name": "EURUSD",
      "price": "1.08456",
      "payout": "85.0",
      "category": "forex",
      "enabled": true,
      "timestamp": 1640995200000,
      "lastUpdate": 1640995200000
    },
    "BTCUSD": {
      "name": "BTCUSD",
      "price": "43250.50",
      "payout": "90.0",
      "category": "crypto",
      "enabled": true,
      "timestamp": 1640995200000,
      "lastUpdate": 1640995200000
    }
  },
  "metadata": {
    "lastAssetsUpdate": 1640995200000,
    "totalAssets": 150
  }
}
```

## Development Workflow

### Adding New Features

1. **Backend Changes**: Modify `PocketOptionService` or add new services
2. **Frontend Changes**: Update React components and hooks
3. **Firebase Schema**: Update data structure if needed
4. **Testing**: Test locally before deployment

### Debugging

#### Backend Service
```bash
# Check logs
cd backend-service
tail -f logs/combined.log

# Debug mode
LOG_LEVEL=debug npm run dev
```

#### Frontend
- Use browser dev tools
- Check Firebase console for real-time data
- Monitor Network tab for Firebase requests

#### Firebase
- Check Realtime Database in Firebase Console
- Verify security rules
- Monitor usage and quotas

## Code Style

- Use ES6+ features
- Follow React hooks patterns
- Implement proper error handling
- Use TypeScript for new features (optional)

## Testing

### Backend Tests
```bash
cd backend-service
npm test  # Add test framework as needed
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Testing
- Test WebSocket connection
- Verify Firebase data flow
- Check UI responsiveness

## Performance Considerations

### Backend
- Implement connection pooling for multiple WebSocket connections
- Use Redis for caching if needed
- Monitor memory usage

### Frontend
- Implement virtual scrolling for large datasets
- Use React.memo for expensive components
- Optimize Firebase queries

### Firebase
- Monitor read/write operations
- Implement data pagination if needed
- Use appropriate security rules

## Security

### Backend
- Never expose SSID token in logs
- Validate all incoming data
- Implement rate limiting

### Frontend
- Use HTTPS in production
- Validate user inputs
- Implement proper authentication when adding user features

### Firebase
- Use least-privilege security rules
- Enable Firebase Security Rules
- Monitor for unusual activity

## Future Enhancements

### Phase 2 Features
- User authentication
- Price alerts
- Historical data charts
- Portfolio tracking

### Phase 3 Features
- Trading signals
- Automated trading
- Advanced analytics
- Mobile app (React Native)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Common Issues and Solutions

### WebSocket Connection Issues
- Check SSID token validity
- Verify network connectivity
- Check Pocket Option API changes

### Firebase Permission Issues
- Verify service account permissions
- Check database security rules
- Ensure correct project ID

### Frontend Build Issues
- Clear node_modules and reinstall
- Check environment variables
- Verify Firebase configuration

## Resources

- [Pocket Option API Documentation](https://pocketoption.com/api-docs)
- [Firebase Realtime Database Docs](https://firebase.google.com/docs/database)
- [React Documentation](https://reactjs.org/docs)
- [Netlify Functions Docs](https://docs.netlify.com/edge-functions/overview/)
