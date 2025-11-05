# Email Sending Troubleshooting Guide

## Why Emails Might Not Be Sent

### 1. Check Email Configuration ✅

**Make sure you've:**
- Entered your email address in "Email Configuration"
- Entered your **Gmail App Password** (NOT your regular password)
- Clicked "Save Email Settings"
- See a green success message

**Get Gmail App Password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Enable 2-Step Verification if needed
3. Generate App Password
4. Copy the 16-character password
5. Paste it in the "App Password" field

### 2. Check Campaign Status

After starting a campaign:
- Go to "Recent Campaigns" section
- Check the status:
  - **Running** = Campaign is in progress
  - **Completed** = Finished (check sent count)
  - **Failed** = Something went wrong

### 3. Check Railway Logs

**To see what's happening:**
1. Go to Railway dashboard
2. Click on your project
3. Go to "Logs" tab
4. Look for:
   - "Starting to send X emails"
   - "Connecting to SMTP server"
   - "Email sent successfully" ✅
   - "SMTP Authentication failed" ❌

### 4. Common Issues

**Issue: "SMTP Authentication failed"**
- **Solution:** Use Gmail App Password, not regular password
- Make sure 2-Step Verification is enabled

**Issue: "No companies to process"**
- **Solution:** Check CSV file exists and has valid emails
- Make sure email list is selected correctly

**Issue: Campaign shows "Failed"**
- **Solution:** Check Railway logs for error details
- Verify email settings are saved correctly

**Issue: Emails show as "sent" but not received**
- **Solution:** Check spam folder
- Verify recipient email is correct
- Check Gmail sending limits (500/day)

### 5. Test Steps

1. **Configure Email:**
   - Enter: `your.email@gmail.com`
   - Enter: Your Gmail App Password
   - Click "Save Email Settings"
   - Should see: "Email configured! You can now start campaigns."

2. **Start Small Test:**
   - Set Email Limit: `5` (test with 5 emails first)
   - Choose email list
   - Write a simple template
   - Click "Start Campaign"

3. **Check Results:**
   - Wait 1-2 minutes
   - Check "Recent Campaigns"
   - See sent count update
   - Check your email inbox

### 6. Verify Email Settings Are Saved

After saving:
1. Refresh the page
2. Email Configuration should show your email
3. If it's empty, settings weren't saved (check for errors)

### 7. Check CSV Files

Make sure:
- `ycombinatoremails.csv` exists (for YC Startups)
- `companies.csv` exists (for Business Emails)
- Files have valid email addresses

### 8. Common Errors in Logs

**"User has not configured SMTP credentials"**
- → Save email settings first

**"SMTP Authentication failed"**
- → Use App Password, enable 2-Step Verification

**"No companies to process"**
- → Check CSV file exists and has valid data

**"Error sending email"**
- → Check Railway logs for specific error

---

## Quick Checklist

- [ ] Email address entered
- [ ] Gmail App Password entered (not regular password)
- [ ] Settings saved successfully
- [ ] Email list selected (YC/Business/GR)
- [ ] Template written or selected
- [ ] Email limit set (start with 5 for testing)
- [ ] Campaign started
- [ ] Check campaign status in dashboard
- [ ] Check Railway logs for errors

---

## Still Not Working?

1. Check Railway logs for specific errors
2. Verify Gmail App Password is correct
3. Test with email limit of 1-2 emails first
4. Check spam folder
5. Verify recipient emails are valid

---

## Test Email Sending

1. Start a campaign with limit: **1**
2. Use a test email you control
3. Check if it arrives
4. If successful, increase limit gradually

