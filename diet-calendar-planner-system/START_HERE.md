# ⚡ START HERE - 5 Minute Setup

## 🎯 Your 3 Steps to Success

### Step 1️⃣: Start MySQL (1 minute)
1. Open **XAMPP Control Panel**
2. Find **MySQL**
3. Click **Start**
4. Wait for status to say "Running"
5. Leave it open

### Step 2️⃣: Start the App (1 minute)
```
From your folder: c:\xampp\htdocs\diet-calendar-planner-system

Option A (Easiest):
  Double-click: START_APP.bat

Option B (Manual):
  Open PowerShell here
  Run: python backend/app.py
```

**You should see:**
```
✅ Database initialized
🚀 Server running at http://localhost:5000
```

### Step 3️⃣: Open App (1 minute)
1. Open browser
2. Go to: `http://localhost:5000`
3. Click **Register**
4. **Use your REAL email address** (you'll get email notifications!)
5. Create account
6. Click **Login**

---

## 🧪 Quick Test (2 minutes)

### Test Meals
1. Click **Calendar**
2. Click **Add Meal**
3. Fill in details
4. Click **Save**
5. **Check your email!** 📧 You should have a notification!

### Test Activities  
1. Click **Activities**
2. Select activity (e.g., Running)
3. Enter duration (e.g., 30 min)
4. Click **Log Activity**
5. **Check your email!** 📧 Another notification!

---

## ✅ If Everything Worked

Congratulations! You have:
- ✅ Meals working
- ✅ Activities working
- ✅ Email notifications working
- ✅ Calendar system working

---

## ❌ If Something Didn't Work

### MySQL Error
**Error:** "Can't connect to server on 'localhost' (10061)"
**Fix:** Start MySQL in XAMPP (see Step 1)

### Port 5000 Error
**Error:** "Address already in use"
**Fix:** Close the app, restart, or use different port

### Email Not Received
**Error:** Email doesn't arrive
**Fix:** 
1. Check spam folder
2. Check you registered with real email
3. Wait 10 seconds
4. Check [EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)

### Other Errors
1. See the error in terminal
2. Read [WHATS_FIXED.md](WHATS_FIXED.md)
3. Check [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)

---

## 📚 Full Documentation

When you're ready for more info:
- [WHATS_FIXED.md](WHATS_FIXED.md) - See what got fixed
- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - Complete setup guide
- [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Test everything
- [EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md) - Email details

---

## 🎉 You're All Set!

Your diet calendar planner is ready to use.

**Next time you start:**
1. Open XAMPP → Start MySQL
2. Run: `python backend/app.py`
3. Go to: http://localhost:5000
4. Login and use!

Enjoy! 💪🍽️
