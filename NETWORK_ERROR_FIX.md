# Network Error Fix: OSError [Errno 101] Network is unreachable

## What Happened?

You saw this error in the Railway logs:
```
OSError: [Errno 101] Network is unreachable
```

## This is NOT a database problem!

This is a **networking issue**. Railway's servers cannot connect to Gmail's SMTP server (`smtp.gmail.com:587`).

## Why It Happens

Many hosting platforms (Railway, Heroku, etc.) **block port 587** to prevent spam and abuse. This is standard security practice.

## The Solution: Port 465 (SSL)

✅ **I've fixed this by adding support for port 465 (SSL)**

### What Changed:

1. **Email Automation Script** (`email_automation.py`):
   - Now supports both port 587 (TLS) and port 465 (SSL)
   - Automatically uses `SMTP_SSL` for port 465
   - Keeps using `SMTP` with `starttls()` for port 587

2. **Dashboard** (`templates/dashboard.html`):
   - Changed port input to dropdown
   - **Defaults to port 465 (SSL)** - recommended for hosting
   - Option to use port 587 (TLS) if needed

### How to Test:

1. **Wait 2 minutes** for Railway to redeploy
2. **Refresh the dashboard page**
3. **Go to Email Configuration section**
4. **Re-save your settings** (port should now be 465 by default)
5. **Start a new campaign**

### Expected Results:

With port 465, you should see in the logs:
```
✅ Connected to SMTP server using SSL (port 465)
✅ Login successful!
✅ Email sent to xxx@yyy.com
```

## Alternative: Use SendGrid

If port 465 **still** doesn't work on Railway, use SendGrid:
- ✅ FREE 100 emails/day
- ✅ Works on all hosting platforms
- ✅ Better deliverability
- See `SENDGRID_SETUP.md` for instructions

## Summary

- ❌ Problem: Port 587 blocked on Railway
- ✅ Solution: Use port 465 (SSL)
- 🎯 Status: **DEPLOYED** - test now!

