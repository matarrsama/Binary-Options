# Pocket Option Market Data Backend

Python backend service that connects to Pocket Option via WebSocket and streams live market data to Firebase Firestore.

## Features

- Real-time WebSocket connection to Pocket Option
- Automatic reconnection with exponential backoff
- Data throttling (max 1 update/second per pair)
- Batch updates to Firestore for efficiency
- Health check endpoint for monitoring
- Structured logging

## Prerequisites

- Python 3.8+
- Pocket Option SSID token (session cookie)
- Firebase project with Firestore enabled
- Firebase service account credentials

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Pocket Option SSID Token

1. Log in to Pocket Option in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage → Cookies
4. Find the `ssid` cookie and copy its value

### 3. Get Firebase Service Account Key

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save the JSON file as `serviceAccountKey.json` in the backend directory

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
POCKET_OPTION_SSID=your_actual_ssid_token_here
FIREBASE_PROJECT_ID=binary-fc0fb
GOOGLE_APPLICATION_CREDENTIALS=./serviceAccountKey.json
```

## Running Locally

```bash
python main.py
```

The service will:
- Connect to Pocket Option WebSocket
- Subscribe to all available market pairs
- Stream data to Firestore in real-time
- Start health check server on port 8080

## Health Check

```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "services": {
    "pocket_option": "connected",
    "firebase": "connected"
  },
  "reconnect_attempts": 0
}
```

## Deploying to Render

### 1. Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your Git repository

### 2. Configure Service

- **Name**: `pocket-option-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Instance Type**: Free or Starter

### 3. Add Environment Variables

In Render dashboard, add:

- `POCKET_OPTION_SSID`: Your SSID token
- `FIREBASE_PROJECT_ID`: `binary-fc0fb`
- `GOOGLE_APPLICATION_CREDENTIALS`: Paste the entire content of your `serviceAccountKey.json` as a secret file

### 4. Add Health Check

- **Health Check Path**: `/health`
- **Port**: `8080`

### 5. Deploy

Click "Create Web Service" and Render will deploy automatically.

## Project Structure

```
backend/
├── main.py                          # Main entry point
├── config.py                        # Configuration management
├── health_server.py                 # Health check HTTP server
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── services/
│   ├── __init__.py
│   ├── pocket_option_service.py     # Pocket Option WebSocket client
│   ├── firebase_service.py          # Firebase Firestore client
│   └── data_processor.py            # Data processing and throttling
└── README.md                        # This file
```

## Firestore Data Structure

```
pairs/
  ├── EURUSD/
  │   ├── id: "EURUSD"
  │   ├── name: "EUR/USD"
  │   ├── price: 1.0856
  │   ├── payout: 85
  │   ├── category: "forex"
  │   ├── isOpen: true
  │   ├── timestamp: 1739645210
  │   └── lastUpdate: Timestamp
  └── ...
```

## Troubleshooting

### Connection Issues

- Verify your SSID token is valid (tokens expire after ~24 hours)
- Check Render logs for connection errors
- Ensure Firebase credentials are correct

### High Firebase Costs

- Adjust `UPDATE_THROTTLE_SECONDS` in `.env` (default: 1 second)
- Monitor Firebase usage in console

### Service Crashes

- Check health endpoint: `/health`
- Review Render logs
- Verify all environment variables are set

## Security Notes

- Never commit `.env` or `serviceAccountKey.json` to Git
- Rotate SSID token regularly
- Use Firestore security rules to prevent unauthorized writes
- Keep dependencies updated

## License

MIT
