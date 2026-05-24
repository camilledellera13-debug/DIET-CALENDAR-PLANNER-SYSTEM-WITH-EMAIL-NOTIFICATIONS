# 🚀 Diet Calendar Planner - Complete Setup & Startup Guide

## ⚠️ IMPORTANT: Issues Fixed

I've fixed the following issues in your code:
1. ✅ Removed bad import that was breaking the app
2. ✅ Fixed `/api/trigger-activity-email` endpoint to use proper Flask-Mail
3. ✅ Email notifications now properly configured
4. ✅ Meal generation endpoints should work

---

## 🔧 Step 1: Start MySQL (REQUIRED)

Your app cannot add meals or generate meal plans without MySQL running.

### Option A: Start XAMPP MySQL
1. Open **XAMPP Control Panel**
2. Click **Start** next to MySQL
3. Wait for it to say "Running"
4. Leave it running while using the app

### Option B: Manual MySQL Start (Windows)
```powershell
# Option 1: If installed as service
net start MySQL80

# Option 2: Check services
Get-Service | grep -i mysql

# Option 3: Navigate to MySQL bin and start
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
mysqld
```

**Test MySQL is running:**
```powershell
mysql -u root -p
# Just press Enter if no password
# You should see: mysql>
# Type: exit
```

---

## 📧 Step 2: Configure Email (Optional but Recommended)

### 2A: Get Gmail Credentials
1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already enabled
3. Go to: https://myaccount.google.com/apppasswords
4. Select: 
   - App: **Mail**
   - Device: **Windows PC** (or your OS)
5. Google will show a **16-character password**
6. **Copy this password** (spaces are part of it)

### 2B: Set Environment Variables

**PowerShell (Option 1 - Best)**
```powershell
$env:MAIL_USERNAME = "your-gmail@gmail.com"
$env:MAIL_PASSWORD = "xxxx xxxx xxxx xxxx"
```

**Command Prompt (Option 2)**
```cmd
set MAIL_USERNAME=your-gmail@gmail.com
set MAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

**Permanent (Windows - Option 3)**
1. Press `Win + X` → System
2. Advanced system settings → Environment Variables
3. New User Variable:
   - Name: `MAIL_USERNAME`
   - Value: `your-gmail@gmail.com`
4. New User Variable:
   - Name: `MAIL_PASSWORD`
   - Value: `xxxx xxxx xxxx xxxx`
5. Click OK and restart terminal

---

## 🎯 Step 3: Install Dependencies

**First time only:**
```powershell
cd c:\xampp\htdocs\diet-calendar-planner-system
pip install -r requirements.txt
```

---

## ▶️ Step 4: Start the Flask App

```powershell
cd c:\xampp\htdocs\diet-calendar-planner-system
python backend/app.py
```

You should see:
```
✅ Database initialized
🚀 Server running at http://localhost:5000
 * Running on http://127.0.0.1:5000
```

---

## ✅ Step 5: Test Everything Works

### Test 1: Check if app is running
- Open browser: http://localhost:5000
- You should see the login page

### Test 2: Add a Meal
1. Register a test account with your real email
2. Go to "Add Meal" 
3. Select meal type and food
4. Click Save
5. **Check your email** - you should receive notification!

### Test 3: Log an Activity
1. Go to "Activities"
2. Select an activity and duration
3. Click Log Activity
4. **Check your email** - you should receive activity notification!

### Test 4: Generate Meal Plan
1. Go to "Generate Meal Plan"
2. Select goal (lose/gain/maintain)
3. Click Generate
4. Meals should appear in calendar

---

## 🐛 Troubleshooting

### Problem: "Can't connect to server on 'localhost' (10061)"
**Solution:** MySQL is not running
- Start MySQL in XAMPP Control Panel
- Or use `net start MySQL80` in PowerShell

### Problem: "Meals won't save"
**Solution:** 
- Check MySQL is running
- Check user is logged in
- Check browser console for errors (F12)

### Problem: "Emails not sending"
**Solution:**
- Check environment variables are set: `$env:MAIL_USERNAME`
- Check Gmail 2FA is enabled
- Check App Password is correct (spaces matter!)
- Check Gmail Account in MAIL_USERNAME variable

### Problem: "ImportError: No module named 'flask_mail'"
**Solution:** 
```powershell
pip install Flask-Mail
```

### Problem: Port 5000 already in use
**Solution:**
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F

# Or use different port
python backend/app.py --port 5001
```

---

## 📋 Quick Reference Checklist

Before you start, ensure:
- [ ] MySQL is installed and running
- [ ] Python 3.7+ is installed
- [ ] requirements.txt dependencies installed
- [ ] (Optional) Gmail credentials configured
- [ ] (Optional) Environment variables set for email
- [ ] Port 5000 is available

---

## 🎉 What Should Work Now

✅ User registration and login  
✅ Adding meals to calendar  
✅ Generating meal plans automatically  
✅ Logging activities  
✅ Email notifications for meals (if configured)  
✅ Email notifications for activities (if configured)  
✅ Daily reminder emails (if configured)  
✅ Activity recommendations  

---

## 📞 Still Having Issues?

1. **Check error messages** in the terminal window
2. **Look at browser console** (Press F12 → Console tab)
3. **Verify MySQL is running** with: `mysql -u root -p`
4. **Restart Flask app** (Ctrl+C, then python backend/app.py)
5. **Clear browser cache** (Ctrl+Shift+Delete)

---

## 🔐 Security Reminder

- Never commit passwords to GitHub
- Use environment variables in production
- Gmail App Passwords are safer than main password
- Keep your database credentials secure

Enjoy your Diet Calendar Planner! 💪🍽️
