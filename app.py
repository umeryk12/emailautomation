#!/usr/bin/env python3
"""
Email Automation Tool - Land Jobs, Marketing & Cold Emails
Multi-user platform for automated email campaigns to help you land jobs, grow your network, and automate cold emails
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import csv
from datetime import datetime
from typing import Dict, List
import threading
import time
import sys
import logging

# Configure logging to stdout so it appears in Railway logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import the email automation class
from email_automation import EmailAutomation

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# Use DATABASE_URL if provided (for production), otherwise SQLite
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    # For Railway, use PostgreSQL if available, otherwise fallback to SQLite with proper path
    database_url = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'email_automation.db')
else:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'user_templates'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('user_data', exist_ok=True)
os.makedirs('instance', exist_ok=True)  # For SQLite database

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Email SMTP settings (encrypted/optional)
    smtp_email = db.Column(db.String(120), nullable=True)
    smtp_password = db.Column(db.String(255), nullable=True)  # Store app password (encrypted in production)
    smtp_server = db.Column(db.String(100), default='smtp.gmail.com')
    smtp_port = db.Column(db.Integer, default=587)
    sender_name = db.Column(db.String(100), nullable=True)
    email_provider = db.Column(db.String(20), default='gmail')  # 'gmail' or 'sendgrid'
    sendgrid_api_key = db.Column(db.String(200), nullable=True)
    
    # Relationships
    templates = db.relationship('EmailTemplate', backref='user', lazy=True, cascade='all, delete-orphan')
    campaigns = db.relationship('Campaign', backref='user', lazy=True, cascade='all, delete-orphan')

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    template_content = db.Column(db.Text, nullable=False)
    subject_template = db.Column(db.String(200), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email_list_type = db.Column(db.String(50), nullable=False)  # 'yc_startups', 'business_emails', 'gr'
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'), nullable=True)
    custom_template_content = db.Column(db.Text, nullable=True)  # For directly written templates
    custom_subject_template = db.Column(db.String(200), nullable=True)
    email_limit = db.Column(db.Integer, default=0)  # 0 means no limit
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    total_emails = db.Column(db.Integer, default=0)
    sent_emails = db.Column(db.Integer, default=0)
    failed_emails = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('signup'))

@app.route('/health')
def health():
    return 'ok', 200

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        # Create default template for user
        default_template = EmailTemplate(
            user_id=user.id,
            name='Default Template',
            template_content=get_default_template(),
            subject_template='Partnership Opportunity - {company_name}',
            is_default=True
        )
        db.session.add(default_template)
        db.session.commit()
        
        # Auto-login user
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully! Starting email automation setup...',
            'redirect': url_for('dashboard')
        })
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect': url_for('dashboard')
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signup'))

@app.route('/dashboard')
@login_required
def dashboard():
    campaigns = Campaign.query.filter_by(user_id=current_user.id).order_by(Campaign.created_at.desc()).limit(10).all()
    templates = EmailTemplate.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', campaigns=campaigns, templates=templates)

@app.route('/api/templates', methods=['GET', 'POST'])
@login_required
def templates():
    if request.method == 'GET':
        templates = EmailTemplate.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'success': True,
            'templates': [{
                'id': t.id,
                'name': t.name,
                'subject_template': t.subject_template,
                'template_content': t.template_content,
                'is_default': t.is_default,
                'created_at': t.created_at.isoformat()
            } for t in templates]
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name', 'Custom Template')
        template_content = data.get('template_content', '')
        subject_template = data.get('subject_template', 'Partnership Opportunity - {company_name}')
        
        if not template_content:
            return jsonify({'success': False, 'message': 'Template content is required'}), 400
        
        template = EmailTemplate(
            user_id=current_user.id,
            name=name,
            template_content=template_content,
            subject_template=subject_template
        )
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Template saved successfully',
            'template_id': template.id
        })

@app.route('/api/templates/<int:template_id>', methods=['PUT', 'DELETE'])
@login_required
def template_detail(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    
    if template.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if request.method == 'PUT':
        data = request.get_json()
        template.name = data.get('name', template.name)
        template.template_content = data.get('template_content', template.template_content)
        template.subject_template = data.get('subject_template', template.subject_template)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Template updated'})
    
    elif request.method == 'DELETE':
        db.session.delete(template)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Template deleted'})

@app.route('/api/upload-template', methods=['POST'])
@login_required
def upload_template():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{current_user.id}_{filename}")
        file.save(filepath)
        
        # Read template content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract subject if present
        subject_template = 'Partnership Opportunity - {company_name}'
        if content.startswith('Subject:'):
            lines = content.split('\n', 1)
            subject_line = lines[0].replace('Subject:', '').strip()
            if '{company_name}' in subject_line:
                subject_template = subject_line
            content = lines[1] if len(lines) > 1 else content
        
        # Save template to database
        template = EmailTemplate(
            user_id=current_user.id,
            name=f'Uploaded: {filename}',
            template_content=content,
            subject_template=subject_template
        )
        db.session.add(template)
        db.session.commit()
        
        # Clean up file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Template uploaded successfully',
            'template_id': template.id
        })

@app.route('/api/campaigns', methods=['POST'])
@login_required
def create_campaign():
    data = request.get_json()
    email_list_type = data.get('email_list_type')  # 'yc_startups', 'business_emails', 'gr'
    template_id = data.get('template_id')
    custom_template = data.get('custom_template')  # Directly written template
    custom_subject = data.get('custom_subject', 'Partnership Opportunity - {company_name}')
    email_limit = data.get('email_limit', 0)  # 0 means no limit
    save_template = data.get('save_template', False)  # Save custom template to database
    
    if not email_list_type:
        return jsonify({'success': False, 'message': 'Email list type is required'}), 400
    
    # Handle custom template (directly written)
    template = None
    custom_template_content = None
    custom_subject_template = None
    
    if custom_template and custom_template.strip():
        # User wrote a custom template
        custom_template_content = custom_template.strip()
        custom_subject_template = custom_subject
        
        # Optionally save to database
        if save_template:
            template = EmailTemplate(
                user_id=current_user.id,
                name=f"Campaign Template - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                template_content=custom_template_content,
                subject_template=custom_subject_template
            )
            db.session.add(template)
            db.session.commit()
    elif template_id:
        # Use saved template
        template = EmailTemplate.query.get(template_id)
        if template and template.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized template'}), 403
    else:
        # Use default template
        template = EmailTemplate.query.filter_by(user_id=current_user.id, is_default=True).first()
    
    if not template and not custom_template_content:
        return jsonify({'success': False, 'message': 'No template found. Please write a template or select one.'}), 400
    
    # Create campaign
    campaign = Campaign(
        user_id=current_user.id,
        name=f"Campaign - {email_list_type} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        email_list_type=email_list_type,
        template_id=template.id if template else None,
        custom_template_content=custom_template_content,
        custom_subject_template=custom_subject_template,
        email_limit=int(email_limit) if email_limit else 0,
        status='pending'
    )
    db.session.add(campaign)
    db.session.commit()
    
    logger.info(f"✅ Campaign {campaign.id} created for user {current_user.id} ({current_user.email})")
    logger.info(f"   Email list: {email_list_type}, Limit: {email_limit}")
    logger.info(f"   User SMTP: {current_user.smtp_email}, Has password: {bool(current_user.smtp_password)}")
    
    # Start campaign in background thread
    try:
        thread = threading.Thread(target=run_campaign, args=(campaign.id,))
        thread.daemon = True
        thread.start()
        logger.info(f"✅ Background thread started for campaign {campaign.id}")
    except Exception as e:
        logger.error(f"❌ Failed to start background thread: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return jsonify({
        'success': True,
        'message': 'Campaign started',
        'campaign_id': campaign.id
    })

@app.route('/api/campaigns/<int:campaign_id>', methods=['GET'])
@login_required
def get_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    return jsonify({
        'success': True,
        'campaign': {
            'id': campaign.id,
            'name': campaign.name,
            'email_list_type': campaign.email_list_type,
            'status': campaign.status,
            'total_emails': campaign.total_emails,
            'sent_emails': campaign.sent_emails,
            'failed_emails': campaign.failed_emails,
            'created_at': campaign.created_at.isoformat(),
            'started_at': campaign.started_at.isoformat() if campaign.started_at else None,
            'completed_at': campaign.completed_at.isoformat() if campaign.completed_at else None
        }
    })

@app.route('/api/debug/csv-check', methods=['GET'])
@login_required
def debug_csv_check():
    """Debug endpoint to check CSV files"""
    import os
    
    csv_files = {
        'ycombinatoremails.csv': os.path.exists('ycombinatoremails.csv'),
        'companies.csv': os.path.exists('companies.csv')
    }
    
    csv_info = {}
    for filename, exists in csv_files.items():
        if exists:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    csv_info[filename] = {
                        'exists': True,
                        'rows': len(lines) - 1,  # Exclude header
                        'header': lines[0].strip() if lines else 'empty'
                    }
            except Exception as e:
                csv_info[filename] = {
                    'exists': True,
                    'error': str(e)
                }
        else:
            csv_info[filename] = {'exists': False}
    
    return jsonify({
        'success': True,
        'csv_files': csv_info,
        'cwd': os.getcwd(),
        'user': {
            'smtp_email': current_user.smtp_email,
            'has_smtp_password': bool(current_user.smtp_password),
            'smtp_server': current_user.smtp_server,
            'smtp_port': current_user.smtp_port
        }
    })

@app.route('/api/campaigns', methods=['GET'])
@login_required
def list_campaigns():
    campaigns = Campaign.query.filter_by(user_id=current_user.id).order_by(Campaign.created_at.desc()).all()
    return jsonify({
        'success': True,
        'campaigns': [{
            'id': c.id,
            'name': c.name,
            'email_list_type': c.email_list_type,
            'status': c.status,
            'total_emails': c.total_emails,
            'sent_emails': c.sent_emails,
            'failed_emails': c.failed_emails,
            'created_at': c.created_at.isoformat()
        } for c in campaigns]
    })

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def email_settings():
    """Get or update user's email SMTP settings"""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'settings': {
                'smtp_email': current_user.smtp_email or '',
                'smtp_server': current_user.smtp_server or 'smtp.gmail.com',
                'smtp_port': current_user.smtp_port or 587,
                'sender_name': current_user.sender_name or current_user.username,
                'has_password': bool(current_user.smtp_password)
            }
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Update user settings
        smtp_email = data.get('smtp_email', '').strip()
        smtp_password = data.get('smtp_password', '').strip()
        smtp_server = data.get('smtp_server', 'smtp.gmail.com').strip()
        smtp_port = data.get('smtp_port', 587)
        sender_name = data.get('sender_name', current_user.username).strip()
        
        # Update fields
        if smtp_email:
            current_user.smtp_email = smtp_email
        if smtp_password:  # Only update if password is provided
            current_user.smtp_password = smtp_password  # App password
        current_user.smtp_server = smtp_server
        try:
            current_user.smtp_port = int(smtp_port)
        except (ValueError, TypeError):
            current_user.smtp_port = 587
        if sender_name:
            current_user.sender_name = sender_name
        
        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Email settings saved successfully!'
            })
        except Exception as e:
            db.session.rollback()
            import traceback
            error_msg = str(e)
            print(f"Error saving settings: {error_msg}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'message': f'Error saving settings: {error_msg}'
            }), 500

def get_email_list_path(email_list_type: str) -> str:
    """Get the CSV file path for the selected email list type"""
    mapping = {
        'yc_startups': 'ycombinatoremails.csv',
        'business_emails': 'companies.csv',
        'gr': 'companies.csv'  # Placeholder - you can add a GR-specific CSV later
    }
    return mapping.get(email_list_type, 'companies.csv')

def run_campaign(campaign_id: int):
    """Run email campaign in background thread"""
    try:
        logger.info(f"🚀 run_campaign() called for campaign {campaign_id}")
        logger.info(f"   Thread ID: {threading.current_thread().ident}")
        
        # IMPORTANT: Keep app context for entire function
        with app.app_context():
            campaign = Campaign.query.get(campaign_id)
            if not campaign:
                logger.error(f"❌ Campaign {campaign_id} not found in database")
                return
            
            logger.info(f"✅ Campaign {campaign_id} found in database")
            
            # Get user from campaign
            user = User.query.get(campaign.user_id)
            if not user:
                campaign.status = 'failed'
                db.session.commit()
                logger.error(f"❌ Campaign {campaign_id}: User {campaign.user_id} not found")
                return
            
            logger.info(f"✅ User {user.id} ({user.email}) found for campaign {campaign_id}")
            
            campaign.status = 'running'
            campaign.started_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"🏃 Campaign {campaign_id}: Status set to 'running'")
            logger.info(f"   User: {user.username}")
            logger.info(f"   Email list type: {campaign.email_list_type}")
            
            try:
                # Get template - either from database or custom
                template_content = None
                subject_template = None
                
                if campaign.custom_template_content:
                    # Use custom template written directly
                    template_content = campaign.custom_template_content
                    subject_template = campaign.custom_subject_template or 'Partnership Opportunity - {company_name}'
                else:
                    # Get template from database
                    template = EmailTemplate.query.get(campaign.template_id)
                    if not template:
                        campaign.status = 'failed'
                        db.session.commit()
                        return
                    template_content = template.template_content
                    subject_template = template.subject_template
                
                # Get email list file
                csv_file = get_email_list_path(campaign.email_list_type)
                logger.info(f"📄 Campaign {campaign_id}: Using CSV file: {csv_file}")
                logger.info(f"   Current directory: {os.getcwd()}")
                logger.info(f"   CSV exists: {os.path.exists(csv_file)}")
                
                # Check if CSV file exists
                if not os.path.exists(csv_file):
                    campaign.status = 'failed'
                    campaign.failed_emails = 1
                    db.session.commit()
                    logger.error(f"❌ Campaign {campaign_id} failed: CSV file not found: {csv_file}")
                    logger.error(f"   Files in directory: {os.listdir('.')}")
                    return
                
                # Check if user has email credentials configured (SMTP or SendGrid)
                if user.email_provider == 'sendgrid':
                    if not user.sendgrid_api_key or not user.smtp_email:
                        campaign.status = 'failed'
                        campaign.failed_emails = 1
                        db.session.commit()
                        logger.error(f"❌ Campaign {campaign_id} failed: User has not configured SendGrid credentials")
                        return
                else:
                    if not user.smtp_email or not user.smtp_password:
                        campaign.status = 'failed'
                        campaign.failed_emails = 1
                        db.session.commit()
                        logger.error(f"❌ Campaign {campaign_id} failed: User has not configured SMTP credentials")
                        return
                
                logger.info(f"✅ Campaign {campaign_id}: Email provider: {user.email_provider}")
                
                # Create user-specific config
                user_config = {
                    'email_provider': user.email_provider or 'gmail',
                    'smtp_server': user.smtp_server or 'smtp.gmail.com',
                    'smtp_port': user.smtp_port or 587,
                    'sender_email': user.smtp_email,
                    'sender_password': user.smtp_password,  # User's app password
                    'sendgrid_api_key': user.sendgrid_api_key,
                    'sender_name': user.sender_name or user.username,
                    'delay_between_emails': 5,
                    'max_emails_per_day': 50,
                    'email_subject_template': subject_template,
                    'csv_file': csv_file
                }
                
                # Save user config
                config_file = f'user_data/user_{campaign.user_id}_config.json'
                with open(config_file, 'w') as f:
                    json.dump(user_config, f, indent=4)
                
                # Save user template
                template_file = f'user_data/user_{campaign.user_id}_template_{campaign.id}.txt'
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                
                # Initialize email automation with the config file
                automation = EmailAutomation(config_file=config_file)
                
                # Reload config to ensure it has the latest SMTP credentials
                automation.config = user_config
                
                # Override template loading
                automation.load_email_template = lambda: open(template_file, 'r', encoding='utf-8').read()
                
                # Load companies - don't skip dry_run emails for new campaigns
                # Only skip actually sent emails
                companies = automation.load_companies_from_csv(csv_file, skip_sent=False, include_dry_run=False)
                
                # Apply email limit if set
                if campaign.email_limit and campaign.email_limit > 0:
                    companies = companies[:campaign.email_limit]
                
                if not companies:
                    campaign.status = 'failed'
                    campaign.failed_emails = 1
                    db.session.commit()
                    logger.error(f"❌ Campaign {campaign_id} failed: No companies to process")
                    return
                
                campaign.total_emails = len(companies)
                db.session.commit()
                
                # Log that we're about to send emails
                logger.info(f"📧 Campaign {campaign_id}: Starting to send {len(companies)} emails")
                logger.info(f"   Using email: {user.smtp_email}")
                logger.info(f"   SMTP server: {user.smtp_server}:{user.smtp_port}")
                logger.info(f"   CSV file: {csv_file}")
                logger.info(f"   Companies loaded: {len(companies)}")
                logger.info(f"   DRY RUN = False (will actually send emails)")
                
                # Run automation with user's SMTP credentials (actual sending)
                # Set include_dry_run=False so we process all emails, not just new ones
                logger.info(f"🎯 Campaign {campaign_id}: Calling automation.run()...")
                
                # Progress callback to update campaign counts live
                def on_progress(sent_count: int, failed_count: int, company: dict):
                    try:
                        campaign.sent_emails = sent_count
                        campaign.failed_emails = failed_count
                        db.session.commit()
                        logger.info(f"📊 Campaign {campaign_id}: Progress - Sent: {sent_count}, Failed: {failed_count}")
                    except Exception as e:
                        logger.error(f"❌ Progress update failed: {e}")
                        db.session.rollback()
                
                automation.run(
                    csv_file=csv_file,
                    dry_run=False,
                    skip_sent=False,
                    include_dry_run=False,
                    on_progress=on_progress
                )
                
                logger.info(f"✅ Campaign {campaign_id}: Automation completed")
                logger.info(f"   Sent count: {automation.sent_count}")
                logger.info(f"   Failed count: {automation.failed_count}")
                
                # Update campaign status
                campaign.sent_emails = automation.sent_count
                campaign.failed_emails = automation.failed_count
                
                # Save results to CSV for tracking
                if automation.results:
                    results_file = f"user_data/user_{campaign.user_id}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    with open(results_file, 'w', newline='', encoding='utf-8') as f:
                        if automation.results:
                            writer = csv.DictWriter(f, fieldnames=automation.results[0].keys())
                            writer.writeheader()
                            writer.writerows(automation.results)
                    logger.info(f"Campaign {campaign_id}: Results saved to {results_file}")
                
                logger.info(f"Campaign {campaign_id}: Sent {automation.sent_count}, Failed {automation.failed_count}")
                
                if automation.sent_count > 0 or automation.failed_count == 0:
                    campaign.status = 'completed'
                else:
                    campaign.status = 'failed'
                
                campaign.completed_at = datetime.utcnow()
                db.session.commit()
                
            except Exception as e:
                import traceback
                error_msg = str(e)
                traceback_str = traceback.format_exc()
                logger.error(f"❌❌❌ Campaign {campaign_id} EXCEPTION: {error_msg}")
                logger.error(traceback_str)
                
                campaign.status = 'failed'
                campaign.failed_emails = campaign.total_emails if campaign.total_emails > 0 else 1
                db.session.commit()
                
                # Log error to file for debugging
                try:
                    error_log = f"user_data/user_{campaign.user_id}_error_{campaign_id}.log"
                    with open(error_log, 'w') as f:
                        f.write(f"Campaign {campaign_id} Error:\n{error_msg}\n\n{traceback_str}")
                except:
                    pass
                    
    except Exception as e:
        # Catch ANY exception in the thread
        import traceback
        logger.error(f"❌❌❌ THREAD EXCEPTION for campaign {campaign_id}: {e}")
        logger.error(traceback.format_exc())

def get_default_template() -> str:
    """Get default email template"""
    if os.path.exists('email_template.txt'):
        with open('email_template.txt', 'r', encoding='utf-8') as f:
            return f.read()
    return """Subject: Partnership Opportunity - {company_name}

Hi {founder_name},

I hope this email finds you well. I came across {company_name} and was impressed by your work in {industry}.

I would love to explore potential partnership opportunities that could benefit both of our organizations.

Would you be available for a brief call this week to discuss how we might collaborate?

Best regards,
{sender_name}
"""

# Initialize database and handle schema updates
def init_database():
    """Initialize database and handle schema updates"""
    with app.app_context():
        try:
            # Create all tables (only creates if they don't exist)
            # This will NOT error if tables already exist
            db.create_all()
            
            # For existing databases, try to add new columns if they don't exist
            # SQLite supports ALTER TABLE ADD COLUMN, but we need to check if column exists first
            try:
                from sqlalchemy import text, inspect
                inspector = inspect(db.engine)
                
                # Check if user table exists
                if 'user' in inspector.get_table_names():
                    columns = [col['name'] for col in inspector.get_columns('user')]
                    
                    # Check if new columns exist, if not add them
                    with db.engine.connect() as conn:
                        if 'smtp_email' not in columns:
                            try:
                                conn.execute(text("ALTER TABLE user ADD COLUMN smtp_email VARCHAR(120)"))
                                conn.commit()
                            except Exception as e:
                                print(f"Note: Could not add smtp_email column: {e}")
                        
                        if 'smtp_password' not in columns:
                            try:
                                conn.execute(text("ALTER TABLE user ADD COLUMN smtp_password VARCHAR(255)"))
                                conn.commit()
                            except Exception as e:
                                print(f"Note: Could not add smtp_password column: {e}")
                        
                        if 'smtp_server' not in columns:
                            try:
                                conn.execute(text("ALTER TABLE user ADD COLUMN smtp_server VARCHAR(100) DEFAULT 'smtp.gmail.com'"))
                                conn.commit()
                            except Exception as e:
                                print(f"Note: Could not add smtp_server column: {e}")
                        
                        if 'smtp_port' not in columns:
                            try:
                                conn.execute(text("ALTER TABLE user ADD COLUMN smtp_port INTEGER DEFAULT 587"))
                                conn.commit()
                            except Exception as e:
                                print(f"Note: Could not add smtp_port column: {e}")
                        
                        if 'sender_name' not in columns:
                            try:
                                conn.execute(text("ALTER TABLE user ADD COLUMN sender_name VARCHAR(100)"))
                                conn.commit()
                            except Exception as e:
                                print(f"Note: Could not add sender_name column: {e}")
                else:
                    # Table doesn't exist, db.create_all() will create it with all columns
                    pass
            except Exception as e:
                # Columns might already exist or database might not support ALTER
                print(f"Note: Could not check/add columns (this is usually fine): {e}")
                # Continue anyway - db.create_all() should handle it
        except Exception as e:
            # Only print error if it's not about table already existing
            if "already exists" not in str(e).lower():
                print(f"Database initialization warning: {e}")
            # Continue anyway - tables might already exist which is fine

init_database()

if __name__ == '__main__':
    # Get port from environment variable (for production) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Only run in debug mode if not in production
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
