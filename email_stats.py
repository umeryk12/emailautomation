#!/usr/bin/env python3
"""
Email Statistics and Resend Tool
Shows email sending statistics and generates lists for resending
"""

import csv
import os
import glob
from collections import defaultdict
from datetime import datetime

def load_all_results():
    """Load all results from result CSV files"""
    all_results = []
    result_files = glob.glob('results_*.csv')
    
    for file in sorted(result_files, reverse=True):  # Most recent first
        try:
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['source_file'] = file
                    all_results.append(row)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    return all_results

def get_statistics():
    """Get email sending statistics"""
    results = load_all_results()
    
    if not results:
        print("No results found. No emails have been sent yet.")
        return
    
    stats = {
        'total': len(results),
        'sent': 0,
        'failed': 0,
        'dry_run': 0,
        'unique_emails': set(),
        'unique_companies': set(),
        'by_date': defaultdict(lambda: {'sent': 0, 'failed': 0})
    }
    
    for result in results:
        status = result.get('status', '').lower()
        email = result.get('email', '')
        company = result.get('company', '')
        timestamp = result.get('timestamp', '')
        
        if status == 'sent':
            stats['sent'] += 1
        elif status == 'failed':
            stats['failed'] += 1
        elif status == 'dry_run':
            stats['dry_run'] += 1
        
        if email:
            stats['unique_emails'].add(email)
        if company:
            stats['unique_companies'].add(company)
        
        # Group by date
        if timestamp:
            try:
                date_str = timestamp.split('T')[0]  # Get date part
                if status == 'sent':
                    stats['by_date'][date_str]['sent'] += 1
                elif status == 'failed':
                    stats['by_date'][date_str]['failed'] += 1
            except:
                pass
    
    return stats

def print_statistics():
    """Print email statistics"""
    stats = get_statistics()
    
    if not stats:
        return
    
    print("\n" + "="*70)
    print("EMAIL SENDING STATISTICS")
    print("="*70)
    print(f"Total emails processed: {stats['total']}")
    print(f"  [SUCCESS] Successfully sent: {stats['sent']}")
    print(f"  [FAILED] Failed: {stats['failed']}")
    print(f"  [TEST] Dry run (test): {stats['dry_run']}")
    print(f"\nUnique companies: {len(stats['unique_companies'])}")
    print(f"Unique emails: {len(stats['unique_emails'])}")
    
    if stats['by_date']:
        print("\nBreakdown by Date:")
        for date in sorted(stats['by_date'].keys(), reverse=True):
            sent = stats['by_date'][date]['sent']
            failed = stats['by_date'][date]['failed']
            print(f"  {date}: {sent} sent, {failed} failed")
    
    print("="*70 + "\n")

def create_resend_list(output_file='emails_to_resend.csv'):
    """Create a CSV file with failed emails that need to be resent"""
    results = load_all_results()
    
    # Get all failed emails
    failed_emails = {}
    for result in results:
        if result.get('status', '').lower() == 'failed':
            email = result.get('email', '')
            company = result.get('company', '')
            if email and company:
                failed_emails[email] = {
                    'company_name': company,
                    'founder_email': email,
                    'founder_name': '',  # Will need to get from original CSV
                    'website': '',
                    'industry': 'Technology',
                    'notes': 'Failed email - needs resend'
                }
    
    if not failed_emails:
        print("No failed emails found. All emails were sent successfully!")
        return
    
    # Try to get additional info from original CSV
    try:
        with open('ycombinatoremails.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('Email', '').strip()
                if email in failed_emails:
                    failed_emails[email]['founder_name'] = row.get('Full Name', '').strip()
                    failed_emails[email]['website'] = row.get('Organization Domain', '').strip()
                    failed_emails[email]['industry'] = 'Technology'
    except:
        pass
    
    # Save to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['company_name', 'founder_email', 'founder_name', 'website', 'industry', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(failed_emails.values())
    
    print(f"\n[SUCCESS] Created resend list: {output_file}")
    print(f"  Total emails to resend: {len(failed_emails)}\n")

def create_sent_list(output_file='emails_sent.csv'):
    """Create a CSV file with all successfully sent emails"""
    results = load_all_results()
    
    sent_emails = {}
    for result in results:
        if result.get('status', '').lower() == 'sent':
            email = result.get('email', '')
            company = result.get('company', '')
            if email and company:
                sent_emails[email] = {
                    'company_name': company,
                    'founder_email': email,
                    'timestamp': result.get('timestamp', '')
                }
    
    if not sent_emails:
        print("No sent emails found.")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['company_name', 'founder_email', 'timestamp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sent_emails.values())
    
    print(f"[SUCCESS] Created sent emails list: {output_file}")
    print(f"  Total emails sent: {len(sent_emails)}\n")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Email Statistics and Resend Tool')
    parser.add_argument('--stats', action='store_true', help='Show email statistics')
    parser.add_argument('--resend', action='store_true', help='Create list of failed emails to resend')
    parser.add_argument('--sent', action='store_true', help='Create list of successfully sent emails')
    parser.add_argument('--all', action='store_true', help='Show stats and create all lists')
    
    args = parser.parse_args()
    
    if args.all or args.stats:
        print_statistics()
    
    if args.all or args.resend:
        create_resend_list()
    
    if args.all or args.sent:
        create_sent_list()
    
    if not any([args.stats, args.resend, args.sent, args.all]):
        # Default: show stats
        print_statistics()
        print("\nUsage:")
        print("  python email_stats.py --stats    # Show statistics")
        print("  python email_stats.py --resend   # Create resend list")
        print("  python email_stats.py --sent     # Create sent emails list")
        print("  python email_stats.py --all      # Do everything\n")

if __name__ == '__main__':
    main()

