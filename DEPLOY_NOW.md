# 🚀 Deploy Now - Step by Step

## Your Secret Key (Save This!)
```
c987a5b4b8680ef773a4ea2593b5338e568f9b4da253f96652b39d8e8103e63e
```

## Option 1: Railway (Easiest - Recommended)

### Step 1: Initialize Git
```bash
git init
git add .
git commit -m "Initial commit - Email Automation Platform"
```

### Step 2: Push to GitHub
1. Go to [github.com](https://github.com) and create a new repository
2. Name it: `email-automation-platform`
3. Don't initialize with README
4. Copy the repository URL
5. Run these commands (replace YOUR_USERNAME with your GitHub username):
```bash
git remote add origin https://github.com/YOUR_USERNAME/email-automation-platform.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click "Login" → Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `email-automation-platform` repository
6. Railway will auto-detect and start deploying

### Step 4: Set Environment Variables
1. In Railway dashboard, click on your project
2. Go to "Variables" tab
3. Click "New Variable"
4. Add these variables:
   - **Name**: `SECRET_KEY`
     **Value**: `c987a5b4b8680ef773a4ea2593b5338e568f9b4da253f96652b39d8e8103e63e`
   - **Name**: `FLASK_ENV`
     **Value**: `production`
5. Railway will automatically redeploy

### Step 5: Get Your URL
1. Click "Settings" tab
2. Click "Generate Domain"
3. Your website is now live! 🎉

---

## Option 2: Test Locally First

```bash
# Set environment variable
$env:SECRET_KEY="c987a5b4b8680ef773a4ea2593b5338e568f9b4da253f96652b39d8e8103e63e"
$env:FLASK_ENV="production"

# Run the app
python app.py
```

Then open: http://localhost:5000

---

## Option 3: Render.com (Alternative)

1. Push to GitHub (same as Railway)
2. Go to [render.com](https://render.com)
3. Sign up with GitHub
4. Click "New" → "Web Service"
5. Connect your repository
6. Settings:
   - **Name**: email-automation
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -c gunicorn_config.py app:app`
7. Add environment variables:
   - `SECRET_KEY` = `c987a5b4b8680ef773a4ea2593b5338e568f9b4da253f96652b39d8e8103e63e`
   - `FLASK_ENV` = `production`
8. Click "Create Web Service"

---

## Quick Commands (Copy & Paste)

```bash
# Initialize Git
git init
git add .
git commit -m "Initial commit"

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/email-automation-platform.git
git branch -M main
git push -u origin main
```

---

## After Deployment

1. ✅ Visit your website URL
2. ✅ Test signup (create an account)
3. ✅ Test login
4. ✅ Upload a template
5. ✅ Create a campaign
6. ✅ Check dashboard

---

## Need Help?

- Check Railway/Render logs if there are errors
- Make sure all environment variables are set
- Verify CSV files are in the repository
- Check `DEPLOY.md` for detailed instructions

---

## 🎉 You're Ready!

Your website is production-ready. Follow the steps above to deploy!

