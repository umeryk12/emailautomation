# IMPORTANT: Email Setup Instructions

## Before Sending Emails - You MUST Do This First!

### 1. Set Up Gmail App Password

Your email `mrumeryk@gmail.com` is configured, but you NEED to create a Gmail App Password:

**Steps:**
1. Go to: https://myaccount.google.com/apppasswords
2. Sign in with your Gmail account
3. Enable 2-Step Verification if you haven't already (required for App Passwords)
4. Click "Select app" → Choose "Mail"
5. Click "Select device" → Choose "Other (Custom name)" → Type "Email Automation"
6. Click "Generate"
7. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)
8. Paste it into `config.json` replacing `"your_app_password"` (remove spaces)

**Example:**
```json
"sender_password": "abcdefghijklmnop",
```

### 2. Update Your Name

Edit `config.json` and change:
```json
"sender_name": "Your Name",
```
To your actual name, for example:
```json
"sender_name": "Mrumer YK",
```

### 3. Important Considerations

⚠️ **Sending 7,282 emails will take:**
- With 30-second delays: ~60 hours (2.5 days) of continuous running
- Gmail has daily sending limits (around 500 emails/day for regular accounts)
- You may hit rate limits or spam filters

**Recommendations:**
1. **Start Small**: Test with 10-20 emails first
2. **Filter Your CSV**: Only send to companies you're truly interested in
3. **Adjust Delay**: You might want to increase `delay_between_emails` to 60+ seconds
4. **Monitor**: Watch the logs for any errors or rate limiting

### 4. How to Send

**Test with a small batch first:**
```bash
# Create a small test CSV with just 5 companies
python email_automation.py --csv small_test.csv --dry-run
```

**Send to all (after setting up App Password):**
```bash
python email_automation.py --csv ycombinatoremails.csv
```

### 5. Troubleshooting

**If you get "SMTP Authentication failed":**
- Check that you're using the App Password (not your regular Gmail password)
- Make sure 2-Step Verification is enabled
- The App Password should be 16 characters with no spaces

**If emails are being rejected:**
- Gmail may be rate-limiting you
- Try sending in smaller batches
- Increase the delay between emails

**Monitor the log file:**
- Check `email_automation.log` for detailed information about each email sent


