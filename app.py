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
    
    # Start campaign in background thread
    thread = threading.Thread(target=run_campaign, args=(campaign.id,))
    thread.daemon = True
    thread.start()
    
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
    with app.app_context():
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return
        
        # Get user from campaign
        user = User.query.get(campaign.user_id)
        if not user:
            campaign.status = 'failed'
            db.session.commit()
            return
        
        campaign.status = 'running'
        campaign.started_at = datetime.utcnow()
        db.session.commit()
        
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
            
            # Create user-specific config
            user_config = {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': user.email,  # Use user's email
                'sender_password': '',  # User needs to set this up
                'sender_name': user.username,
                'delay_between_emails': 30,
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
            
            # Initialize email automation
            automation = EmailAutomation(config_file=config_file)
            
            # Override template loading
            automation.load_email_template = lambda: open(template_file, 'r', encoding='utf-8').read()
            
            # Load companies
            companies = automation.load_companies_from_csv(csv_file, skip_sent=True, include_dry_run=True)
            
            # Apply email limit if set
            if campaign.email_limit and campaign.email_limit > 0:
                companies = companies[:campaign.email_limit]
            
            campaign.total_emails = len(companies)
            db.session.commit()
            
            # Run automation (dry run for now - users need to configure SMTP)
            # In production, you'd want users to provide their SMTP credentials
            automation.run(csv_file=csv_file, dry_run=True, skip_sent=True)
            
            # Update campaign status
            campaign.sent_emails = automation.sent_count
            campaign.failed_emails = automation.failed_count
            campaign.status = 'completed'
            campaign.completed_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            campaign.status = 'failed'
            db.session.commit()
            print(f"Campaign {campaign_id} failed: {e}")

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

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Get port from environment variable (for production) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Only run in debug mode if not in production
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
