# SendGrid Quick Setup - 5 Minutes ⚡

Railway blocks Gmail SMTP, but **SendGrid works perfectly** (FREE 100 emails/day).

## Step 1: Sign Up for SendGrid (2 minutes)
1. Go to: https://signup.sendgrid.com/
2. Fill in your details
3. Verify your email

## Step 2: Create API Key (1 minute)
1. Login to SendGrid: https://app.sendgrid.com/
2. Go to: **Settings** → **API Keys**
3. Click **"Create API Key"**
4. Name: `Email Automation Tool`
5. Permissions: **"Full Access"**
6. Click **"Create & View"**
7. **COPY THE API KEY** (starts with `SG.`)
   - ⚠️ You won't see it again!

## Step 3: Verify Your Sender Email (1 minute)
1. In SendGrid, go to: **Settings** → **Sender Authentication**
2. Click **"Verify a Single Sender"**
3. Fill in:
   - From Name: `Your Name`
   - From Email: `your.email@gmail.com`
   - Address, City, etc. (required by SendGrid)
4. Click **"Create"**
5. **Check your inbox** and click the verification link

## Step 4: Use in Your App (1 minute)
1. Go to your dashboard: https://web-production-8a68.up.railway.app/
2. In **Email Configuration**:
   - Select **"SendGrid (Recommended for Railway)"**
   - **SendGrid API Key**: Paste the API key from Step 2 (starts with `SG.`)
   - **From Email**: Use the email you verified in Step 3
   - **Sender Name**: Your name
3. Click **"Save Email Settings"**
4. Start a campaign!

## Expected Behavior
- ✅ Emails send instantly (no port blocks!)
- ✅ Better deliverability than Gmail
- ✅ FREE 100 emails/day
- ✅ Works on Railway, Heroku, any platform

## Troubleshooting
- **"Invalid API Key"**: Make sure you copied the entire key (starts with `SG.`)
- **"Sender not verified"**: Check your inbox for SendGrid verification email
- **"Daily limit exceeded"**: Free tier is 100 emails/day

