# SendGrid Setup Guide

## Why SendGrid?
- ✅ Works on Railway (SMTP allowed)
- ✅ 100 FREE emails/day
- ✅ Better deliverability than Gmail
- ✅ No network blocks

## Steps:

### 1. Create SendGrid Account
- Go to: https://signup.sendgrid.com/
- Sign up for FREE account
- Verify your email

### 2. Create API Key
- Go to Settings → API Keys
- Click "Create API Key"
- Name: "Email Automation Tool"
- Permissions: "Full Access"
- Copy the API key (save it - you won't see it again!)

### 3. Verify Sender Email
- Go to Settings → Sender Authentication
- Click "Verify a Single Sender"
- Fill in your details (use your real email)
- Verify the email SendGrid sends you

### 4. Update Railway Environment Variables
In Railway, go to your project → Variables tab, and add:

```
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Use SendGrid in the App
Once set up, you'll use:
- SMTP Server: `smtp.sendgrid.net`
- SMTP Port: `587`
- Username: `apikey` (literally the word "apikey")
- Password: Your SendGrid API Key

## Alternative: Use SendGrid API (No SMTP needed!)
Even better - use their API instead of SMTP:
- No network blocks
- Faster
- Better error messages

