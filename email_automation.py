#!/usr/bin/env python3
"""
Cold Email Automation Tool
Reads company data from CSV and sends personalized cold emails
"""

import csv
import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from typing import List, Dict
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_automation.log'),
        logging.StreamHandler()
    ]
)

class EmailAutomation:
    def __init__(self, config_file='config.json'):
        """Initialize the email automation tool"""
        self.config = self.load_config(config_file)
        self.sent_count = 0
        self.failed_count = 0
        self.results = []
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration template
            default_config = {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "your_email@gmail.com",
                "sender_password": "your_app_password",
                "sender_name": "Your Name",
                "delay_between_emails": 30,  # seconds
                "max_emails_per_day": 50,
                "email_subject_template": "Partnership Opportunity - {company_name}",
                "csv_file": "companies.csv"
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            logging.warning(f"Created default config file: {config_file}. Please update it with your details.")
            return default_config
    
    def load_sent_emails(self, include_dry_run: bool = True) -> set:
        """Load list of already sent emails to avoid duplicates"""
        sent_emails = set()
        import glob
        result_files = glob.glob('results_*.csv')
        
        for file in result_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        status = row.get('status', '').lower()
                        # Include both 'sent' and 'dry_run' emails
                        if status == 'sent' or (include_dry_run and status == 'dry_run'):
                            email = row.get('email', '').strip()
                            if email:
                                sent_emails.add(email.lower())
            except:
                pass
        
        return sent_emails
    
    def load_companies_from_csv(self, csv_file: str, skip_sent: bool = True, include_dry_run: bool = True) -> List[Dict]:
        """Load company data from CSV file with flexible column mapping"""
        companies = []
        sent_emails = self.load_sent_emails(include_dry_run=include_dry_run) if skip_sent else set()
        
        if skip_sent and sent_emails:
            logging.info(f"Found {len(sent_emails)} already processed emails (including dry runs). Will skip them.")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # Get all available column names
                available_columns = reader.fieldnames or []
                
                # Flexible column mapping - try multiple possible column names
                def get_column_value(row, possible_names):
                    """Try to get value from row using multiple possible column names"""
                    for name in possible_names:
                        if name in row:
                            value = row.get(name, '').strip()
                            if value and value.upper() != 'TBD':
                                return value
                    return ''
                
                for row in reader:
                    # Map company name (try multiple variations)
                    company_name = get_column_value(row, [
                        'company_name', 'Organization Name', 'organization_name', 
                        'Company', 'company', 'Company Name'
                    ])
                    
                    # Map email (try multiple variations)
                    founder_email = get_column_value(row, [
                        'founder_email', 'Email', 'email', 'Founder Email',
                        'contact_email', 'Contact Email'
                    ])
                    
                    # Map founder name (try multiple variations)
                    founder_name = get_column_value(row, [
                        'founder_name', 'Full Name', 'full_name', 'Founder Name',
                        'Name', 'name'
                    ])
                    
                    # If Full Name not found, try combining First Name + Last Name
                    if not founder_name:
                        first_name = get_column_value(row, ['First Name', 'first_name', 'First_Name'])
                        last_name = get_column_value(row, ['Last Name', 'last_name', 'Last_Name'])
                        if first_name or last_name:
                            founder_name = f"{first_name} {last_name}".strip()
                    
                    # Map website (try multiple variations)
                    website = get_column_value(row, [
                        'website', 'Organization Domain', 'organization_domain',
                        'Website', 'domain', 'Domain', 'url', 'URL'
                    ])
                    
                    # Map industry (optional)
                    industry = get_column_value(row, [
                        'industry', 'Industry', 'sector', 'Sector', 'category', 'Category'
                    ]) or 'Technology'
                    
                    # Map notes (optional)
                    notes = get_column_value(row, [
                        'notes', 'Notes', 'batch', 'Batch', 'description', 'Description'
                    ])
                    
                    # Map status (for filtering)
                    status = get_column_value(row, [
                        'status', 'Status', 'Status'
                    ])
                    
                    # Filter: Only include ACTIVE companies
                    if status.upper() != 'ACTIVE':
                        logging.debug(f"Skipping {company_name} - Status is {status}, not ACTIVE")
                        continue
                    
                    # Validate required fields
                    if founder_email and '@' in founder_email and company_name:
                        # Skip if already sent
                        if skip_sent and founder_email.lower() in sent_emails:
                            logging.debug(f"Skipping {company_name} - already sent to {founder_email}")
                            continue
                        
                        company_data = {
                            'company_name': company_name,
                            'founder_email': founder_email,
                            'founder_name': founder_name,
                            'website': website,
                            'industry': industry,
                            'notes': notes
                        }
                        companies.append(company_data)
                    else:
                        logging.debug(f"Skipping row - missing email or company name: {company_name[:50] if company_name else 'N/A'}")
            
            logging.info(f"Loaded {len(companies)} companies from {csv_file}")
            return companies
        except FileNotFoundError:
            logging.error(f"CSV file not found: {csv_file}")
            return []
        except Exception as e:
            logging.error(f"Error reading CSV file: {e}")
            return []
    
    def load_email_template(self, template_file: str = 'email_template.txt') -> str:
        """Load email template from file"""
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Default template
            default_template = """Subject: Partnership Opportunity - {company_name}

Hi {founder_name},

I hope this email finds you well. I came across {company_name} and was impressed by your work in {industry}.

I would love to explore potential partnership opportunities that could benefit both of our organizations.

Would you be available for a brief call this week to discuss how we might collaborate?

Best regards,
{sender_name}

---
This email was sent via automated cold email tool.
"""
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(default_template)
            logging.info(f"Created default email template: {template_file}")
            return default_template
    
    def personalize_email(self, template: str, company_data: Dict, config: Dict) -> str:
        """Personalize email template with company data"""
        founder_name = company_data.get('founder_name', 'Founder')
        if not founder_name:
            founder_name = company_data.get('company_name', 'there')
        
        replacements = {
            'company_name': company_data.get('company_name', ''),
            'founder_name': founder_name,
            'founder_email': company_data.get('founder_email', ''),
            'website': company_data.get('website', ''),
            'industry': company_data.get('industry', 'Technology'),
            'sender_name': config.get('sender_name', 'Your Name'),
            'github_profile': config.get('github_profile', 'https://github.com/yourusername')
        }
        
        personalized = template
        for key, value in replacements.items():
            personalized = personalized.replace(f'{{{key}}}', str(value))
        
        return personalized
    
    def send_email(self, to_email: str, subject: str, body: str, config: Dict) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{config.get('sender_name', '')} <{config['sender_email']}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            
            # Send email
            text = msg.as_string()
            server.sendmail(config['sender_email'], to_email, text)
            server.quit()
            
            logging.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logging.error(f"SMTP Authentication failed. Check your email and password.")
            return False
        except smtplib.SMTPException as e:
            logging.error(f"SMTP error sending email to {to_email}: {e}")
            return False
        except Exception as e:
            logging.error(f"Error sending email to {to_email}: {e}")
            return False
    
    def run(self, csv_file: str = None, dry_run: bool = False, skip_sent: bool = True, include_dry_run: bool = None):
        """Run the email automation"""
        csv_file = csv_file or self.config.get('csv_file', 'companies.csv')
        template = self.load_email_template()
        
        # Default behavior: 
        # - Skip both emails that were actually sent (status='sent') and dry runs (status='dry_run')
        # - This prevents sending duplicates to emails that were already processed
        if include_dry_run is None:
            include_dry_run = True  # Skip dry_run emails to prevent duplicates
        
        companies = self.load_companies_from_csv(csv_file, skip_sent=skip_sent, include_dry_run=include_dry_run)
        
        if not companies:
            logging.error("No companies to process. Please check your CSV file.")
            return
        
        logging.info(f"Starting email automation. Dry run: {dry_run}")
        logging.info(f"Will process {len(companies)} companies")
        
        if dry_run:
            logging.info("DRY RUN MODE - No emails will be sent")
        
        for i, company in enumerate(companies, 1):
            try:
                # Personalize email
                email_body = self.personalize_email(template, company, self.config)
                subject = self.personalize_email(
                    self.config.get('email_subject_template', 'Partnership Opportunity - {company_name}'),
                    company,
                    self.config
                )
                
                # Double-check: Verify email hasn't been sent before (real-time check)
                # Check for both sent emails and dry runs to prevent duplicates
                current_sent_emails = self.load_sent_emails(include_dry_run=True)
                if company['founder_email'].lower() in current_sent_emails:
                    logging.warning(f"Skipping {company['company_name']} - Email {company['founder_email']} was already sent (duplicate detected)")
                    self.failed_count += 1
                    self.results.append({
                        'company': company['company_name'],
                        'email': company['founder_email'],
                        'status': 'skipped_duplicate',
                        'timestamp': datetime.now().isoformat()
                    })
                    continue
                
                if dry_run:
                    logging.info(f"[DRY RUN] Would send email {i}/{len(companies)}:")
                    logging.info(f"  To: {company['founder_email']}")
                    logging.info(f"  Subject: {subject}")
                    logging.info(f"  Company: {company['company_name']}")
                    self.results.append({
                        'company': company['company_name'],
                        'email': company['founder_email'],
                        'status': 'dry_run',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    # Send email
                    success = self.send_email(
                        company['founder_email'],
                        subject,
                        email_body,
                        self.config
                    )
                    
                    if success:
                        self.sent_count += 1
                        self.results.append({
                            'company': company['company_name'],
                            'email': company['founder_email'],
                            'status': 'sent',
                            'timestamp': datetime.now().isoformat()
                        })
                        # Notify user after each email is sent
                        print(f"\n{'='*60}")
                        print(f"✅ EMAIL SENT SUCCESSFULLY!")
                        print(f"   Email #{self.sent_count}/{len(companies)}")
                        print(f"   To: {company['founder_email']}")
                        print(f"   Company: {company['company_name']}")
                        print(f"   Subject: {subject[:50]}...")
                        print(f"{'='*60}\n")
                    else:
                        self.failed_count += 1
                        self.results.append({
                            'company': company['company_name'],
                            'email': company['founder_email'],
                            'status': 'failed',
                            'timestamp': datetime.now().isoformat()
                        })
                        # Notify user about failed email
                        print(f"\n{'='*60}")
                        print(f"❌ EMAIL FAILED!")
                        print(f"   Email #{i}/{len(companies)}")
                        print(f"   To: {company['founder_email']}")
                        print(f"   Company: {company['company_name']}")
                        print(f"{'='*60}\n")
                
                # Delay between emails to avoid rate limiting
                if i < len(companies) and not dry_run:
                    delay = self.config.get('delay_between_emails', 30)
                    logging.info(f"Waiting {delay} seconds before next email...")
                    time.sleep(delay)
                    
            except Exception as e:
                logging.error(f"Error processing company {company['company_name']}: {e}")
                self.failed_count += 1
        
        # Save results
        self.save_results()
        
        # Print summary
        logging.info("\n" + "="*50)
        logging.info("Email Automation Summary")
        logging.info("="*50)
        logging.info(f"Total companies processed: {len(companies)}")
        if not dry_run:
            logging.info(f"Emails sent successfully: {self.sent_count}")
            logging.info(f"Emails failed: {self.failed_count}")
        logging.info("="*50)
    
    def save_results(self):
        """Save results to CSV file"""
        results_file = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(results_file, 'w', newline='', encoding='utf-8') as f:
                if self.results:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)
            logging.info(f"Results saved to {results_file}")
        except Exception as e:
            logging.error(f"Error saving results: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cold Email Automation Tool')
    parser.add_argument('--csv', type=str, help='Path to CSV file with company data')
    parser.add_argument('--config', type=str, default='config.json', help='Path to config file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no emails sent)')
    
    args = parser.parse_args()
    
    automation = EmailAutomation(args.config)
    automation.run(csv_file=args.csv, dry_run=args.dry_run)


if __name__ == '__main__':
    main()

