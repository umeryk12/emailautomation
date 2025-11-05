# 🚀 Deploy Your Email Automation Tool

**Repository:** https://github.com/mrumer-yk/emailaumation

## ✅ Code is Pushed to GitHub!

Your repository is ready at: https://github.com/mrumer-yk/emailaumation

---

## 🚀 Deploy to Railway (RECOMMENDED - 3 Minutes)

### Step 1: Go to Railway
Visit: https://railway.app

### Step 2: Sign Up
- Click "Login"
- Choose "Sign up with GitHub"
- Authorize Railway

### Step 3: Deploy Your Repo
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select: **`mrumer-yk/emailaumation`**
4. Railway will auto-detect Flask and start deploying

### Step 4: Set Environment Variables
1. Click on your project
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Add these:

   **Variable 1:**
   ```
   Name: SECRET_KEY
   Value: 2c0819d984af217cad2b8a3b6061aebc74502d7575ef2ed019f5d8ada33f6f3a
   ```

   **Variable 2:**
   ```
   Name: FLASK_ENV
   Value: production
   ```

5. Railway will automatically redeploy

### Step 5: Get Your Live URL
1. Click **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Your site is LIVE! 🎉

**Your site will be at:** `your-app-name.railway.app`

---

## 🎯 Alternative: Deploy to Render

### Step 1: Go to Render
Visit: https://render.com

### Step 2: Sign Up
- Sign up with GitHub
- Authorize Render

### Step 3: Create Web Service
1. Click **"New"** → **"Web Service"**
2. Connect repository: **`mrumer-yk/emailaumation`**

### Step 4: Configure
- **Name:** email-automation-tool
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn -c gunicorn_config.py app:app`
- **Plan:** Free (or Starter $7/month)

### Step 5: Environment Variables
Add in "Environment" tab:
```
SECRET_KEY = 2c0819d984af217cad2b8a3b6061aebc74502d7575ef2ed019f5d8ada33f6f3a
FLASK_ENV = production
```

### Step 6: Deploy
- Click **"Create Web Service"**
- Wait 3-5 minutes
- Your site is live!

---

## 📋 What's Included

✅ Complete Flask web application
✅ User authentication (signup/login)
✅ Email template editor (write directly or use default)
✅ Email list selection (YC Startups, Business, GR)
✅ Campaign management with email limits
✅ Multi-user support (scalable to 100+ users)
✅ Production-ready configuration

---

## 🔐 Security

- **SECRET_KEY:** Already generated (use the one above or generate new)
- **FLASK_ENV:** Set to `production` for security
- **Database:** SQLite (works for 100 users, upgrade to PostgreSQL for more)

---

## 💰 Cost Estimate

**Railway:**
- Free tier: $5 credit/month (good for testing)
- Paid: $5-20/month for 100 users

**Render:**
- Free tier: Available (spins down after inactivity)
- Paid: $7/month for always-on

---

## 🎉 Next Steps After Deployment

1. ✅ Visit your live URL
2. ✅ Create a test account
3. ✅ Test all features
4. ✅ Share with your users!

---

## 🆘 Troubleshooting

**Site not loading?**
- Check Railway/Render logs
- Verify environment variables are set
- Wait 2-3 minutes after deployment

**Database errors?**
- Platform auto-creates database
- Check logs for specific errors

**Need help?**
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs

---

## 📝 Repository Info

- **GitHub:** https://github.com/mrumer-yk/emailaumation
- **Status:** ✅ Ready for deployment
- **All files:** ✅ Pushed to GitHub

---

## 🚀 Ready to Deploy!

Your code is on GitHub and ready to deploy. Follow the Railway steps above to go live in 3 minutes!

