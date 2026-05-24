# 🐛 Troubleshooting: Login/Register Errors

## Error: "Unexpected token '<' at position 0" / "!doctype is not valid JSON"

This error means the backend returned **HTML** instead of **JSON**.

---

## ✅ I've Already Fixed This!

The backend now:
1. ✅ Always returns JSON (never HTML)
2. ✅ Has proper error handling on all auth endpoints
3. ✅ Has a global error handler for unhandled exceptions
4. ✅ Includes a health check endpoint to test

---

## 🔍 How to Verify the Fix

### Step 1: Check Backend Health
```
Open this in your browser:
http://localhost:5000/test
```

**Expected response:**
```json
{
  "success": true,
  "message": "Backend is working and MySQL is connected",
  "status": "healthy"
}
```

✅ If you see this JSON: **Everything is working!**

❌ If you see HTML with `<!doctype`: The backend crashed

❌ If you see `"status": "unhealthy"`: **MySQL is not running**

---

### Step 2: Try Logging In

1. Go to http://localhost:5000
2. Enter any email and password
3. Click "Login"

**Expected:** One of these JSON responses:
```json
{"success": false, "message": "Invalid credentials"}
```
or if MySQL fails:
```json
{"success": false, "message": "Database connection error. Make sure MySQL is running"}
```

✅ If you see JSON: **The fix is working!**

❌ If you see HTML: **Restart the Flask app**

---

## 🔧 If You Still See HTML Error

### Option 1: Restart Everything
1. Stop Flask app (Ctrl+C)
2. Restart MySQL (XAMPP Control Panel → Stop → Start)
3. Start Flask again: `python backend/app.py`
4. Refresh browser: Ctrl+Shift+R (hard refresh)

### Option 2: Clear Browser Cache
1. Press Ctrl+Shift+Delete
2. Select "All time"
3. Check "Cached images and files"
4. Click "Clear data"
5. Try again

### Option 3: Check Flask Console
Look at the terminal where Flask is running:
```
Should see:
  ✅ Database initialized
  🚀 Server running at http://localhost:5000

Should NOT see error messages like:
  ❌ Error
  ❌ Exception
  ❌ Connection refused
```

If you see errors, MySQL might not be running.

---

## 📋 Common Scenarios

### Scenario 1: MySQL Not Running
**What you see:**
```
Error: Database connection error. Make sure MySQL is running
```

**Fix:**
1. Open XAMPP Control Panel
2. Click "Start" next to MySQL
3. Refresh page

---

### Scenario 2: Invalid Credentials (Normal)
**What you see:**
```
Login failed: Invalid credentials
```

**This is correct!** Your email/password are wrong. Try:
- Different email
- Different password
- Register new account first

---

### Scenario 3: Flask App Crashed
**What you see:**
```
Error connecting to the backend
```

**Fix:**
1. Check Flask terminal for errors
2. Stop app: Ctrl+C
3. Restart: `python backend/app.py`
4. Try again

---

### Scenario 4: Port 5000 Already in Use
**What you see:**
```
Address already in use
```

**Fix:**
```powershell
# Find process on port 5000
netstat -ano | findstr :5000

# Kill it (replace 1234 with the PID)
taskkill /PID 1234 /F

# Or restart your computer
```

---

## ✨ What Changed in the Code

### Before
```python
@app.route('/login', methods=['POST'])
def login():
    # If any error happens here:
    data = request.json  # Could fail
    cursor = mysql.connection.cursor()  # Could fail
    cursor.execute(...)  # Could fail
    # Flask returns HTML error page instead of JSON
```

### After
```python
@app.route('/login', methods=['POST'])
def login():
    try:
        # All code wrapped in try-catch
        data = request.json
        # ...
        return jsonify({'success': True, ...})
    except Exception as db_error:
        # Returns JSON even on error
        return jsonify({'success': False, 'message': '...'})
    except Exception as e:
        return jsonify({'success': False, 'message': '...'})

# Plus global error handlers:
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({'success': False, 'message': str(error)})
```

This ensures **all responses are JSON**, never HTML.

---

## 🧪 Quick Test Script

**Run this to test backend:**
```powershell
# Windows PowerShell
curl http://localhost:5000/test

# Should return:
# {"success":true,"message":"Backend is working...","status":"healthy"}
```

**Or double-click:**
```
TEST_BACKEND.bat
```

---

## 📞 Still Having Issues?

### Step 1: Check MySQL
```powershell
mysql -u root -p
# Just press Enter for password

# You should see: mysql>
# If not, MySQL is not running
```

### Step 2: Check Flask
```powershell
python backend/app.py

# Should show:
# ✅ Database initialized
# 🚀 Server running at http://localhost:5000
```

### Step 3: Test Endpoint
```
Browser: http://localhost:5000/test
Should return JSON, not HTML
```

### Step 4: Check Browser Console
1. Open browser (Chrome, Firefox, Edge)
2. Press F12
3. Go to "Console" tab
4. Try to login
5. Look for error messages
6. Screenshot and share with developer

---

## ✅ Success Checklist

- [ ] http://localhost:5000/test returns JSON
- [ ] Can see login page
- [ ] Can enter email and password
- [ ] See JSON response (error or success)
- [ ] No "<!doctype" errors
- [ ] No HTML page displayed
- [ ] Can register new account
- [ ] Can login with valid credentials

---

## 🎉 You're Ready!

The backend now properly handles all errors and always returns JSON instead of HTML.

**To start:**
1. Start MySQL
2. Run `python backend/app.py`
3. Go to http://localhost:5000
4. Register and login!

No more "unexpected token" errors! 🎊
