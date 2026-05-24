# ✅ Diet Calendar Planner - Complete Testing Checklist

## 🎯 Pre-Launch Checklist

Before starting the app, verify:
- [ ] MySQL is installed
- [ ] Python 3.7+ is installed
- [ ] XAMPP is installed (if using XAMPP)
- [ ] You're in the correct directory: `c:\xampp\htdocs\diet-calendar-planner-system`

---

## 🚀 Startup Test

### 1. Start MySQL
```
✓ Open XAMPP Control Panel
✓ Click Start next to MySQL
✓ Wait for status to show "Running"
✓ Keep XAMPP open
```

### 2. Start Flask App
```powershell
cd c:\xampp\htdocs\diet-calendar-planner-system
python backend/app.py
```

**Expected output:**
```
✅ Database initialized
🚀 Server running at http://localhost:5000
 * Running on http://127.0.0.1:5000
```

✓ If you see this, everything is working!

---

## 📝 Functional Testing

### Test 1: User Registration ✅
1. Open http://localhost:5000
2. Click "Register"
3. Fill in:
   - Name: Test User
   - Email: **use your real email**
   - Password: TestPass123
   - Age: 25
   - Gender: Female
   - Height: 165
   - Weight: 60
   - Goal: Lose
4. Click "Register"
5. Expected: Redirected to login page

### Test 2: User Login ✅
1. Enter email from registration
2. Enter password
3. Click "Login"
4. Expected: Dashboard loads

### Test 3: Add Meal ✅
1. Click "Add Meal" or go to Calendar
2. Select meal type: "Breakfast"
3. Select food (or type custom)
4. Select date
5. Click "Save Meal"
6. **Check your email** - You should receive notification!

**Expected:**
- ✓ Meal appears on calendar
- ✓ Email in inbox with title "🍽️ Meal Logged - Diet Planner"
- ✓ Email shows meal type, calories, date

### Test 4: Generate Meal Plan ✅
1. Go to "Generate Meal Plan"
2. Select:
   - Goal: Lose Weight
   - Days: 7
3. Click "Generate"
4. Expected: Calendar fills with 7 days of meals

### Test 5: Log Activity ✅
1. Go to "Activities"
2. Select activity: "Running"
3. Enter duration: 30 minutes
4. Select date
5. Click "Log Activity"
6. **Check your email** - You should receive notification!

**Expected:**
- ✓ Activity logs successfully
- ✓ Email in inbox with title "🏃 Activity Logged..."
- ✓ Email shows duration, calories burned

### Test 6: View Notifications ✅
1. Click "Notifications" (bell icon)
2. You should see:
   - Meal notification
   - Activity notification
3. Click on notification to mark as read

### Test 7: Daily Reminder Email ✅
1. Go to "Send Daily Reminder"
2. Click "Send Today's Schedule"
3. **Check your email** - You should receive today's schedule!

---

## 🔍 Database Testing

### Verify Database Structure
```powershell
mysql -u root -p
# Just press Enter if no password
mysql> USE dietcalendarplannersys;
mysql> SHOW TABLES;
```

You should see:
```
user
dietplan
meal
fooditem
mealfood
user_activities
activities
notifications
progresslog
```

### Check if Data was Saved
```sql
USE dietcalendarplannersys;
SELECT COUNT(*) FROM user;
SELECT COUNT(*) FROM meal;
SELECT COUNT(*) FROM user_activities;
SELECT COUNT(*) FROM notifications;
```

---

## 📧 Email Notification Testing

### Setup Verification
```powershell
# Check if environment variables are set
$env:MAIL_USERNAME
$env:MAIL_PASSWORD

# Both should show your Gmail credentials
```

### Email Flow Test

**Test 1: Meal Email**
1. Add a meal
2. Wait 5 seconds
3. Check inbox
4. ✓ Email should be there

**Test 2: Activity Email**
1. Log an activity
2. Wait 5 seconds
3. Check inbox
4. ✓ Email should be there

**Test 3: Reminder Email**
1. Click "Send Daily Reminder"
2. Wait 5 seconds
3. Check inbox
4. ✓ Email should list today's meals/activities

**If emails don't arrive:**
1. Check spam/junk folder
2. Check email address is correct in user profile
3. Verify MAIL_USERNAME and MAIL_PASSWORD are set
4. Check terminal for error messages

---

## 🐛 Debugging

### View Console Output
The Flask terminal should show:
```
✅ Meal notification email sent to user@example.com
✅ Activity notification email sent to user@example.com
✅ Daily reminder email sent to user@example.com
```

### Check Browser Console
1. Press F12
2. Go to "Console" tab
3. Perform actions and watch for errors
4. Report any red error messages

### Check Flask Terminal
1. Look for error messages
2. Stack trace shows what went wrong
3. Common issues:
   - `ImportError` - missing package
   - `database error` - MySQL not running
   - `connection refused` - port 5000 in use

---

## ✨ Feature Completeness

### Core Features
- [ ] User registration works
- [ ] User login works
- [ ] Can add meals
- [ ] Can log activities
- [ ] Can view calendar
- [ ] Can generate meal plan

### Email Features
- [ ] Meal email sends
- [ ] Activity email sends
- [ ] Daily reminder sends
- [ ] Email formatting looks good
- [ ] Email arrives in inbox

### Data Persistence
- [ ] Meals saved to database
- [ ] Activities saved to database
- [ ] User profile saved
- [ ] Can logout and login again
- [ ] Data still there after refresh

### Notifications
- [ ] In-app notifications appear
- [ ] Notifications marked as read
- [ ] Notifications can be deleted
- [ ] Notification count updates

---

## 📊 Performance Testing

### App Response Time
- Page loads in <2 seconds: ✓ Good
- Page loads in 2-5 seconds: ⚠️ Acceptable
- Page loads in >5 seconds: ❌ Issue (check MySQL, browser)

### Multiple Meals Test
1. Add 10 meals
2. Load calendar
3. Should be responsive

### Email Performance
- Emails send in <10 seconds: ✓ Good
- Emails send in 10-30 seconds: ⚠️ Acceptable
- Emails don't arrive: ❌ Check configuration

---

## 🔐 Security Verification

### Session Management
- [ ] Can't access calendar without login
- [ ] Logout works
- [ ] Can't use old session after logout
- [ ] User can only see own data

### Password Security
- [ ] Password shown as dots on login
- [ ] Password not visible in HTML source
- [ ] Password stored as hash in database

### Email Security
- [ ] Gmail App Password used (not main password)
- [ ] Credentials not in GitHub/code
- [ ] No credentials in console output

---

## 📝 Final Checklist

**Before declaring complete:**
- [ ] All tests above passed
- [ ] No error messages in console
- [ ] Emails arrive successfully
- [ ] Database has real data
- [ ] Can logout and login again
- [ ] All features working

---

## 🎉 Success Criteria

You'll know everything is working when:
✅ App starts without errors  
✅ Can register and login  
✅ Can add meal and receive email  
✅ Can log activity and receive email  
✅ Can generate meal plan  
✅ Calendar displays meals and activities  
✅ Notifications work properly  

---

## 💡 Pro Tips

1. **Always keep MySQL running** while using the app
2. **Check spam folder** for test emails
3. **Use real email address** for testing notifications
4. **Restart app** if you make configuration changes
5. **Check browser console** (F12) for frontend errors

---

## 📞 Troubleshooting Guide

| Symptom | Cause | Solution |
|---------|-------|----------|
| Can't login | Wrong credentials | Check email/password |
| Can't add meal | MySQL down | Start MySQL in XAMPP |
| Emails not arriving | Not configured | Set environment variables |
| App crashes | Import error | Run `pip install -r requirements.txt` |
| Port 5000 in use | Another app running | Kill process or use different port |
| Database not found | MySQL issue | Create database: `CREATE DATABASE dietcalendarplannersys;` |

---

## 📞 Get Help

If something fails:
1. **Check the error message** in terminal
2. **Look at browser console** (F12)
3. **Review troubleshooting section** above
4. **Verify MySQL is running**
5. **Check requirements.txt is installed**

Enjoy your fully functional Diet Calendar Planner! 🎉
