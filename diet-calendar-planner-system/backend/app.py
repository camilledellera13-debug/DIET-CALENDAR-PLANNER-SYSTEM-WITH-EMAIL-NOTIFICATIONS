from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_cors import CORS
from database import get_db_connection, migrate_existing_db
import hashlib
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.secret_key = 'your-secret-key-change-in-production'
CORS(app, supports_credentials=True)
# Print debug info to see where templates are
print(f"Current directory: {os.getcwd()}")
print(f"Template folder path: {os.path.join(os.path.dirname(__file__), 'templates')}")
print(f"Templates exist: {os.path.exists(os.path.join(os.path.dirname(__file__), 'templates'))}")

# Initialize database on startup
migrate_existing_db()

# Email configuration
EMAIL_ADDRESS = 'your-email@gmail.com'
EMAIL_PASSWORD = 'your-app-password'

# Serve static files (CSS, JS)
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('css', filename)

@app.route('/activities.html')
def activities_page():
    """Serve the activities recommendation page"""
    if not session.get('user_id'):
        return render_template('login.html')
    return render_template('activities.html')

@app.route('/calendar.html')
def calendar_page():
    """Serve the calendar page"""
    if not session.get('user_id'):
        return render_template('login.html')
    return render_template('calendar.html')

@app.route('/test')
def test():
    return "<h1>Flask is working!</h1><p>If you see this, the server is running correctly.</p>"


@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)

@app.route('/')
def index():
    # Check if user is logged in via session
    if session.get('user_id'):
        return render_template('index.html')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'})
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        user = conn.execute('SELECT userid as id, email, goal, name FROM users WHERE email = ? AND password = ?', 
                           (email, hashed_password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['email'] = email
            session['goal'] = user['goal'] if user['goal'] else 'maintain'
            return jsonify({'success': True, 'user': {'id': user['id'], 'email': email, 'goal': session['goal']}})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    goal = data.get('goal', 'maintain')
    name = data.get('name', '')
    age = data.get('age')
    weight = data.get('weight')
    height = data.get('height')
    
    # Validate required fields
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'})
    
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db_connection()
    try:
        conn.execute('''INSERT INTO users (email, password, goal, name, age, weight, height) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                    (email, hashed_password, goal, name, age, weight, height))
        conn.commit()
        return jsonify({'success': True, 'message': 'Registration successful!'})
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'message': 'Email already exists or invalid data'})
    finally:
        conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/meals/<date>')
def get_meals_by_date(date):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    meals = conn.execute('''
        SELECT m.*, GROUP_CONCAT(f.foodname, ', ') as food_names, 
               SUM(f.calories * mf.quantity) as total_calories
        FROM meal m
        JOIN dietplan dp ON m.planid = dp.planid
        JOIN mealfood mf ON m.mealid = mf.mealid
        JOIN fooditem f ON mf.foodid = f.foodid
        WHERE dp.userid = ? AND m.mealdate = ?
        GROUP BY m.mealid
        ORDER BY m.mealtype
    ''', (user_id, date)).fetchall()
    conn.close()
    
    return jsonify([dict(meal) for meal in meals])

@app.route('/api/add-meal', methods=['POST'])
def add_meal():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    conn = get_db_connection()
    
    try:
        plan = conn.execute('''
            SELECT planid FROM dietplan 
            WHERE userid = ? AND startdate <= ? AND (enddate >= ? OR enddate IS NULL)
        ''', (user_id, data['date'], data['date'])).fetchone()
        
        if not plan:
            return jsonify({'error': 'No active diet plan found'}), 404
        
        cursor = conn.execute('''
            INSERT INTO meal (planid, mealtype, mealdate, totalcalories)
            VALUES (?, ?, ?, ?)
        ''', (plan['planid'], data['meal_type'], data['date'], data['calories']))
        
        meal_id = cursor.lastrowid
        
        for food in data['foods']:
            food_item = conn.execute('SELECT foodid FROM fooditem WHERE foodname = ?', 
                                    (food['name'],)).fetchone()
            
            if not food_item:
                cursor_food = conn.execute('''
                    INSERT INTO fooditem (foodname, calories, protein, carbs, fats)
                    VALUES (?, ?, ?, ?, ?)
                ''', (food['name'], food['calories'], food.get('protein', 0), 
                      food.get('carbs', 0), food.get('fats', 0)))
                food_id = cursor_food.lastrowid
            else:
                food_id = food_item['foodid']
            
            conn.execute('''
                INSERT INTO mealfood (mealid, foodid, quantity, servingsize)
                VALUES (?, ?, ?, ?)
            ''', (meal_id, food_id, food.get('quantity', 1), food.get('servingsize', '')))
        
        conn.commit()
        send_email_notification(user_id, data)
        
        return jsonify({'success': True, 'meal_id': meal_id})
        
    except Exception as e:
        conn.rollback()
        print(f"Error adding meal: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/progress', methods=['POST'])
def log_progress():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    conn = get_db_connection()
    
    try:
        conn.execute('''
            INSERT OR REPLACE INTO progresslog (user_id, date, weight, notes)
            VALUES (?, ?, ?, ?)
        ''', (user_id, data['date'], data['weight'], data.get('notes', '')))
        
        conn.execute('UPDATE users SET weight = ? WHERE userid = ?', 
                    (data['weight'], user_id))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/water', methods=['POST'])
def log_water():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    conn = get_db_connection()
    
    try:
        conn.execute('''
            INSERT OR REPLACE INTO waterintake (userid, date, amountml)
            VALUES (?, ?, ?)
        ''', (user_id, data['date'], data['amount_ml']))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/activity-recommendations', methods=['GET'])
def get_activity_recommendations():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    
    user = conn.execute('SELECT goal, weight, name FROM users WHERE userid = ?', (user_id,)).fetchone()
    user_goal = user['goal'] if user and user['goal'] else 'maintain'
    
    if user_goal == 'lose':
        activities = conn.execute('''
            SELECT * FROM activities 
            WHERE goal_type IN ('lose', 'all')
            AND intensity = 'high'
            ORDER BY calories_per_minute DESC
        ''').fetchall()
        weekly_target_minutes = 150
        weekly_target_calories = 1200
        recommendation_reason = "To achieve your weight loss goal, high-intensity activities like jogging will help burn more calories efficiently."
        
    elif user_goal == 'gain':
        activities = conn.execute('''
            SELECT * FROM activities 
            WHERE goal_type IN ('gain', 'all')
            AND intensity = 'low'
            ORDER BY calories_per_minute ASC
        ''').fetchall()
        weekly_target_minutes = 60
        weekly_target_calories = 200
        recommendation_reason = "For weight gain, focus on light activities to maintain health without burning excess calories."
        
    else:
        activities = conn.execute('''
            SELECT * FROM activities 
            WHERE goal_type IN ('maintain', 'all')
            AND intensity = 'medium'
            ORDER BY calories_per_minute DESC
        ''').fetchall()
        weekly_target_minutes = 90
        weekly_target_calories = 600
        recommendation_reason = "To maintain your weight, moderate activities will help balance calorie intake and expenditure."
    
    weekly_activities = conn.execute('''
        SELECT a.name, ua.duration_minutes, ua.date, a.calories_per_minute
        FROM user_activities ua
        JOIN activities a ON ua.activity_id = a.id
        WHERE ua.user_id = ? AND ua.date >= date('now', '-7 days')
        ORDER BY ua.date DESC
    ''', (user_id,)).fetchall()
    
    total_minutes = sum(act['duration_minutes'] for act in weekly_activities)
    total_calories = sum(act['duration_minutes'] * act['calories_per_minute'] for act in weekly_activities)
    
    conn.close()
    
    return jsonify({
        'goal': user_goal,
        'recommendations': [dict(activity) for activity in activities],
        'weekly_target_minutes': weekly_target_minutes,
        'weekly_target_calories': weekly_target_calories,
        'recommendation_reason': recommendation_reason,
        'weekly_summary': {
            'total_minutes': total_minutes,
            'total_calories': int(total_calories),
            'remaining_minutes': max(0, weekly_target_minutes - total_minutes),
            'remaining_calories': max(0, weekly_target_calories - int(total_calories)),
            'activities': [dict(act) for act in weekly_activities]
        },
        'message': get_goal_message(user_goal)
    })

@app.route('/api/log-activity', methods=['POST'])
def log_activity():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    activity_id = data['activity_id']
    duration_minutes = data['duration_minutes']
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    conn = get_db_connection()
    
    activity = conn.execute('SELECT calories_per_minute FROM activities WHERE id = ?', 
                           (activity_id,)).fetchone()
    
    if not activity:
        conn.close()
        return jsonify({'error': 'Activity not found'}), 404
    
    calories_burned = int(duration_minutes * activity['calories_per_minute'])
    
    conn.execute('''
        INSERT INTO user_activities (user_id, activity_id, duration_minutes, date, calories_burned)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, activity_id, duration_minutes, date, calories_burned))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'calories_burned': calories_burned,
        'message': f"Logged {duration_minutes} minutes of activity! 🔥"
    })

def get_goal_message(goal):
    messages = {
        'lose': "🔥 Focus on high-intensity activities like jogging, running, and HIIT to maximize calorie burn!",
        'gain': "💪 Focus on strength training and light activities. Avoid excessive cardio to preserve calories for muscle growth.",
        'maintain': "⚖️ Balance is key! Mix moderate activities with your regular routine."
    }
    return messages.get(goal, "Stay active and healthy!")

def send_email_notification(user_id, meal_data):
    conn = get_db_connection()
    user = conn.execute('SELECT email FROM users WHERE userid = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        try:
            msg = MIMEText(f"New meal logged: {meal_data['meal_type']} with {len(meal_data['foods'])} items")
            msg['Subject'] = 'Diet Plan Update'
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = user['email']
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
        except:
            pass  # Silent fail for demo

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('css', exist_ok=True)
    os.makedirs('js', exist_ok=True)
    
    app.run(debug=True, port=5000)