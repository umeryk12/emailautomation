# 📤 Push Code to GitHub Repository

**Target Repository:** https://github.com/umeryk12/emailautomation

## Option 1: Using GitHub CLI (Easiest)

If you have GitHub CLI installed:

```bash
gh repo clone umeryk12/emailautomation
cd emailautomation
# Copy all your files here
git add .
git commit -m "Email Automation Tool - Production ready"
git push
```

## Option 2: Using Git with Authentication

### Step 1: Set Remote
```bash
git remote remove origin
git remote add origin https://github.com/umeryk12/emailautomation.git
```

### Step 2: Authenticate
You'll need to authenticate. Options:

**A. Personal Access Token (Recommended):**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "Email Automation Tool"
4. Select scopes: `repo` (full control)
5. Copy the token
6. Use it when pushing:
   ```bash
   git push -u origin main
   ```
   When prompted:
   - Username: `umeryk12`
   - Password: `paste-your-token-here`

**B. SSH Key (If you have SSH set up):**
```bash
git remote set-url origin git@github.com:umeryk12/emailautomation.git
git push -u origin main
```

## Option 3: Upload via GitHub Web Interface

1. Go to: https://github.com/umeryk12/emailautomation
2. Click "uploading an existing file"
3. Drag and drop all your files
4. Commit directly

## Option 4: Use GitHub Desktop

1. Download GitHub Desktop: https://desktop.github.com
2. Clone repository: `umeryk12/emailautomation`
3. Copy your files into the cloned folder
4. Commit and push via GitHub Desktop

---

## ✅ Files to Push

Make sure these files are included:
- `app.py`
- `email_automation.py`
- `requirements.txt`
- `Procfile`
- `gunicorn_config.py`
- `templates/` folder (all HTML files)
- `ycombinatoremails.csv`
- `companies.csv`
- All other project files

---

## 🚀 After Pushing

Once code is on GitHub, deploy to Railway:

1. Go to: https://railway.app
2. New Project → Deploy from GitHub
3. Select: `umeryk12/emailautomation`
4. Add environment variables:
   - `SECRET_KEY` = `2c0819d984af217cad2b8a3b6061aebc74502d7575ef2ed019f5d8ada33f6f3a`
   - `FLASK_ENV` = `production`
5. Generate domain → Live!

---

## 🔐 Generate Personal Access Token

1. Visit: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "Email Automation"
4. Expiration: 90 days (or no expiration)
5. Scopes: Check `repo` (Full control)
6. Generate token
7. **Copy token immediately** (you won't see it again)
8. Use as password when pushing

---

## 🆘 Need Help?

- **Permission denied?** → Use Personal Access Token
- **Repository not found?** → Make sure you're logged in as `umeryk12`
- **Can't push?** → Try GitHub Desktop or web upload

