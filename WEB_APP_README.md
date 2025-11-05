# Email Automation Web Platform

A scalable multi-user web platform for automated email campaigns.

## Features

- ✅ User authentication (signup/login)
- ✅ Multiple email list options (YC Startups, Business Emails, GR)
- ✅ Custom email template upload
- ✅ Default email templates
- ✅ Campaign management
- ✅ Real-time campaign tracking
- ✅ Scalable for 100+ users

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### 3. First Time Setup

1. Visit `http://localhost:5000`
2. Create an account with username, email, and password
3. Choose your email list (YC Startups, Business Emails, or GR)
4. Upload a custom template or use the default
5. Start your campaign!

## Deployment Options

### Option 1: Railway (Recommended - Easy & Free)

1. Sign up at [railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Railway will auto-detect Flask and deploy
5. Add environment variable: `SECRET_KEY=your-secret-key-here`

### Option 2: Render

1. Sign up at [render.com](https://render.com)
2. Create a new Web Service
3. Connect your repository
4. Build command: `pip install -r requirements.txt`
5. Start command: `python app.py`
6. Add environment variable: `SECRET_KEY=your-secret-key-here`

### Option 3: Heroku

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Deploy: `git push heroku main`
5. Set secret key: `heroku config:set SECRET_KEY=your-secret-key`

### Option 4: Local Production (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Environment Variables

- `SECRET_KEY`: Flask secret key for sessions (required for production)
- `DATABASE_URL`: Optional database URL (defaults to SQLite)

## File Structure

```
├── app.py                 # Main Flask application
├── email_automation.py    # Email automation backend
├── templates/             # HTML templates
│   ├── base.html
│   ├── signup.html
│   ├── login.html
│   └── dashboard.html
├── user_data/            # User-specific data (auto-created)
├── user_templates/       # Uploaded templates (auto-created)
├── email_automation.db   # SQLite database (auto-created)
└── requirements.txt      # Python dependencies
```

## Notes

- The application uses SQLite by default (good for up to 100 users)
- For production with 100+ users, consider PostgreSQL
- Email campaigns run in background threads
- Users need to configure their SMTP credentials for actual email sending

