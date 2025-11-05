# Deployment Guide

## Quick Deploy Options

### 🚀 Option 1: Railway (Easiest - Recommended)

1. **Sign up**: Go to [railway.app](https://railway.app) and create an account
2. **New Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Connect Repo**: Select your repository
4. **Auto Deploy**: Railway will automatically detect Flask and deploy
5. **Set Environment Variable**:
   - Go to Variables tab
   - Add: `SECRET_KEY` = (generate a random string)
   - Add: `FLASK_ENV` = `production`
6. **Done!** Your app will be live at `your-app-name.railway.app`

**Pros**: Free tier, auto-deploy, easy setup
**Cons**: Limited free hours per month

---

### 🌐 Option 2: Render (Free Tier Available)

1. **Sign up**: Go to [render.com](https://render.com)
2. **New Web Service**: Click "New" → "Web Service"
3. **Connect Repository**: Link your GitHub repo
4. **Configure**:
   - **Name**: email-automation (or your choice)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -c gunicorn_config.py app:app`
5. **Environment Variables**:
   - `SECRET_KEY`: Generate a random secret key
   - `FLASK_ENV`: `production`
6. **Deploy**: Click "Create Web Service"

**Pros**: Free tier, persistent storage, easy scaling
**Cons**: Spins down after inactivity (free tier)

---

### 🟣 Option 3: Heroku

1. **Install Heroku CLI**: [heroku.com/cli](https://devcenter.heroku.com/articles/heroku-cli)
2. **Login**: `heroku login`
3. **Create App**: `heroku create your-app-name`
4. **Set Config**: 
   ```bash
   heroku config:set SECRET_KEY=your-random-secret-key
   heroku config:set FLASK_ENV=production
   ```
5. **Deploy**: `git push heroku main`
6. **Open**: `heroku open`

**Pros**: Well-established, good documentation
**Cons**: No free tier anymore

---

### 💻 Option 4: Local Production Server

For hosting on your own server (VPS, AWS EC2, DigitalOcean, etc.):

```bash
# Install dependencies
pip install -r requirements.txt

# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or use the config file
gunicorn -c gunicorn_config.py app:app
```

**For production, use a process manager like systemd or supervisor**

---

## Environment Variables

Set these in your hosting platform:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key (REQUIRED) | `your-random-secret-key-here` |
| `FLASK_ENV` | Environment mode | `production` |
| `DATABASE_URL` | Database URL (optional) | `postgresql://user:pass@host/db` |
| `PORT` | Port number (auto-set by most platforms) | `5000` |

## Generate Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

Or use:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Post-Deployment Checklist

- [ ] Set `SECRET_KEY` environment variable
- [ ] Set `FLASK_ENV=production`
- [ ] Verify database is created (SQLite or PostgreSQL)
- [ ] Test signup/login functionality
- [ ] Test template upload
- [ ] Test campaign creation
- [ ] Monitor logs for errors

## Scaling for 100 Users

The app is designed to handle 100+ users:

- **SQLite**: Works fine for up to 100 concurrent users
- **PostgreSQL**: Recommended for 100+ users or high traffic
  - Update `DATABASE_URL` environment variable
  - Install `psycopg2-binary` (already in requirements.txt)

## Troubleshooting

### Database Issues
- Ensure write permissions for SQLite database
- For PostgreSQL, verify connection string format

### Port Issues
- Most platforms set PORT automatically
- If issues, check platform documentation

### Static Files
- All templates are served by Flask
- No additional static file configuration needed

## Support

For issues, check:
1. Application logs in your hosting platform
2. Database connection status
3. Environment variables are set correctly

