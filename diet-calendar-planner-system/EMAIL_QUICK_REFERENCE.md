# Email Notification System - Quick Reference

## ✅ What's Already Done

Your app.py already contains:
- ✓ `send_meal_notification_email()` - sends when meals are logged
- ✓ `send_activity_notification_email()` - sends when activities are logged  
- ✓ `send_daily_reminder_email()` - sends daily digest emails
- ✓ Background threading to prevent email delays
- ✓ HTML formatted professional emails
- ✓ Flask-Mail integration with Gmail SMTP

---

## 🚀 Quick Start (3 Steps)

### 1. Get Gmail Credentials
```
Go to: https://myaccount.google.com/apppasswords
Select: Mail + Windows PC
Copy: 16-character app password
```

### 2. Set Environment Variables (PowerShell)
```powershell
$env:MAIL_USERNAME = "your-email@gmail.com"
$env:MAIL_PASSWORD = "xxxx xxxx xxxx xxxx"
```

### 3. Run Your App
```powershell
python backend/app.py
```

---

## 📧 How to Test Emails

1. **Register a test account** with your email address
2. **Log a meal**:
   ```bash
   POST /api/add-meal
   {
       "meal_type": "breakfast",
       "foods": [{"name": "Eggs", "calories": 150}],
       "calories": 150,
       "date": "2024-05-22"
   }
   ```
3. **Check inbox** for notification email

4. **Log an activity**:
   ```bash
   POST /api/log-activity
   {
       "activity_id": 1,
       "duration_minutes": 30,
       "date": "2024-05-22"
   }
   ```
5. **Check inbox** again

---

## 🔍 Debugging

### Check if emails are configured:
Look in Flask console after starting app:
```
✅ Email configured - MAIL_USERNAME found
OR
⚠️ Mail not configured - skipping email
```

### Enable logging in app.py:
Add this after Flask app creation:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test email directly:
```python
from flask_mail import Message
msg = Message('Test', recipients=['your-email@gmail.com'], body='Test')
mail.send(msg)
```

---

## 📝 Email Content Examples

### Meal Email Includes:
- Meal type (Breakfast, Lunch, Dinner, Snack)
- Food name
- Calories consumed
- Date logged
- Tip about consistent logging

### Activity Email Includes:
- Activity name (Running, Swimming, etc.)
- Duration in minutes
- Calories burned
- Intensity level
- Date logged
- Motivational message

---

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Mail not configured" | Set MAIL_USERNAME and MAIL_PASSWORD env vars |
| Email not arriving | Check spam folder, verify email in user profile |
| "Failed to send email" | Check 2FA enabled, app password correct |
| Port 587 blocked | Check firewall, use VPN if needed |
| ImportError: Flask-Mail | Run `pip install Flask-Mail` |

---

## 🔐 Security Tips

1. **Never commit credentials** to GitHub
2. Use `.env` file for local development:
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```
3. Add `.env` to `.gitignore`:
   ```
   .env
   *.pyc
   __pycache__/
   ```
4. Use environment variables in production
5. Use Gmail App Passwords (not main password)

---

## 📞 Support

For issues with Gmail credentials:
- https://support.google.com/accounts/answer/185833 (2FA setup)
- https://support.google.com/accounts/answer/185833 (App passwords)

For Flask-Mail issues:
- https://pythonhosted.org/Flask-Mail/
- Check Flask app config in backend/app.py (line 26-33)

---

## 🎯 Next Steps

1. [ ] Set up Gmail 2-Step Verification
2. [ ] Generate App Password
3. [ ] Set environment variables
4. [ ] Run install script or `pip install -r requirements.txt`
5. [ ] Test with sample meal/activity
6. [ ] Verify email arrives
7. [ ] Deploy with environment variables
