# PRODUCTION DEPLOYMENT GUIDE
## Handcrafted Baskets - Flask Application

---

## TABLE OF CONTENTS
1. Pre-Deployment Checklist
2. Server Requirements
3. Deployment Steps
4. Security Configuration
5. Monitoring & Maintenance
6. Troubleshooting
7. Backup & Recovery

---

## 1. PRE-DEPLOYMENT CHECKLIST

Before deploying to production, complete ALL these items:

### Security
- [ ] Change admin password (not 'password')
- [ ] Change SECRET_KEY in config.py (use `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Set DEBUG = False in config.py
- [ ] Review and update WHATSAPP_NUMBER
- [ ] Create .env file with all secrets (do NOT commit to git)
- [ ] Set up HTTPS certificate (Let's Encrypt recommended)

### Code Quality
- [ ] Test on staging environment first
- [ ] Run full test suite (TESTING_GUIDE.txt)
- [ ] Check for console errors (browser DevTools)
- [ ] Verify all routes work
- [ ] Test admin panel fully
- [ ] Test WhatsApp integration with real number

### Database
- [ ] Backup existing database
- [ ] Test database migrations
- [ ] Verify backups work and can be restored
- [ ] Set up automated backup schedule

### Files & Permissions
- [ ] Create /uploads directory with correct permissions
- [ ] Ensure database file is in secure location
- [ ] Set proper file permissions (644 for files, 755 for directories)
- [ ] Remove any debug files or temporary files

### Documentation
- [ ] Update README.md with actual business info
- [ ] Document admin password location (secure storage)
- [ ] Document database location and backup procedures
- [ ] Create runbook for common issues

---

## 2. SERVER REQUIREMENTS

### Minimum Specifications
- **OS**: Linux (Ubuntu 20.04+ recommended) or Windows Server
- **Python**: 3.8+
- **Disk Space**: 5GB minimum (more if expecting high product volume)
- **RAM**: 512MB minimum (1GB+ recommended)
- **Bandwidth**: Depends on usage

### Recommended Specifications
- **OS**: Ubuntu 20.04 LTS or 22.04 LTS
- **Python**: 3.10+
- **Disk Space**: 20GB+
- **RAM**: 2GB
- **CPU**: 2+ cores
- **Database**: SSD for baskets.db

### Domain & SSL
- [ ] Domain name configured
- [ ] SSL certificate installed (Let's Encrypt free option available)
- [ ] Auto-renewal configured for SSL certificate

---

## 3. DEPLOYMENT STEPS

### Step 1: Server Setup (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y nginx postgresql-client  # optional: postgres client

# Create application user
sudo useradd -m -s /bin/bash baskets
sudo su - baskets
```

### Step 2: Install Application

```bash
# Clone or upload application files
cd /home/baskets
# Either:
# git clone <repository> app
# OR upload files manually

# Create and activate virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

### Step 3: Configure Application

```bash
# Create .env file with secrets (NEVER commit this to git)
nano .env

# Add these lines:
# SECRET_KEY=your-very-long-secret-key-here
# WHATSAPP_NUMBER=919876543210
# FLASK_ENV=production
# DEBUG=False

# Create uploads directory
mkdir -p uploads
chmod 755 uploads
```

### Step 4: Create Systemd Service (Auto-start)

```bash
# Create service file
sudo nano /etc/systemd/system/baskets.service

# Add this content:
"""
[Unit]
Description=Handcrafted Baskets Flask App
After=network.target

[Service]
User=baskets
WorkingDirectory=/home/baskets/app
Environment="PATH=/home/baskets/app/venv/bin"
ExecStart=/home/baskets/app/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 app:app

[Install]
WantedBy=multi-user.target
"""

# Enable and start service
sudo systemctl enable baskets
sudo systemctl start baskets
sudo systemctl status baskets
```

### Step 5: Configure Nginx (Reverse Proxy)

```bash
# Create nginx configuration
sudo nano /etc/nginx/sites-available/baskets

# Add this content:
"""
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificate (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Logging
    access_log /var/log/nginx/baskets_access.log;
    error_log /var/log/nginx/baskets_error.log;

    # Proxy Configuration
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files caching (optional)
    location /static/ {
        alias /home/baskets/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads/ {
        alias /home/baskets/app/uploads/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
"""

# Enable site
sudo ln -s /etc/nginx/sites-available/baskets /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default 2>/dev/null

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### Step 6: Set Up SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Auto-renewal runs via cron automatically
```

### Step 7: Set Up Database Backups

```bash
# Create backup script
mkdir -p /home/baskets/backups
nano /home/baskets/backups/backup.sh

# Add this content:
"""
#!/bin/bash
BACKUP_DIR="/home/baskets/backups"
DB_FILE="/home/baskets/app/baskets.db"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
cp $DB_FILE $BACKUP_DIR/baskets_$DATE.db

# Keep only last 30 days of backups
find $BACKUP_DIR -name "baskets_*.db" -mtime +30 -delete

echo "Backup completed: baskets_$DATE.db"
"""

# Make executable
chmod +x /home/baskets/backups/backup.sh

# Add to crontab for daily backups at 2am
crontab -e
# Add: 0 2 * * * /home/baskets/backups/backup.sh >> /home/baskets/backups/backup.log 2>&1
```

---

## 4. SECURITY CONFIGURATION

### Environment Variables (.env file)

```bash
# Production .env file
SECRET_KEY=your-very-long-random-secret-key-here
WHATSAPP_NUMBER=919876543210
FLASK_ENV=production
DEBUG=False
ADMIN_USERNAME=admin
MAX_UPLOAD_SIZE=16777216  # 16MB in bytes
```

### File Permissions

```bash
# Set proper permissions
sudo chown -R baskets:baskets /home/baskets/app
sudo chmod 755 /home/baskets/app
sudo chmod 755 /home/baskets/app/uploads
sudo chmod 600 .env  # Very restrictive for secrets file
sudo chmod 644 baskets.db  # Database readable
```

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Verify
sudo ufw status
```

### Additional Security Measures

```python
# In config.py, ensure these settings:

# Session security
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection

# File upload security
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
```

---

## 5. MONITORING & MAINTENANCE

### System Monitoring

```bash
# Check service status
sudo systemctl status baskets

# View service logs
sudo journalctl -u baskets -f

# Check nginx logs
sudo tail -f /var/log/nginx/baskets_error.log
sudo tail -f /var/log/nginx/baskets_access.log

# Monitor disk usage
df -h
du -sh /home/baskets/app

# Monitor memory/CPU
htop
# or
ps aux | grep gunicorn
```

### Database Maintenance

```bash
# Weekly: Check database integrity
cd /home/baskets/app
python3 -c "from app import db; db.engine.execute('PRAGMA integrity_check')"

# Monthly: Vacuum database (optimize)
python3 -c "from app import db; db.engine.execute('VACUUM')"

# Check database size
ls -lh baskets.db
```

### Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/baskets

# Add:
"""
/var/log/nginx/baskets*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}

/home/baskets/backups/backup.log {
    daily
    rotate 30
    compress
}
"""
```

### Performance Tuning

```python
# Optimize gunicorn workers
# workers = 2 + (2 × CPU_cores)
# For 2 CPU core server: workers = 6

# In baskets.service or gunicorn command:
# ExecStart=... --workers 6 --worker-class sync --worker-connections 1000
```

---

## 6. TROUBLESHOOTING

### Application Won't Start

```bash
# Check service status
sudo systemctl status baskets

# View detailed logs
sudo journalctl -u baskets -n 50

# Check Python errors
cd /home/baskets/app
source venv/bin/activate
python3 app.py  # Run manually to see errors

# Verify database
ls -la baskets.db
file baskets.db
```

### Database Errors

```bash
# Backup current database
cp baskets.db baskets.db.backup

# Reinitialize database
rm baskets.db
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Restore from backup if needed
cp baskets.db.backup baskets.db
```

### Upload Issues

```bash
# Check uploads folder
ls -la uploads/
ls -la uploads/ | wc -l  # count files

# Fix permissions if needed
chmod 755 uploads
sudo chown baskets:baskets uploads

# Clear old uploads (>90 days)
find uploads/ -type f -mtime +90 -delete
```

### SSL Certificate Issues

```bash
# Check certificate expiration
sudo certbot certificates

# Manually renew
sudo certbot renew --force-renewal

# Check nginx SSL
sudo openssl s_client -connect yourdomain.com:443
```

### Performance Issues

```bash
# Check system resources
free -h
top

# Identify slow queries
# Enable database logging in app.py:
# app.config['SQLALCHEMY_ECHO'] = True

# Check nginx status
sudo systemctl status nginx
sudo nginx -t

# Analyze access logs
sudo tail -100 /var/log/nginx/baskets_access.log | awk '{print $9}' | sort | uniq -c | sort -rn
```

---

## 7. BACKUP & RECOVERY

### Automated Backups

Already configured in Step 7. Verify:

```bash
# Check backup location
ls -la /home/baskets/backups/

# Test restoration
cp baskets.db baskets.db.current
cp /home/baskets/backups/baskets_YYYYMMDD_HHMMSS.db baskets.db
# Then restart: sudo systemctl restart baskets
```

### Manual Backup

```bash
# Create immediate backup
/home/baskets/backups/backup.sh

# Download backup (from local machine)
scp baskets@yourdomain.com:/home/baskets/backups/baskets_*.db ./
```

### Complete System Backup

```bash
# Backup entire application
tar -czf baskets_backup_$(date +%Y%m%d).tar.gz \
    /home/baskets/app \
    /etc/nginx/sites-available/baskets \
    /etc/systemd/system/baskets.service

# Upload to safe location
scp baskets_backup_*.tar.gz your-backup-storage:/path/
```

### Recovery Procedure

```bash
# 1. Stop application
sudo systemctl stop baskets

# 2. Restore database
cp /path/to/baskets_YYYYMMDD.db /home/baskets/app/baskets.db
sudo chown baskets:baskets /home/baskets/app/baskets.db

# 3. Start application
sudo systemctl start baskets

# 4. Verify
sudo systemctl status baskets
curl https://yourdomain.com/
```

---

## QUICK REFERENCE

### Common Commands

```bash
# Service management
sudo systemctl start baskets
sudo systemctl stop baskets
sudo systemctl restart baskets
sudo systemctl status baskets

# View logs
sudo journalctl -u baskets -f
tail -f /var/log/nginx/baskets_error.log

# Backup
/home/baskets/backups/backup.sh

# Test config
sudo nginx -t
python3 -m py_compile /home/baskets/app/app.py

# SSL renewal
sudo certbot renew --dry-run
sudo certbot renew

# Access admin
# https://yourdomain.com/admin/login
# Username: admin
# Password: (what you set)
```

### Important Paths

```
Application:        /home/baskets/app/
Database:          /home/baskets/app/baskets.db
Uploads:           /home/baskets/app/uploads/
Backups:           /home/baskets/backups/
Config:            /home/baskets/app/config.py
Environment:       /home/baskets/app/.env
Nginx config:      /etc/nginx/sites-available/baskets
Service file:      /etc/systemd/system/baskets.service
SSL cert:          /etc/letsencrypt/live/yourdomain.com/
Logs (app):        journalctl
Logs (nginx):      /var/log/nginx/baskets_*.log
```

---

## SUPPORT & HELP

### Getting Help

1. Check TESTING_GUIDE.txt for common issues
2. Review logs: `sudo journalctl -u baskets -n 100`
3. Check nginx: `sudo tail -50 /var/log/nginx/baskets_error.log`
4. Test database: Connect to baskets.db and verify tables exist

### Reporting Issues

When reporting issues, include:
- Error message from logs
- Steps to reproduce
- System info (Ubuntu version, Python version, etc.)
- Output of: `python3 --version`, `pip list`

---

**Last Updated**: January 2025
**Version**: 1.0
**Status**: Production Ready