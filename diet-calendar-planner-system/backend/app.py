from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
import sqlite3
import hashlib
import smtplib
from email.mime.text import MimeText
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app, supports_credentials=True)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('diet_planner.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    with open('database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# Email configuration
EMAIL_ADDRESS = 'your-email@gmail.com'
EMAIL_PASSWORD = 'your-app-password'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data['email']
        password = hashlib.sha256(data['password'].encode()).hexdigest()
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                           (email, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['email'] = email
            return jsonify({'success': True, 'user': {'id': user['id'], 'email': email}})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data['email']
    password = hashlib.sha256(data['password'].encode()).hexdigest()
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already exists'})
    finally:
        conn.close()

@app.route('/api/calendar')
def get_calendar():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    conn = get_db_connection()
    meals = conn.execute('''
        SELECT m.*, f.name as food_name, f.calories 
        FROM meals m 
        JOIN foods f ON m.food_id = f.id 
        WHERE m.user_id = ? AND DATE(m.date) = ?
        ORDER BY m.meal_type
    ''', (user_id, date_str)).fetchall()
    conn.close()
    
    return jsonify([dict(meal) for meal in meals])

@app.route('/api/meals', methods=['POST'])
def add_meal():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    conn = get_db_connection()
    
    # Add food if it doesn't exist
    conn.execute('INSERT OR IGNORE INTO foods (name, calories) VALUES (?, ?)',
                (data['food_name'], data['calories']))
    
    food = conn.execute('SELECT id FROM foods WHERE name = ?', (data['food_name'],)).fetchone()
    conn.execute('''
        INSERT INTO meals (user_id, food_id, meal_type, date, notes) 
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, food['id'], data['meal_type'], data['date'], data.get('notes', '')))
    
    conn.commit()
    conn.close()
    
    # Send email notification
    send_email_notification(user_id, data)
    
    return jsonify({'success': True})

@app.route('/api/send-reminder', methods=['POST'])
def send_reminder():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    send_email_notification(user_id, data)
    return jsonify({'success': True})

def send_email_notification(user_id, meal_data):
    conn = get_db_connection()
    user = conn.execute('SELECT email FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        msg = MimeText(f"New meal logged: {meal_data['food_name']} ({meal_data['calories']} cal) - {meal_data['meal_type']}")
        msg['Subject'] = 'Diet Plan Update'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = user['email']
        
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
        except:
            pass  # Silent fail for demo

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)