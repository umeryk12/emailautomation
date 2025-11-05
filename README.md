# Cold Email Automation Tool

An automated tool for sending personalized cold emails to companies and founders from a CSV file.

## Features

- 📧 **Bulk Email Sending**: Send personalized cold emails to multiple recipients
- 📊 **CSV Integration**: Read company and founder data from CSV files
- 🎨 **Template System**: Customizable email templates with personalization
- ⏱️ **Rate Limiting**: Configurable delays between emails to avoid spam filters
- 📝 **Logging**: Comprehensive logging of all email activities
- 🔍 **Dry Run Mode**: Test your setup without actually sending emails
- 📈 **Results Tracking**: Save results to CSV for tracking sent emails

## Setup Instructions

### 1. Install Python

Make sure you have Python 3.7+ installed on your system.

### 2. Configure Email Settings

1. Open `config.json` and update the following:
   - `sender_email`: Your email address
   - `sender_password`: Your email app password (see below)
   - `sender_name`: Your name
   - `smtp_server` and `smtp_port`: SMTP settings for your email provider

2. **For Gmail users:**
   - Enable 2-factor authentication
   - Generate an "App Password": https://myaccount.google.com/apppasswords
   - Use the app password (not your regular password) in `config.json`

3. **For other email providers:**
   - Gmail: smtp.gmail.com, port 587
   - Outlook: smtp-mail.outlook.com, port 587
   - Yahoo: smtp.mail.yahoo.com, port 587
   - Custom: Check with your email provider

### 3. Prepare Your CSV File

Create a CSV file (e.g., `companies.csv`) with the following columns:

```csv
company_name,founder_email,founder_name,website,industry,notes
TechCorp Inc,founder@techcorp.com,John Smith,https://techcorp.com,Technology,Leading software company
```

**Required columns:**
- `company_name`: Name of the company
- `founder_email`: Email address of the founder/contact

**Optional columns:**
- `founder_name`: Name of the founder (for personalization)
- `website`: Company website
- `industry`: Industry sector
- `notes`: Any additional notes

### 4. Customize Email Template

Edit `email_template.txt` to customize your email message. You can use these placeholders:

- `{company_name}`: Company name
- `{founder_name}`: Founder's name
- `{founder_email}`: Founder's email
- `{website}`: Company website
- `{industry}`: Industry sector
- `{sender_name}`: Your name (from config)

## Usage

### Basic Usage

```bash
python email_automation.py
```

This will:
- Read companies from `companies.csv` (default)
- Use settings from `config.json`
- Send emails with delays between them

### Custom CSV File

```bash
python email_automation.py --csv my_companies.csv
```

### Dry Run (Test Mode)

Test your setup without sending actual emails:

```bash
python email_automation.py --dry-run
```

### Custom Config File

```bash
python email_automation.py --config my_config.json
```

## Command Line Options

- `--csv FILE`: Specify CSV file path (default: companies.csv)
- `--config FILE`: Specify config file path (default: config.json)
- `--dry-run`: Run in test mode without sending emails

## Output

The tool will:
1. Log all activities to `email_automation.log`
2. Save results to `results_YYYYMMDD_HHMMSS.csv` with:
   - Company name
   - Email address
   - Status (sent/failed/dry_run)
   - Timestamp

## Important Notes

⚠️ **Compliance & Best Practices:**

1. **Follow Email Laws**: Ensure you comply with CAN-SPAM Act, GDPR, and other email regulations
2. **Get Consent**: Only email people who have opted in or have a legitimate business relationship
3. **Personalization**: Always personalize your emails to avoid spam filters
4. **Rate Limiting**: Use appropriate delays (30+ seconds) between emails
5. **Monitor Bounce Rates**: Keep track of bounce rates and remove invalid emails
6. **Warm Up Your Domain**: Start with small batches if using a new email domain
7. **Test First**: Always use `--dry-run` to test before sending real emails

## Troubleshooting

### Authentication Errors

- **Gmail**: Make sure you're using an App Password, not your regular password
- Check that 2-factor authentication is enabled
- Verify SMTP settings in config.json

### Emails Not Sending

- Check your internet connection
- Verify SMTP server and port settings
- Check firewall settings
- Review email_automation.log for error details

### CSV Not Loading

- Ensure CSV file exists and path is correct
- Check that CSV has required columns: `company_name` and `founder_email`
- Verify CSV encoding (should be UTF-8)

## Security

- Never commit `config.json` with real credentials to version control
- Use environment variables for sensitive data in production
- Consider using `.env` file with python-dotenv for better security

## License

This tool is provided as-is for educational and business purposes. Use responsibly and in compliance with all applicable laws.


