# Pocket Option Live Market Pairs

A full-stack web application that displays live market pairs and price data from Pocket Option with real-time updates.

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Pocket Option  │────────▶│  Backend Service │────────▶│    Firebase     │
│   WebSocket     │         │  (Render/Python) │         │   Firestore     │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                                                   │
                                                                   │ Real-time
                                                                   │ Listener
                                                                   ▼
                                                          ┌─────────────────┐
                                                          │    Frontend     │
                                                          │ (Netlify/React) │
                                                          └─────────────────┘
```

### Components

1. **Backend Service (Python on Render)**
   - Connects to Pocket Option via WebSocket using PocketOption API Async
   - Processes and normalizes market data
   - Writes to Firebase Firestore with throttling (1 update/second per pair)
   - Auto-reconnection with exponential backoff
   - Health check endpoint for monitoring

2. **Frontend (React/Next.js on Netlify)**
   - Static site with real-time Firestore listeners
   - Responsive design with dark theme
   - Search and category filtering
   - Live price charts
   - Connection status indicator

3. **Database (Firebase Firestore)**
   - Real-time data distribution
   - Secure with read-only client access
   - Efficient indexing for queries

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (for backend)
- Node.js 18+ (for frontend)
- Pocket Option SSID token
- Firebase project with Firestore

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python main.py
```

See [backend/README.md](backend/README.md) for detailed instructions.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

See [frontend/README.md](frontend/README.md) for detailed instructions.

## 📦 Deployment

### Backend → Render

1. Create new Web Service on Render
2. Connect your Git repository
3. Set environment variables:
   - `POCKET_OPTION_SSID`
   - `FIREBASE_PROJECT_ID`
   - `GOOGLE_APPLICATION_CREDENTIALS` (paste JSON content)
4. Deploy with:
   - Build: `pip install -r requirements.txt`
   - Start: `python main.py`

### Frontend → Netlify

1. Push code to Git
2. Connect repository in Netlify
3. Deploy with:
   - Build: `npm run build`
   - Publish: `out`

### Firebase Setup

1. Deploy security rules:
```bash
firebase deploy --only firestore:rules
```

2. Deploy indexes:
```bash
firebase deploy --only firestore:indexes
```

## 🔐 Security

- ✅ SSID token stored only on backend
- ✅ Firestore rules prevent client writes
- ✅ Public read access for market data
- ✅ No sensitive data in frontend code
- ✅ HTTPS everywhere

## 📊 Features

### Current Features

- ✅ Real-time market pair display
- ✅ Live price updates (<1 second latency)
- ✅ Search by pair name
- ✅ Filter by category (Forex, Crypto, Commodities, Stocks)
- ✅ Detailed pair view with charts
- ✅ Connection status monitoring
- ✅ Auto-reconnection
- ✅ Responsive design
- ✅ Dark theme with glassmorphism

### Future Enhancements

- 🔜 Push notifications for price alerts
- 🔜 User accounts and authentication
- 🔜 Signal generation logic
- 🔜 Trade tracking dashboard
- 🔜 Historical data analysis
- 🔜 Multiple timeframe charts

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- PocketOption API Async
- Firebase Admin SDK
- aiohttp (health server)

**Frontend:**
- Next.js 14
- React 18
- Firebase Client SDK
- Tailwind CSS
- Recharts
- Lucide Icons

**Infrastructure:**
- Render (backend hosting)
- Netlify (frontend hosting)
- Firebase Firestore (database)

## 📁 Project Structure

```
options/
├── backend/
│   ├── main.py                    # Main entry point
│   ├── config.py                  # Configuration
│   ├── health_server.py           # Health check server
│   ├── services/
│   │   ├── pocket_option_service.py
│   │   ├── firebase_service.py
│   │   └── data_processor.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── components/                # React components
│   ├── lib/                       # Firebase & utilities
│   ├── pages/                     # Next.js pages
│   ├── styles/                    # Global styles
│   ├── package.json
│   └── README.md
├── firestore.rules                # Firestore security rules
├── firestore.indexes.json         # Firestore indexes
└── README.md                      # This file
```

## 🔧 Configuration

### Backend Environment Variables

```env
POCKET_OPTION_SSID=your_ssid_token
FIREBASE_PROJECT_ID=binary-fc0fb
GOOGLE_APPLICATION_CREDENTIALS=./serviceAccountKey.json
UPDATE_THROTTLE_SECONDS=1
LOG_LEVEL=INFO
HEALTH_CHECK_PORT=8080
```

### Firebase Configuration

Already configured in `frontend/lib/firebase.js`:
- Project ID: `binary-fc0fb`
- Public read access enabled
- Client writes disabled

## 📈 Monitoring

### Backend Health Check

```bash
curl https://your-backend.onrender.com/health
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

### Frontend Status

Check the connection indicator in the top-right corner:
- 🟢 Connected - Receiving real-time updates
- 🟡 Reconnecting - Attempting to reconnect
- 🔴 Disconnected - No connection

## 🐛 Troubleshooting

### Backend Issues

**Connection fails:**
- Verify SSID token is valid (expires after ~24 hours)
- Check Render logs for errors
- Ensure Firebase credentials are correct

**High Firebase costs:**
- Increase `UPDATE_THROTTLE_SECONDS` in `.env`
- Monitor usage in Firebase console

### Frontend Issues

**No data showing:**
- Verify backend is running and healthy
- Check Firestore console for data
- Check browser console for errors

**Build fails:**
- Delete `node_modules` and reinstall
- Clear Next.js cache: `rm -rf .next`

## 📝 License

MIT

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📧 Support

For issues or questions, please check:
1. Backend logs on Render
2. Frontend console in browser
3. Firebase console for data
4. Health check endpoint

---

**Note:** This application uses an unofficial API and is not affiliated with or endorsed by Pocket Option.
