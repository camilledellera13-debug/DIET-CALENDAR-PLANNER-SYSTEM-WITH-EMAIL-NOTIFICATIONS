# 🍽️ Diet Calendar Planner System - Complete Guide

## ✨ What's Been Fixed

✅ **Email notifications are now working!**
- When users add meals → Email sent
- When users log activities → Email sent  
- Broken import error fixed
- Activity recommendation emails configured

✅ **Meal management fully functional**
- Add meals to calendar
- Generate automatic meal plans
- Log activities and exercises

✅ **Database integration complete**
- All meal endpoints working
- Activity tracking enabled
- User profiles stored

---

## 🚀 Quick Start (2 Minutes)

### Step 1: Start MySQL (Required!)
- Open **XAMPP Control Panel**
- Click **Start** next to MySQL
- Leave it running

### Step 2: Run the App

**Option A: Use Startup Script (Recommended)**
```
Double-click: START_APP.bat
```

**Option B: Manual Start**
```powershell
cd c:\xampp\htdocs\diet-calendar-planner-system
python backend/app.py
```

### Step 3: Open in Browser
```
http://localhost:5000
```

---

## 📧 Enable Email Notifications (Optional)

### Get Gmail App Password (3 Steps)
1. Go to https://myaccount.google.com/apppasswords
2. Select: **Mail** → **Windows PC**
3. Copy the 16-character password

### Set Environment Variables

**PowerShell:**
```powershell
$env:MAIL_USERNAME = "your-email@gmail.com"
$env:MAIL_PASSWORD = "xxxx xxxx xxxx xxxx"
```

**Command Prompt:**
```cmd
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

### Test Email Notifications
1. Register with real email
2. Add a meal
3. Check inbox for notification email!

---

## 📋 File Structure

```
diet-calendar-planner-system/
├── backend/
│   ├── app.py                           # Main Flask app ✅ FIXED
│   ├── database.py                      # Database setup
│   ├── notification_service.py          # In-app notifications
│   ├── notification_enhanced.py         # Email templates
│   ├── templates/
│   │   ├── index.html
│   │   ├── calendar.html
│   │   ├── activities.html
│   │   └── login.html
│   ├── static/ (css, js)
│   └── database/
│       └── dietcalendarplannersys.sql
├── START_APP.bat                        # 🆕 Easy startup script
├── START_APP.ps1                        # 🆕 PowerShell startup
├── STARTUP_GUIDE.md                     # 🆕 Complete setup guide
├── EMAIL_SETUP_GUIDE.md                 # 🆕 Email configuration
├── EMAIL_QUICK_REFERENCE.md             # 🆕 Email troubleshooting
├── requirements.txt                     # 🆕 Python dependencies
└── .env.example                         # 🆕 Environment template
```

---

## 🎯 Key Features Now Working

### Meals 🍽️
- ✅ Add meals with calorie tracking
- ✅ Generate meal plans automatically
- ✅ View meal calendar
- ✅ Track nutrition (protein, carbs, fats)
- ✅ Email notification on meal logging

### Activities 🏃
- ✅ Log exercises and activities
- ✅ Track calories burned
- ✅ View activity history
- ✅ Get personalized recommendations
- ✅ Email notification on activity logging

### Notifications 📧
- ✅ Email sent when meal is logged
- ✅ Email sent when activity is logged
- ✅ Daily reminder emails available
- ✅ In-app notification system
- ✅ Activity goal suggestions

---

## ⚙️ Configuration

### Database
- Host: localhost
- User: root
- Password: (blank by default in XAMPP)
- Database: dietcalendarplannersys

### Email (Optional)
- SMTP Server: smtp.gmail.com
- Port: 587
- Requires: Gmail App Password (not regular password)

### Flask App
- Port: 5000 (configurable)
- Debug: True (for development)
- Secret Key: Change in production!

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| MySQL connection error | Start MySQL in XAMPP Control Panel |
| Can't add meals | Verify MySQL is running and user is logged in |
| Port 5000 in use | `netstat -ano \| findstr :5000` then `taskkill /PID <PID> /F` |
| Import errors | Run `pip install -r requirements.txt` |
| Emails not sending | Check MAIL_USERNAME and MAIL_PASSWORD are set |
| App won't start | Check Python version (3.7+) with `python --version` |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [STARTUP_GUIDE.md](STARTUP_GUIDE.md) | Complete setup & startup instructions |
| [EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md) | Detailed email configuration |
| [EMAIL_QUICK_REFERENCE.md](EMAIL_QUICK_REFERENCE.md) | Email troubleshooting & testing |
| [requirements.txt](requirements.txt) | Python dependencies |

---

## 🔐 Security

⚠️ **IMPORTANT:**
- Change `app.secret_key` in production
- Never commit credentials to GitHub
- Use environment variables for passwords
- Gmail App Passwords safer than main password

---

## 💻 System Requirements

- Python 3.7+
- MySQL 5.7+
- Windows/Mac/Linux
- 4GB RAM minimum
- 500MB disk space

---

## 📞 Quick Help

### Start the App
```bash
cd c:\xampp\htdocs\diet-calendar-planner-system
python backend/app.py
```

### Access the App
```
Browser: http://localhost:5000
```

### Enable Email
```powershell
$env:MAIL_USERNAME = "gmail@gmail.com"
$env:MAIL_PASSWORD = "xxxx xxxx xxxx xxxx"
python backend/app.py
```

### Stop the App
```
Ctrl + C in terminal
```

---

## 🎉 You're All Set!

Your Diet Calendar Planner is ready to use:
1. ✅ Meals working
2. ✅ Activities working
3. ✅ Email notifications working
4. ✅ All endpoints fixed

**Next Steps:**
- [ ] Start MySQL
- [ ] Run START_APP.bat
- [ ] Create account
- [ ] Add a meal
- [ ] Check your email for notification!

---

## 📝 Notes

- App runs in debug mode (perfect for development)
- Emails are sent in background threads (non-blocking)
- All notifications are stored in database
- User sessions persist until logout

Enjoy your Diet Calendar Planner! 💪
