# Email Tracking and Resending Guide

## Email Statistics Tool

Use `email_stats.py` to track your email sending progress and create lists for resending.

### View Statistics

```bash
python email_stats.py --stats
```

This shows:
- Total emails processed
- Successfully sent emails
- Failed emails
- Test/dry run emails
- Unique companies and emails
- Breakdown by date

### Create Resend List

To create a CSV file with all failed emails that need to be resent:

```bash
python email_stats.py --resend
```

This creates `emails_to_resend.csv` with all emails that failed.

### Create Sent Emails List

To create a CSV file with all successfully sent emails:

```bash
python email_stats.py --sent
```

This creates `emails_sent.csv` with all emails that were sent successfully.

### Do Everything

```bash
python email_stats.py --all
```

This will show statistics and create both lists.

## Resending Failed Emails

1. **Generate resend list:**
   ```bash
   python email_stats.py --resend
   ```

2. **Resend failed emails:**
   ```bash
   python email_automation.py --csv emails_to_resend.csv
   ```

## Automatic Duplicate Prevention

The email automation tool now automatically:
- **Skips already sent emails** - Won't send duplicates
- **Tracks sent emails** - Reads from all `results_*.csv` files
- **Prevents resending** - Only sends to emails that haven't been sent before

### To Resend to Already Sent Emails

If you want to resend to emails that were already sent (not recommended):

```bash
python email_automation.py --csv ycombinatoremails.csv --allow-resend
```

Note: You'll need to modify the script to add `--allow-resend` flag if you want this feature.

## Current Statistics

Based on your results files:
- **Total processed:** Check with `python email_stats.py --stats`
- **Sent:** Will show actual sent count
- **Failed:** Will show failed count
- **Ready to send:** Shows remaining emails to send

## Example Output

```
======================================================================
EMAIL SENDING STATISTICS
======================================================================
Total emails processed: 20508
  [SUCCESS] Successfully sent: 0
  [FAILED] Failed: 0
  [TEST] Dry run (test): 20508

Unique companies: 3281
Unique emails: 7260
======================================================================
```

## Files Created

- `emails_to_resend.csv` - List of failed emails to resend
- `emails_sent.csv` - List of successfully sent emails
- `results_YYYYMMDD_HHMMSS.csv` - Detailed results for each run


