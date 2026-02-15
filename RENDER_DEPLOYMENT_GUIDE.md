# Complete Render Deployment Guide

## Step-by-Step Guide to Deploy Your Backend on Render

### Prerequisites Checklist

Before starting, make sure you have:
- ✅ Render account (you just created this!)
- ✅ GitHub or GitLab account
- ✅ Your Pocket Option SSID token
- ✅ Firebase service account key JSON file

---

## Part 1: Prepare Your Code

### Step 1: Push Code to GitHub

If you haven't already pushed your code to GitHub:

```bash
# Navigate to your project
cd c:\Users\matar\OneDrive\Documents\options

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Pocket Option backend"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

> **Important**: Make sure `.gitignore` is working and you're NOT committing:
> - `.env` file
> - `serviceAccountKey.json`
> - `__pycache__/` folders

---

## Part 2: Get Your Credentials

### Step 2: Get Pocket Option SSID Token

1. **Open Pocket Option** in your browser: https://pocketoption.com/
2. **Log in** to your account
3. **Open Developer Tools**:
   - Windows/Linux: Press `F12` or `Ctrl + Shift + I`
   - Mac: Press `Cmd + Option + I`
4. **Go to Application tab** (or Storage in Firefox)
5. **Click on Cookies** → `https://pocketoption.com`
6. **Find the `ssid` cookie**
7. **Copy the Value** (it's a long string like `eyJ0eXAiOiJKV1QiLCJhbGc...`)
8. **Save it somewhere safe** - you'll need it in a moment

> **Note**: This token expires after about 24 hours, so you'll need to update it periodically.

### Step 3: Get Firebase Service Account Key

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Select your project**: `binary-fc0fb`
3. **Click the gear icon** ⚙️ → **Project settings**
4. **Go to "Service accounts" tab**
5. **Click "Generate new private key"**
6. **Download the JSON file**
7. **Open the JSON file** in a text editor (Notepad, VS Code, etc.)
8. **Copy the ENTIRE contents** - you'll paste this into Render

The JSON should look like this:
```json
{
  "type": "service_account",
  "project_id": "binary-fc0fb",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  ...
}
```

---

## Part 3: Deploy to Render

### Step 4: Create a New Web Service

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Click "New +"** button (top right)
3. **Select "Web Service"**

### Step 5: Connect Your Repository

You'll see options to connect your code:

**Option A: Connect GitHub** (Recommended)
1. Click **"Connect GitHub"**
2. Authorize Render to access your GitHub
3. Select your repository from the list
4. Click **"Connect"**

**Option B: Use Public Git Repository**
1. Click **"Public Git repository"**
2. Paste your repository URL
3. Click **"Continue"**

### Step 6: Configure Your Service

Now you'll see a configuration form. Fill it out as follows:

#### Basic Settings

| Field | Value |
|-------|-------|
| **Name** | `pocket-option-backend` (or any name you like) |
| **Region** | Choose closest to you (e.g., `Oregon (US West)`) |
| **Branch** | `main` (or your default branch) |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |

#### Build & Deploy Settings

| Field | Value |
|-------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python main.py` |

#### Instance Type

- Select **Free** (for testing) or **Starter** ($7/month for better performance)

### Step 7: Add Environment Variables

This is the most important part! Scroll down to **Environment Variables** section.

Click **"Add Environment Variable"** and add these **THREE** variables:

#### Variable 1: POCKET_OPTION_SSID
- **Key**: `POCKET_OPTION_SSID`
- **Value**: Paste your SSID token from Step 2

#### Variable 2: FIREBASE_PROJECT_ID
- **Key**: `FIREBASE_PROJECT_ID`
- **Value**: `binary-fc0fb`

#### Variable 3: GOOGLE_APPLICATION_CREDENTIALS (Secret File)
This one is special - it's a secret file, not a regular variable.

1. Click **"Add Secret File"** (not "Add Environment Variable")
2. **Filename**: `serviceAccountKey.json`
3. **Contents**: Paste the ENTIRE JSON content from Step 3
4. Click **"Save"**

Then add one more regular environment variable:

5. **Key**: `GOOGLE_APPLICATION_CREDENTIALS`
   **Value**: `/etc/secrets/serviceAccountKey.json`

> **Why?** Render stores secret files in `/etc/secrets/`, so we tell our app to look there.

### Step 8: Configure Health Check

Scroll down to **Health Check Path**:
- **Health Check Path**: `/health`

This tells Render to check if your service is running by visiting `https://your-service.onrender.com/health`

### Step 9: Deploy!

1. **Review all settings** one more time
2. **Click "Create Web Service"** button at the bottom

---

## Part 4: Monitor Deployment

### Step 10: Watch the Build

After clicking "Create Web Service", you'll see:

1. **Build logs** - Render is installing your dependencies
   - You'll see: `pip install -r requirements.txt`
   - This takes about 1-2 minutes

2. **Deploy logs** - Render is starting your service
   - You'll see: `python main.py`
   - Your app logs will appear here

### Step 11: Check for Success

Look for these messages in the logs:

✅ **Good signs**:
```
INFO - Firebase Admin SDK initialized successfully
INFO - Health check server started on port 8080
INFO - Connecting to Pocket Option...
INFO - Successfully connected to Pocket Option
INFO - Subscribed to all market pairs
INFO - Market Data Service started successfully
```

❌ **Error signs**:
```
ERROR - Failed to connect to Pocket Option
ERROR - Failed to initialize Firebase
ValueError: Configuration errors
```

If you see errors, check:
- SSID token is correct and not expired
- Firebase JSON is complete and valid
- All environment variables are set correctly

### Step 12: Get Your Service URL

Once deployed successfully:
1. Look at the top of the page for your service URL
2. It will be something like: `https://pocket-option-backend-xxxx.onrender.com`
3. **Copy this URL** - you'll need it!

### Step 13: Test Your Backend

Open a new browser tab and visit:
```
https://your-service-url.onrender.com/health
```

You should see:
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

✅ **If you see this** - Congratulations! Your backend is running!

---

## Part 5: Verify Data in Firestore

### Step 14: Check Firestore Console

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Select project**: `binary-fc0fb`
3. **Click "Firestore Database"** in the left menu
4. **Look for "pairs" collection**

You should see documents appearing with market pair data:
- EURUSD
- BTCUSD
- GBPUSD
- etc.

Each document should have:
- `name`: "EUR/USD"
- `price`: 1.08567
- `payout`: 85
- `category`: "forex"
- `lastUpdate`: timestamp

✅ **If you see data** - Your backend is successfully writing to Firestore!

---

## Part 6: Troubleshooting

### Common Issues

#### Issue 1: Build Failed
**Error**: `Could not find a version that satisfies the requirement...`

**Solution**: 
- Check `requirements.txt` has correct package names
- Try updating package versions

#### Issue 2: SSID Token Invalid
**Error**: `Failed to connect to Pocket Option`

**Solution**:
1. Get a fresh SSID token (they expire!)
2. Go to Render dashboard
3. Click your service
4. Go to "Environment" tab
5. Update `POCKET_OPTION_SSID` value
6. Service will auto-redeploy

#### Issue 3: Firebase Connection Failed
**Error**: `Failed to initialize Firebase`

**Solution**:
- Verify the secret file was created correctly
- Check that `GOOGLE_APPLICATION_CREDENTIALS` points to `/etc/secrets/serviceAccountKey.json`
- Make sure the JSON is complete (no truncation)

#### Issue 4: Service Keeps Restarting
**Check logs** for the error message, common causes:
- Missing environment variables
- Invalid credentials
- Port conflicts (should use port 8080)

### How to Update Environment Variables

1. Go to **Render Dashboard**
2. Click your service name
3. Click **"Environment"** tab in the left menu
4. Edit or add variables
5. Click **"Save Changes"**
6. Service will automatically redeploy

### How to View Logs

1. Go to **Render Dashboard**
2. Click your service name
3. Click **"Logs"** tab
4. You'll see real-time logs from your application

---

## Part 7: Keeping Your Service Running

### Free Tier Limitations

If you're using the **Free tier**:
- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ Takes 30-60 seconds to spin back up
- ⚠️ 750 hours/month free (enough for one service 24/7)

**Recommendation**: Upgrade to **Starter plan** ($7/month) for:
- ✅ Always-on service
- ✅ Better performance
- ✅ More reliable for real-time data

### Updating Your SSID Token

The SSID token expires every ~24 hours. To update:

1. Get new SSID token from browser (Step 2)
2. Go to Render → Your Service → Environment
3. Update `POCKET_OPTION_SSID`
4. Save (auto-redeploys)

**Pro tip**: Set a daily reminder to update your token!

---

## Next Steps

Once your backend is running:

1. ✅ **Verify health endpoint** works
2. ✅ **Check Firestore** has data
3. ✅ **Deploy frontend** to Netlify (see frontend README)
4. ✅ **Test end-to-end** - frontend should show live data

---

## Quick Reference

### Your Service URLs
- **Dashboard**: https://dashboard.render.com/
- **Service URL**: `https://your-service.onrender.com`
- **Health Check**: `https://your-service.onrender.com/health`

### Important Files
- **Backend code**: `c:\Users\matar\OneDrive\Documents\options\backend\`
- **Service account key**: Keep this safe, never commit to Git!
- **SSID token**: Update daily

### Support
- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com/

---

## Summary Checklist

- [ ] Code pushed to GitHub
- [ ] SSID token obtained from browser
- [ ] Firebase service account key downloaded
- [ ] Render account created
- [ ] Web Service created on Render
- [ ] Repository connected
- [ ] Build/Start commands configured
- [ ] All 3 environment variables added
- [ ] Secret file created for Firebase key
- [ ] Health check path set to `/health`
- [ ] Service deployed successfully
- [ ] Health endpoint returns "healthy"
- [ ] Data appearing in Firestore
- [ ] Service URL saved for frontend

**Congratulations!** 🎉 Your backend is now live and streaming market data!
