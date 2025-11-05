# Quick Start Guide

## 🚀 Get Your Website Live in 5 Minutes

### Step 1: Choose Your Hosting Platform

**Recommended: Railway** (Easiest)
- Free tier available
- Auto-deploys from GitHub
- No credit card required

### Step 2: Deploy to Railway

1. **Push to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Go to Railway**:
   - Visit [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment**:
   - Click on your project
   - Go to "Variables" tab
   - Add: `SECRET_KEY` = (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - Add: `FLASK_ENV` = `production`

4. **Deploy**:
   - Railway will auto-deploy
   - Wait 2-3 minutes
   - Click "Generate Domain" to get your URL

**Done!** Your website is live! 🎉

---

## 🧪 Test Locally First

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open browser to http://localhost:5000
```

---

## 📋 What You Get

✅ **User Signup/Login** - Secure authentication
✅ **Email List Selection** - YC Startups, Business Emails, or GR
✅ **Template Management** - Upload custom templates or use default
✅ **Campaign Dashboard** - Track all your email campaigns
✅ **Real-time Stats** - See sent/failed emails
✅ **Multi-user Support** - Scalable for 100+ users

---

## 🔧 Alternative Hosting Options

See `DEPLOY.md` for:
- Render.com deployment
- Heroku deployment  
- VPS/server deployment
- Production configuration

---

## ⚠️ Important Notes

1. **Secret Key**: Always set a strong `SECRET_KEY` in production
2. **Database**: SQLite works for 100 users, PostgreSQL for more
3. **SMTP**: Users need to configure their email credentials
4. **CSV Files**: Make sure `ycombinatoremails.csv` and `companies.csv` are in the repo

---

## 🆘 Need Help?

1. Check `DEPLOY.md` for detailed instructions
2. Check application logs in your hosting platform
3. Verify all environment variables are set
4. Ensure CSV files are present in the repository

---

## 🎯 Next Steps After Deployment

1. Test signup/login
2. Upload a test template
3. Create a test campaign
4. Monitor the dashboard
5. Share with your users!

