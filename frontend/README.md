# Pocket Option Frontend

React/Next.js frontend for displaying live Pocket Option market pairs with real-time updates from Firebase Firestore.

## Features

- Real-time market data updates via Firestore
- Search and filter by category (Forex, Crypto, Commodities, Stocks)
- Responsive design with dark theme
- Live price charts
- Connection status indicator
- Detailed pair view with price history

## Prerequisites

- Node.js 18+ and npm
- Firebase project (already configured)

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Firebase Configuration

The Firebase configuration is already set up in `lib/firebase.js` with your project credentials.

## Running Locally

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Building for Production

```bash
npm run build
```

This creates a static export in the `out` directory, ready for Netlify deployment.

## Deploying to Netlify

### Option 1: Netlify CLI

1. Install Netlify CLI:
```bash
npm install -g netlify-cli
```

2. Login to Netlify:
```bash
netlify login
```

3. Deploy:
```bash
netlify deploy --prod
```

### Option 2: Git Integration

1. Push your code to GitHub/GitLab
2. Go to [Netlify Dashboard](https://app.netlify.com/)
3. Click "Add new site" → "Import an existing project"
4. Connect your repository
5. Configure build settings:
   - **Build command**: `npm run build`
   - **Publish directory**: `out`
6. Click "Deploy site"

### Option 3: Manual Deploy

1. Build the project:
```bash
npm run build
```

2. Drag and drop the `out` folder to Netlify's deploy page

## Project Structure

```
frontend/
├── components/
│   ├── CategoryFilter.jsx       # Category filter buttons
│   ├── ConnectionStatus.jsx     # Connection status indicator
│   ├── MarketPairsDashboard.jsx # Main dashboard component
│   ├── PairCard.jsx             # Individual pair card
│   ├── PriceChart.jsx           # Price chart with Recharts
│   └── SearchBar.jsx            # Search input
├── lib/
│   ├── firebase.js              # Firebase initialization
│   └── firestore.js             # Firestore helper functions
├── pages/
│   ├── _app.js                  # App wrapper
│   ├── _document.js             # Document wrapper
│   ├── index.js                 # Home page
│   └── pair/
│       └── [id].js              # Dynamic pair detail page
├── styles/
│   └── globals.css              # Global styles with Tailwind
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # Tailwind configuration
├── netlify.toml                 # Netlify deployment config
└── package.json                 # Dependencies
```

## Environment Variables

No environment variables needed! Firebase config is already included in the code.

## Features Explained

### Real-time Updates

The app uses Firestore's `onSnapshot` to listen for real-time changes:

```javascript
subscribeToAllPairs((pairs) => {
  setPairs(pairs); // Automatically updates when backend writes new data
});
```

### Search & Filter

- **Search**: Filters pairs by name/ID with debouncing
- **Category Filter**: Shows only pairs from selected category

### Price Charts

Uses Recharts to display recent price history with:
- Responsive design
- Dark theme
- Smooth animations

### Connection Status

Shows real-time connection status:
- 🟢 Connected
- 🔴 Disconnected
- 🟡 Reconnecting

## Customization

### Colors

Edit `tailwind.config.js` to change the color scheme:

```javascript
colors: {
  primary: { /* your colors */ },
  success: { /* your colors */ },
  // ...
}
```

### Fonts

Change fonts in `styles/globals.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=YourFont&display=swap');
```

## Troubleshooting

### Build Errors

If you get build errors, try:

```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Firestore Connection Issues

- Check Firebase console for security rules
- Verify project ID in `lib/firebase.js`
- Check browser console for errors

### No Data Showing

- Ensure backend service is running on Render
- Check Firestore console to verify data exists
- Verify collection name is `pairs`

## Performance

- Static export for fast loading
- Code splitting with Next.js
- Optimized images
- Minimal bundle size

## Security

- Firebase credentials are public (read-only)
- Firestore security rules prevent writes from client
- No sensitive data exposed

## License

MIT
