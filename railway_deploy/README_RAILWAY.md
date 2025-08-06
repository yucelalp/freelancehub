# FreelanceHub Railway Deployment Guide

## 🚀 How to Deploy to Railway

Follow these steps to deploy your FreelanceHub application to Railway:

### Step 1: Prepare Your Repository

1. Make sure your GitHub repository contains all the necessary files:
   - `app.py` (main application)
   - `wsgi.py` (for gunicorn)
   - `requirements.txt` (Python packages)
   - `Procfile` (deployment config)
   - `railway.json` (Railway config)
   - `runtime.txt` (Python version)
   - `nixpacks.toml` (build config)
   - `templates/` (all HTML files)
   - `static/` (CSS, JS, images)

### Step 2: Deploy to Railway

1. Go to [Railway.app](https://railway.app) and sign up/login with GitHub
2. Click "Start a New Project"
3. Click "Deploy from GitHub repo"
4. Select your FreelanceHub repository
5. Click "Deploy Now"
6. Wait for the deployment to complete (2-3 minutes)

### Step 3: Check Deployment

Once deployed, you'll get a URL like `https://your-app-name.railway.app`

If you encounter an "Internal Server Error":

1. Go to your Railway dashboard
2. Click on your deployment
3. Check the "Logs" tab for specific error messages
4. Common issues:
   - Database initialization errors
   - Missing environment variables
   - Port binding issues

### Step 4: Configure Environment Variables

In Railway dashboard:

1. Go to your project
2. Click on "Variables"
3. Add these variables:
   - `SECRET_KEY`: (generate a random string)
   - `DATABASE_URL`: (Railway will provide this automatically if you add a PostgreSQL database)

## 🔧 Troubleshooting

### Internal Server Error

If you see "Internal Server Error" when accessing your deployed site:

1. **Check Logs**: In Railway dashboard, go to Logs tab
2. **Database Issues**: Make sure database tables are created
3. **Port Binding**: Ensure the app is binding to the PORT environment variable
4. **Dependencies**: Verify all required packages are in requirements.txt

### Database Issues

If you need a persistent database:

1. In Railway dashboard, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Connect it to your service
4. Railway will automatically set the DATABASE_URL environment variable

## 🎯 Testing Your Deployment

Once deployed, test these features:

- User registration and login
- Browsing services
- Creating services (as a freelancer)
- Placing orders
- Payment system
- Real-time chat
- Notifications

## 🚀 Sharing Your Application

Share these URLs with friends:

- Main site: `https://your-app-name.railway.app`
- Services: `https://your-app-name.railway.app/services`
- Registration: `https://your-app-name.railway.app/register`

---

If you need further assistance, check the [Railway documentation](https://docs.railway.app/) or contact support.