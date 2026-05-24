# Email Notification Setup Guide

## How to Enable Email Notifications

Your Diet Calendar Planner system already has **email notifications built-in**! Follow these steps to activate them.

---

## Step 1: Create or Use a Gmail Account

Use any Gmail account that will send the notifications. You can create a dedicated one if you prefer.

---

## Step 2: Enable 2-Step Verification

1. Go to: https://myaccount.google.com/security
2. Look for "2-Step Verification" and enable it
3. Follow Google's verification process (you may need to verify your phone)

---

## Step 3: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select:
   - App: **Mail**
   - Device: **Windows/Mac (select your OS)**
3. Google will generate a 16-character password
4. **Copy this password** - you'll need it

---

## Step 4: Configure Environment Variables

### Option A: Using Environment Variables (Recommended)

On Windows (PowerShell):
```powershell
$env:MAIL_USERNAME = "your-gmail@gmail.com"
$env:MAIL_PASSWORD = "xxxx xxxx xxxx xxxx"
```

On Windows (Command Prompt):
```cmd
set MAIL_USERNAME=your-gmail@gmail.com
set MAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

Then run your Flask app.

### Option B: Direct Configuration in app.py

Edit `backend/app.py` and find this section:

```python
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')  
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')  
```

Replace with:

```python
app.config['MAIL_USERNAME'] = 'your-gmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'xxxx xxxx xxxx xxxx'
```

⚠️ **Note**: Don't commit your password to version control!

---

## Step 5: Test the Configuration

1. Start your Flask app
2. Create an account with a **real email address**
3. Log a meal or activity
4. Check your inbox for the notification email

---

## What Users Will Receive

### 🍽️ Meal Notification Email
- Contains meal type (Breakfast, Lunch, etc.)
- Food name
- Calories logged
- Date logged
- Motivational tip

### 🏃 Activity Notification Email
- Activity name
- Duration in minutes
- Calories burned
- Intensity level
- Date logged
- Motivational message

---

## Troubleshooting

**❌ "Email service not configured" message**
- Set `MAIL_USERNAME` and `MAIL_PASSWORD` environment variables
- Or update app.py directly with credentials

**❌ "Failed to send email" error**
- Verify Gmail 2-Step Verification is enabled
- Check App Password is correct (spaces matter!)
- Check your firewall isn't blocking SMTP port 587

**❌ Emails not arriving**
- Check spam/junk folder
- Verify email address is correct in user profile
- Test with a different recipient email address

**✅ Successful send**
- You'll see `✅ Meal notification email sent to user@example.com` in console
- User receives styled HTML email

---

## Email Triggers

Emails automatically send when:
1. User adds a meal via the calendar
2. User logs an exercise/activity
3. User confirms a calendar-based activity

All emails are sent **non-blocking** in background threads.

---

## Security Notes

1. **Never commit passwords** to your repository
2. Use environment variables in production
3. Gmail app passwords are better than your main password
4. Consider using `.env` file for local development:

```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

Then add to `.gitignore`:
```
.env
```

---

## Additional Resources

- Flask-Mail Documentation: https://pythonhosted.org/Flask-Mail/
- Gmail App Passwords: https://myaccount.google.com/apppasswords
- Gmail Security: https://myaccount.google.com/security
