from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_cors import CORS
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import hashlib
import os
import threading
import random
from datetime import datetime, timedelta

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

app.secret_key = 'your-secret-key-change-in-production'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dietcalendarplannersys'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Mail Configuration (Optional)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ''

mysql = MySQL(app)
mail = Mail(app)
CORS(app, supports_credentials=True)


# ============= MEAL PLANNER CLASS =============
class MealPlanner:
    """Automatically generates meal plans based on user's weight goals"""

    LOW_CALORIE_MEALS = {
        'breakfast': [
            {'name': 'Greek Yogurt with Berries', 'calories': 250, 'protein': 20, 'carbs': 30, 'fats': 5},
            {'name': 'Oatmeal with Banana', 'calories': 300, 'protein': 10, 'carbs': 55, 'fats': 5},
            {'name': 'Egg White Scramble with Spinach', 'calories': 200, 'protein': 18, 'carbs': 5, 'fats': 6},
            {'name': 'Smoothie Bowl', 'calories': 280, 'protein': 12, 'carbs': 45, 'fats': 4},
            {'name': 'Cottage Cheese with Peaches', 'calories': 220, 'protein': 24, 'carbs': 15, 'fats': 6},
            {'name': 'Avocado Toast', 'calories': 280, 'protein': 8, 'carbs': 25, 'fats': 15},
        ],
        'lunch': [
            {'name': 'Grilled Chicken Salad', 'calories': 350, 'protein': 35, 'carbs': 15, 'fats': 12},
            {'name': 'Quinoa Bowl', 'calories': 380, 'protein': 12, 'carbs': 60, 'fats': 10},
            {'name': 'Turkey Wrap', 'calories': 320, 'protein': 28, 'carbs': 35, 'fats': 10},
            {'name': 'Lentil Soup', 'calories': 350, 'protein': 18, 'carbs': 55, 'fats': 6},
            {'name': 'Tuna Lettuce Wraps', 'calories': 300, 'protein': 32, 'carbs': 10, 'fats': 14},
            {'name': 'Vegetable Stir-fry', 'calories': 320, 'protein': 15, 'carbs': 40, 'fats': 12},
        ],
        'dinner': [
            {'name': 'Baked Salmon with Asparagus', 'calories': 400, 'protein': 35, 'carbs': 10, 'fats': 22},
            {'name': 'Lean Turkey Meatballs', 'calories': 380, 'protein': 38, 'carbs': 15, 'fats': 18},
            {'name': 'Shrimp Broccoli Stir-fry', 'calories': 320, 'protein': 30, 'carbs': 20, 'fats': 12},
            {'name': 'Stuffed Bell Peppers', 'calories': 350, 'protein': 32, 'carbs': 25, 'fats': 14},
            {'name': 'White Fish with Veggies', 'calories': 340, 'protein': 34, 'carbs': 15, 'fats': 10},
            {'name': 'Chicken Vegetable Soup', 'calories': 300, 'protein': 28, 'carbs': 25, 'fats': 8},
        ],
        'snack': [
            {'name': 'Apple with Peanut Butter', 'calories': 150, 'protein': 5, 'carbs': 20, 'fats': 7},
            {'name': 'Protein Shake', 'calories': 120, 'protein': 24, 'carbs': 3, 'fats': 2},
            {'name': 'Handful of Almonds', 'calories': 140, 'protein': 5, 'carbs': 5, 'fats': 12},
            {'name': 'Rice Cake with Cheese', 'calories': 100, 'protein': 8, 'carbs': 12, 'fats': 3},
            {'name': 'Greek Yogurt', 'calories': 90, 'protein': 15, 'carbs': 6, 'fats': 0},
            {'name': 'Carrots with Hummus', 'calories': 120, 'protein': 4, 'carbs': 15, 'fats': 5},
        ]
    }

    HIGH_CALORIE_MEALS = {
        'breakfast': [
            {'name': 'Protein Pancakes', 'calories': 650, 'protein': 30, 'carbs': 85, 'fats': 20},
            {'name': 'Full Breakfast', 'calories': 750, 'protein': 35, 'carbs': 60, 'fats': 40},
            {'name': 'Peanut Butter Smoothie', 'calories': 600, 'protein': 25, 'carbs': 80, 'fats': 22},
            {'name': 'Oatmeal with Nuts', 'calories': 550, 'protein': 18, 'carbs': 85, 'fats': 18},
            {'name': 'Breakfast Burrito', 'calories': 700, 'protein': 32, 'carbs': 55, 'fats': 38},
            {'name': 'French Toast', 'calories': 620, 'protein': 20, 'carbs': 90, 'fats': 18},
        ],
        'lunch': [
            {'name': 'Chicken Alfredo', 'calories': 750, 'protein': 35, 'carbs': 85, 'fats': 30},
            {'name': 'Cheeseburger with Fries', 'calories': 850, 'protein': 42, 'carbs': 75, 'fats': 42},
            {'name': 'Beef and Rice Bowl', 'calories': 700, 'protein': 38, 'carbs': 80, 'fats': 25},
            {'name': 'Tuna Melt Sandwich', 'calories': 680, 'protein': 32, 'carbs': 70, 'fats': 30},
            {'name': 'Chicken Quesadilla', 'calories': 720, 'protein': 35, 'carbs': 65, 'fats': 35},
            {'name': 'Pulled Pork Sandwich', 'calories': 780, 'protein': 40, 'carbs': 85, 'fats': 28},
        ],
        'dinner': [
            {'name': 'Steak with Potatoes', 'calories': 850, 'protein': 50, 'carbs': 60, 'fats': 42},
            {'name': 'Spaghetti and Meatballs', 'calories': 780, 'protein': 35, 'carbs': 95, 'fats': 28},
            {'name': 'Fried Rice with Shrimp', 'calories': 680, 'protein': 28, 'carbs': 90, 'fats': 22},
            {'name': 'Chicken Parmesan', 'calories': 820, 'protein': 45, 'carbs': 85, 'fats': 32},
            {'name': 'Beef Noodle Stir-fry', 'calories': 700, 'protein': 35, 'carbs': 80, 'fats': 25},
            {'name': 'Salmon with Rice', 'calories': 720, 'protein': 38, 'carbs': 55, 'fats': 38},
        ],
        'snack': [
            {'name': 'Protein Bar with Banana', 'calories': 350, 'protein': 20, 'carbs': 45, 'fats': 12},
            {'name': 'Trail Mix', 'calories': 350, 'protein': 10, 'carbs': 30, 'fats': 25},
            {'name': 'Peanut Butter Sandwich', 'calories': 380, 'protein': 15, 'carbs': 40, 'fats': 20},
            {'name': 'Protein Smoothie', 'calories': 400, 'protein': 30, 'carbs': 50, 'fats': 10},
            {'name': 'Yogurt Parfait', 'calories': 350, 'protein': 20, 'carbs': 45, 'fats': 12},
            {'name': 'Cheese and Crackers', 'calories': 320, 'protein': 12, 'carbs': 30, 'fats': 18},
        ]
    }

    @staticmethod
    def calculate_calorie_target(weight, height, age, gender, goal, activity_level='moderate'):
        """Calculate daily calorie target based on user's metrics and goal"""
        if gender == 'Male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        multipliers = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'active': 1.725, 'very_active': 1.9}
        tdee = bmr * multipliers.get(activity_level, 1.55)

        if goal == 'lose':
            return int(tdee - 500)
        elif goal == 'gain':
            return int(tdee + 500)
        return int(tdee)

    @staticmethod
    def generate_meal_plan_from_database(goal, calorie_target, days=7):
        """Generate meal plan using food items from database"""
        cursor = mysql.connection.cursor()

        cursor.execute('SELECT foodid, foodname, calories, protein, carbs, fats FROM fooditem ORDER BY calories')
        all_foods = cursor.fetchall()

        if not all_foods:
            cursor.close()
            return None

        # Categorize foods based on goal
        if goal == 'lose':
            meal_ranges = {
                'breakfast': (0, 150), 'lunch': (150, 350), 'dinner': (200, 400), 'snack': (0, 120)
            }
        elif goal == 'gain':
            meal_ranges = {
                'breakfast': (200, 999), 'lunch': (350, 999), 'dinner': (400, 999), 'snack': (150, 999)
            }
        else:
            meal_ranges = {
                'breakfast': (100, 250), 'lunch': (250, 450), 'dinner': (300, 500), 'snack': (80, 180)
            }

        categorized = {}
        for meal_type, (min_cal, max_cal) in meal_ranges.items():
            categorized[meal_type] = [f for f in all_foods if min_cal <= f['calories'] <= max_cal] or all_foods[:10]

        meal_plan = {}
        for day in range(days):
            date = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
            used_ids = set()
            day_meals = {}

            for meal_type, foods in categorized.items():
                available = [f for f in foods if f['foodid'] not in used_ids] or foods
                selected = random.choice(available)
                used_ids.add(selected['foodid'])

                day_meals[meal_type] = {
                    'name': selected['foodname'],
                    'calories': float(selected['calories']),
                    'protein': float(selected['protein'] or 0),
                    'carbs': float(selected['carbs'] or 0),
                    'fats': float(selected['fats'] or 0),
                    'foodid': selected['foodid']
                }

            day_meals['total_calories'] = sum(m['calories'] for m in day_meals.values())
            day_meals['target_calories'] = calorie_target
            meal_plan[date] = day_meals

        cursor.close()
        return meal_plan

    @staticmethod
    def get_nutrition_tips(goal, meal_type):
        """Get nutrition tips based on goal"""
        tips = {
            'lose': {
                'breakfast': "High protein breakfast keeps you full longer!",
                'lunch': "Load up on leafy greens and lean protein.",
                'dinner': "Avoid carbs late at night. Focus on protein.",
                'snack': "Choose raw vegetables or nuts in moderation."
            },
            'gain': {
                'breakfast': "Add healthy fats like peanut butter or avocado.",
                'lunch': "Include complex carbs like quinoa or brown rice.",
                'dinner': "Double your protein portion for more calories.",
                'snack': "Choose calorie-dense snacks like trail mix."
            },
            'maintain': {
                'breakfast': "Balance carbs and protein for steady energy.",
                'lunch': "Practice portion control with variety.",
                'dinner': "Eat dinner 2-3 hours before bedtime.",
                'snack': "Smart snacking prevents overeating."
            }
        }
        return tips.get(goal, {}).get(meal_type, "Stay consistent with your meal planning!")

    @staticmethod
    def generate_daily_meals_from_database(goal, calorie_target):
        """Generate a single day's meals from database"""
        cursor = mysql.connection.cursor()

        cursor.execute('SELECT foodid, foodname, calories, protein, carbs, fats FROM fooditem ORDER BY RAND() LIMIT 30')
        all_foods = cursor.fetchall()
        cursor.close()

        if not all_foods:
            return None

        # Categorize foods based on goal
        if goal == 'lose':
            breakfast_foods = [f for f in all_foods if f['calories'] <= 150] or all_foods[:5]
            lunch_foods = [f for f in all_foods if 150 <= f['calories'] <= 350] or all_foods[5:10]
            dinner_foods = [f for f in all_foods if 200 <= f['calories'] <= 400] or all_foods[8:13]
            snack_foods = [f for f in all_foods if f['calories'] <= 120] or all_foods[:3]
        elif goal == 'gain':
            breakfast_foods = [f for f in all_foods if f['calories'] >= 200] or all_foods[-5:]
            lunch_foods = [f for f in all_foods if f['calories'] >= 350] or all_foods[-8:-3]
            dinner_foods = [f for f in all_foods if f['calories'] >= 400] or all_foods[-10:-5]
            snack_foods = [f for f in all_foods if f['calories'] >= 150] or all_foods[-4:]
        else:
            breakfast_foods = [f for f in all_foods if 100 <= f['calories'] <= 250] or all_foods[3:8]
            lunch_foods = [f for f in all_foods if 250 <= f['calories'] <= 450] or all_foods[6:11]
            dinner_foods = [f for f in all_foods if 300 <= f['calories'] <= 500] or all_foods[8:13]
            snack_foods = [f for f in all_foods if 80 <= f['calories'] <= 180] or all_foods[2:6]

        return {
            'breakfast': {
                'name': random.choice(breakfast_foods)['foodname'],
                'calories': float(random.choice(breakfast_foods)['calories']),
                'protein': float(random.choice(breakfast_foods).get('protein', 0)),
                'carbs': float(random.choice(breakfast_foods).get('carbs', 0)),
                'fats': float(random.choice(breakfast_foods).get('fats', 0))
            },
            'lunch': {
                'name': random.choice(lunch_foods)['foodname'],
                'calories': float(random.choice(lunch_foods)['calories']),
                'protein': float(random.choice(lunch_foods).get('protein', 0)),
                'carbs': float(random.choice(lunch_foods).get('carbs', 0)),
                'fats': float(random.choice(lunch_foods).get('fats', 0))
            },
            'dinner': {
                'name': random.choice(dinner_foods)['foodname'],
                'calories': float(random.choice(dinner_foods)['calories']),
                'protein': float(random.choice(dinner_foods).get('protein', 0)),
                'carbs': float(random.choice(dinner_foods).get('carbs', 0)),
                'fats': float(random.choice(dinner_foods).get('fats', 0))
            },
            'snack': {
                'name': random.choice(snack_foods)['foodname'],
                'calories': float(random.choice(snack_foods)['calories']),
                'protein': float(random.choice(snack_foods).get('protein', 0)),
                'carbs': float(random.choice(snack_foods).get('carbs', 0)),
                'fats': float(random.choice(snack_foods).get('fats', 0))
            },
            'total_calories': 0,
            'target_calories': calorie_target
        }

# ============= HELPER FUNCTIONS =============
def get_goal_recommendations(goal):
    recommendations = {
        'lose': "💡 Focus on portion control, increase protein intake, drink water before meals!",
        'gain': "💡 Eat frequently (5-6 meals/day), add healthy fats, include protein with every meal!",
        'maintain': "💡 Balance your macros and maintain consistent physical activity!"
    }
    return recommendations.get(goal, "Stay consistent with your meal planning!")


def init_activities_table():
    """Initialize activities and related tables"""
    cursor = mysql.connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            calories_per_minute DECIMAL(5,2) NOT NULL,
            intensity ENUM('low', 'medium', 'high') NOT NULL,
            goal_type ENUM('lose', 'gain', 'maintain', 'all') NOT NULL,
            description TEXT,
            icon VARCHAR(10)
        )
    ''')

    cursor.execute("SELECT COUNT(*) as count FROM activities")
    if cursor.fetchone()['count'] == 0:
        activities_data = [
            ('Jogging', 11.5, 'high', 'lose', 'Great for burning calories', '🏃'),
            ('Running', 13.0, 'high', 'lose', 'High-intensity cardio', '🏃‍♀️'),
            ('Brisk Walking', 5.5, 'medium', 'maintain', 'Low-impact activity', '🚶'),
            ('Yoga', 4.0, 'low', 'maintain', 'Improves flexibility', '🧘'),
            ('Light Walking', 3.5, 'low', 'gain', 'Gentle activity', '🚶'),
            ('Weight Training', 8.5, 'medium', 'gain', 'Build muscle', '💪'),
        ]
        for act in activities_data:
            cursor.execute('''
                INSERT INTO activities (name, calories_per_minute, intensity, goal_type, description, icon)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', act)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activities (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            activity_id INT NOT NULL,
            duration_minutes INT NOT NULL,
            date DATE NOT NULL,
            calories_burned INT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(userid) ON DELETE CASCADE,
            FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            preference_key VARCHAR(100) NOT NULL,
            preference_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_preference (user_id, preference_key),
            FOREIGN KEY (user_id) REFERENCES user(userid) ON DELETE CASCADE
        )
    ''')

    mysql.connection.commit()
    cursor.close()


# ============= EMAIL FUNCTIONS =============
def send_meal_notification_email(user_email, user_name, meal_data):
    try:
        if not app.config['MAIL_USERNAME']:
            return True

        html = f"""
        <html><body>
            <div style="max-width:600px;margin:0 auto;padding:20px;">
                <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;text-align:center;">
                    <h1>🍽️ Meal Logged!</h1>
                    <p>Hi {user_name}</p>
                </div>
                <div style="background:#f7fafc;padding:20px;">
                    <h2>{meal_data['meal_type'].title()}</h2>
                    <p>Food: {meal_data['food_name']}</p>
                    <p>🔥 Calories: {meal_data['calories']} cal</p>
                    <p>Date: {meal_data['date']}</p>
                </div>
            </div>
        </body></html>
        """
        msg = Message("Meal Logged - Diet Planner", recipients=[user_email], html=html)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_activity_notification_email(user_email, user_name, activity_data):
    try:
        if not app.config['MAIL_USERNAME']:
            return True

        html = f"""
        <html><body>
            <div style="max-width:600px;margin:0 auto;padding:20px;">
                <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;text-align:center;">
                    <h1>🏃 Activity Logged!</h1>
                    <p>Great job {user_name}!</p>
                </div>
                <div style="background:#f7fafc;padding:20px;">
                    <h2>{activity_data['icon']} {activity_data['name']}</h2>
                    <p>Duration: {activity_data['duration']} minutes</p>
                    <p>🔥 Calories Burned: {activity_data['calories_burned']} cal</p>
                </div>
            </div>
        </body></html>
        """
        msg = Message("Activity Logged - Diet Planner", recipients=[user_email], html=html)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


# ============= FLASK ROUTES =============
@app.route('/')
def index():
    if session.get('user_id'):
        return render_template('index.html')
    return render_template('login.html')


@app.route('/activities.html')
def activities_page():
    if not session.get('user_id'):
        return render_template('login.html')
    return render_template('activities.html')


@app.route('/calendar.html')
def calendar_page():
    if not session.get('user_id'):
        return render_template('login.html')
    return render_template('calendar.html')


@app.route('/test')
def test():
    return "<h1>Flask is working!</h1>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'})

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT userid as id, email, goal, name FROM user WHERE email = %s AND password = %s',
                       (email, hashed_password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user['id']
            session['email'] = email
            session['goal'] = user['goal'] or 'maintain'
            return jsonify({'success': True, 'user': dict(user)})
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

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'})

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor = mysql.connection.cursor()

    try:
        cursor.execute('''
            INSERT INTO user (name, email, password, goal, age, weight, height)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (name, email, hashed_password, goal, age, weight, height))
        mysql.connection.commit()

        user_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO dietplan (userid, planname, description, startdate, enddate)
            VALUES (%s, 'My Diet Plan', 'Personalized diet plan', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 3 MONTH))
        ''', (user_id,))
        mysql.connection.commit()

        return jsonify({'success': True, 'message': 'Registration successful!'})
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'message': 'Email already exists'})
    finally:
        cursor.close()


@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/api/generate-meal-plan', methods=['POST'])
def generate_meal_plan():
    """Generate personalized meal plan with custom date range"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    data = request.json
    target_weight = float(data.get('target_weight', 0))
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    days = data.get('days', 7)

    # If dates provided, calculate days from dates
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        days = (end_date - start_date).days + 1
        if days < 1:
            days = 7
    else:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days - 1)

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT u.weight, u.height, u.age, u.gender, u.goal,
               COALESCE(p.weight, u.weight) as current_weight
        FROM user u
        LEFT JOIN progresslog p ON u.userid = p.user_id 
        WHERE u.userid = %s 
        ORDER BY p.date DESC LIMIT 1
    ''', (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    current_weight = float(user['current_weight'] or user['weight'] or 70)
    goal = user['goal']

    # Auto-determine goal based on target weight
    if target_weight > 0:
        if target_weight < current_weight:
            goal = 'lose'
        elif target_weight > current_weight:
            goal = 'gain'

    calorie_target = MealPlanner.calculate_calorie_target(
        weight=current_weight,
        height=float(user['height'] or 170),
        age=int(user['age'] or 30),
        gender=user['gender'] or 'Male',
        goal=goal
    )

    # Generate meal plan with specific date range
    meal_plan = {}
    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')

        # Generate daily meals from database
        daily_meals = MealPlanner.generate_daily_meals_from_database(goal, calorie_target)
        if daily_meals:
            meal_plan[date] = daily_meals

    if not meal_plan:
        return jsonify({'error': 'No food items found in database'}), 404

    return jsonify({
        'success': True,
        'goal': goal,
        'current_weight': current_weight,
        'target_weight': target_weight,
        'calorie_target': calorie_target,
        'meal_plan': meal_plan,
        'recommendations': get_goal_recommendations(goal),
        'nutrition_tips': {
            'breakfast': MealPlanner.get_nutrition_tips(goal, 'breakfast'),
            'lunch': MealPlanner.get_nutrition_tips(goal, 'lunch'),
            'dinner': MealPlanner.get_nutrition_tips(goal, 'dinner'),
            'snack': MealPlanner.get_nutrition_tips(goal, 'snack')
        }
    })



@app.route('/api/save-generated-meals', methods=['POST'])
def save_generated_meals():
    """Save generated meal plan to database with proper calories"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    meal_plan = request.json.get('meal_plan', {})

    cursor = mysql.connection.cursor()
    saved_count = 0

    try:
        for date, meals in meal_plan.items():
            if date in ['total_calories', 'target_calories']:
                continue

            # Get or create diet plan
            cursor.execute('''
                SELECT planid FROM dietplan 
                WHERE userid = %s AND startdate <= %s AND (enddate >= %s OR enddate IS NULL)
                LIMIT 1
            ''', (user_id, date, date))
            plan = cursor.fetchone()

            if not plan:
                cursor.execute('''
                    INSERT INTO dietplan (userid, planname, description, startdate, enddate)
                    VALUES (%s, 'AI Generated Plan', 'Auto-generated meal plan', %s, DATE_ADD(%s, INTERVAL 1 MONTH))
                ''', (user_id, date, date))
                mysql.connection.commit()
                cursor.execute('SELECT LAST_INSERT_ID() as planid')
                plan = cursor.fetchone()

            for meal_type, meal_data in meals.items():
                if meal_type in ['total_calories', 'target_calories']:
                    continue

                # Get the calories for this meal
                meal_calories = meal_data.get('calories', 0)

                # Insert meal with proper calories
                cursor.execute('''
                    INSERT INTO meal (planid, mealtype, mealdate, totalcalories)
                    VALUES (%s, %s, %s, %s)
                ''', (plan['planid'], meal_type.capitalize(), date, meal_calories))
                meal_id = cursor.lastrowid

                # Check if food exists in database
                cursor.execute('SELECT foodid, calories FROM fooditem WHERE foodname = %s', (meal_data['name'],))
                food = cursor.fetchone()

                if not food:
                    # Insert the food if it doesn't exist
                    cursor.execute('''
                        INSERT INTO fooditem (foodname, calories, protein, carbs, fats)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (meal_data['name'], meal_calories,
                          meal_data.get('protein', 0), meal_data.get('carbs', 0), meal_data.get('fats', 0)))
                    food_id = cursor.lastrowid
                else:
                    food_id = food['foodid']
                    # Update calories if they differ (optional)
                    if float(food['calories']) != meal_calories:
                        cursor.execute('UPDATE fooditem SET calories = %s WHERE foodid = %s', (meal_calories, food_id))

                # Create relationship
                cursor.execute('''
                    INSERT INTO mealfood (mealid, foodid, quantity, servingsize)
                    VALUES (%s, %s, 1, '1 serving')
                ''', (meal_id, food_id))

                saved_count += 1

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            'success': True,
            'saved_count': saved_count,
            'message': f'Successfully saved {saved_count} meals to your calendar!'
        })

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        print(f"Error saving meals: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-stats', methods=['GET'])
def get_user_stats():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT u.weight, u.height, u.age, u.gender, u.goal,
               COALESCE(p.weight, u.weight) as current_weight
        FROM user u
        LEFT JOIN progresslog p ON u.userid = p.user_id 
        WHERE u.userid = %s 
        ORDER BY p.date DESC LIMIT 1
    ''', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'current_weight': float(user['current_weight'] or user['weight'] or 70),
        'height': float(user['height'] or 170),
        'age': int(user['age'] or 30),
        'gender': user['gender'] or 'Male',
        'goal': user['goal'] or 'maintain'
    })


@app.route('/api/all-activities', methods=['GET'])
def get_all_activities():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM activities ORDER BY name')
    activities = cursor.fetchall()
    cursor.close()
    return jsonify([dict(a) for a in activities])


@app.route('/api/calendar-events', methods=['GET'])
def get_calendar_events():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    start_date = request.args.get('start')
    end_date = request.args.get('end')
    user_id = session['user_id']

    cursor = mysql.connection.cursor()
    events = []

    cursor.execute('''
        SELECT m.mealid, m.mealtype, m.mealdate, m.totalcalories as calories
        FROM meal m
        JOIN dietplan dp ON m.planid = dp.planid
        WHERE dp.userid = %s AND m.mealdate BETWEEN %s AND %s
    ''', (user_id, start_date, end_date))

    for meal in cursor.fetchall():
        events.append({
            'id': f"meal_{meal['mealid']}",
            'title': f"🍽️ {meal['mealtype']}",
            'start': str(meal['mealdate']),
            'allDay': True,
            'type': 'meal',
            'calories': float(meal['calories'] or 0),
            'color': '#48bb78'
        })

    cursor.execute('''
        SELECT ua.id, a.name, a.icon, ua.date, ua.duration_minutes, ua.calories_burned
        FROM user_activities ua
        JOIN activities a ON ua.activity_id = a.id
        WHERE ua.user_id = %s AND ua.date BETWEEN %s AND %s
    ''', (user_id, start_date, end_date))

    for act in cursor.fetchall():
        events.append({
            'id': f"activity_{act['id']}",
            'title': f"{act['icon'] or '🏃'} {act['name']} - {act['duration_minutes']} min",
            'start': str(act['date']),
            'allDay': True,
            'type': 'activity',
            'duration': act['duration_minutes'],
            'calories': float(act['calories_burned'] or 0),
            'color': '#ed64a6'
        })

    cursor.close()
    return jsonify(events)


@app.route('/api/daily-summary/<date>', methods=['GET'])
def get_daily_summary(date):
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # Get meals (existing code)
    cursor.execute('''
        SELECT 
            m.mealid, 
            m.mealtype, 
            m.totalcalories,
            GROUP_CONCAT(DISTINCT f.foodname SEPARATOR ', ') as food_names,
            SUM(f.calories * mf.quantity) as calculated_calories
        FROM meal m
        JOIN dietplan dp ON m.planid = dp.planid
        LEFT JOIN mealfood mf ON m.mealid = mf.mealid
        LEFT JOIN fooditem f ON mf.foodid = f.foodid
        WHERE dp.userid = %s AND m.mealdate = %s
        GROUP BY m.mealid, m.mealtype, m.totalcalories
    ''', (user_id, date))
    meals = cursor.fetchall()

    # IMPORTANT: Include the activity ID in the query
    cursor.execute('''
        SELECT ua.id, a.name, ua.duration_minutes, ua.calories_burned
        FROM user_activities ua
        JOIN activities a ON ua.activity_id = a.id
        WHERE ua.user_id = %s AND ua.date = %s
    ''', (user_id, date))
    activities = cursor.fetchall()

    cursor.close()

    # Process activities to ensure id is explicitly included
    activities_list = []
    for act in activities:
        activities_list.append({
            'id': act['id'],  # This is the user_activities.id - CRITICAL!
            'name': act['name'],
            'duration_minutes': act['duration_minutes'],
            'calories_burned': float(act['calories_burned'] or 0)
        })

    total_meal_calories = sum(float(m.get('calculated_calories', 0) or m.get('totalcalories', 0)) for m in meals)
    total_activity_calories = sum(float(a['calories_burned'] or 0) for a in activities)

    return jsonify({
        'date': date,
        'meals': [dict(m) for m in meals],
        'activities': activities_list,  # Now includes 'id' field
        'total_meal_calories': total_meal_calories,
        'total_activity_calories': total_activity_calories
    })
@app.route('/api/log-calendar-activity', methods=['POST'])
def log_calendar_activity():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    cursor.execute('SELECT name, calories_per_minute, intensity, icon FROM activities WHERE id = %s',
                   (data['activity_id'],))
    activity = cursor.fetchone()

    if not activity:
        cursor.close()
        return jsonify({'error': 'Activity not found'}), 404

    calories_burned = int(data['duration_minutes'] * float(activity['calories_per_minute']))

    cursor.execute('''
        INSERT INTO user_activities (user_id, activity_id, duration_minutes, date, calories_burned, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_id, data['activity_id'], data['duration_minutes'], data['date'],
          calories_burned, data.get('notes', '')))
    mysql.connection.commit()

    cursor.execute('SELECT email, name FROM user WHERE userid = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user and user['email'] and '@example.com' not in user['email']:
        thread = threading.Thread(target=send_activity_notification_email,
                                  args=(user['email'], user['name'], {
                                      'name': activity['name'],
                                      'duration': data['duration_minutes'],
                                      'calories_burned': calories_burned,
                                      'date': data['date'],
                                      'intensity': activity['intensity'],
                                      'icon': activity['icon']
                                  }))
        thread.daemon = True
        thread.start()

    return jsonify({'success': True, 'calories_burned': calories_burned})


@app.route('/api/add-meal', methods=['POST'])
def add_meal():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    try:
        cursor.execute('''
            SELECT planid FROM dietplan 
            WHERE userid = %s AND startdate <= %s AND (enddate >= %s OR enddate IS NULL)
            LIMIT 1
        ''', (user_id, data['date'], data['date']))
        plan = cursor.fetchone()

        if not plan:
            cursor.execute('''
                INSERT INTO dietplan (userid, planname, description, startdate, enddate)
                VALUES (%s, 'My Diet Plan', 'Personalized plan', %s, DATE_ADD(%s, INTERVAL 3 MONTH))
            ''', (user_id, data['date'], data['date']))
            mysql.connection.commit()
            cursor.execute('SELECT LAST_INSERT_ID() as planid')
            plan = cursor.fetchone()

        cursor.execute('''
            INSERT INTO meal (planid, mealtype, mealdate, totalcalories)
            VALUES (%s, %s, %s, %s)
        ''', (plan['planid'], data['meal_type'].capitalize(), data['date'], data['calories']))
        meal_id = cursor.lastrowid

        for food in data['foods']:
            cursor.execute('SELECT foodid FROM fooditem WHERE foodname = %s', (food['name'],))
            food_item = cursor.fetchone()

            if not food_item:
                cursor.execute('INSERT INTO fooditem (foodname, calories) VALUES (%s, %s)',
                               (food['name'], food['calories']))
                food_id = cursor.lastrowid
            else:
                food_id = food_item['foodid']

            cursor.execute('INSERT INTO mealfood (mealid, foodid, quantity) VALUES (%s, %s, %s)',
                           (meal_id, food_id, food.get('quantity', 1)))

        mysql.connection.commit()

        cursor.execute('SELECT email, name FROM user WHERE userid = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user and user['email'] and '@example.com' not in user['email']:
            thread = threading.Thread(target=send_meal_notification_email,
                                      args=(user['email'], user['name'], {
                                          'meal_type': data['meal_type'],
                                          'food_name': data['foods'][0]['name'],
                                          'calories': data['calories'],
                                          'date': data['date']
                                      }))
            thread.daemon = True
            thread.start()

        return jsonify({'success': True, 'meal_id': meal_id})

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/view-foods', methods=['GET'])
def view_foods():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT foodid, foodname, calories FROM fooditem LIMIT 20')
    foods = cursor.fetchall()
    cursor.close()

    return jsonify({'foods': [dict(f) for f in foods]})


@app.route('/api/delete-meal/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    """Delete a specific meal from the calendar"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    try:
        # Verify the meal belongs to the user
        cursor.execute('''
            SELECT m.mealid FROM meal m
            JOIN dietplan dp ON m.planid = dp.planid
            WHERE m.mealid = %s AND dp.userid = %s
        ''', (meal_id, user_id))

        meal = cursor.fetchone()
        if not meal:
            cursor.close()
            return jsonify({'error': 'Meal not found or unauthorized'}), 404

        # Delete the meal (cascade will delete from mealfood automatically)
        cursor.execute('DELETE FROM meal WHERE mealid = %s', (meal_id,))
        mysql.connection.commit()

        cursor.close()
        return jsonify({
            'success': True,
            'message': 'Meal deleted successfully!'
        })

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-meals-by-date/<date>', methods=['DELETE'])
def delete_meals_by_date(date):
    """Delete all meals for a specific date"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    try:
        # Delete all meals for the date
        cursor.execute('''
            DELETE FROM meal WHERE planid IN (
                SELECT planid FROM dietplan WHERE userid = %s
            ) AND mealdate = %s
        ''', (user_id, date))

        mysql.connection.commit()
        deleted_count = cursor.rowcount
        cursor.close()

        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} meal(s) for {date}'
        })

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-all-meals', methods=['DELETE'])
def delete_all_meals():
    """Delete all meals for the current user"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    try:
        cursor.execute('''
            DELETE FROM meal WHERE planid IN (
                SELECT planid FROM dietplan WHERE userid = %s
            )
        ''', (user_id,))

        mysql.connection.commit()
        deleted_count = cursor.rowcount
        cursor.close()

        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} meal(s)'
        })

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500


# Add these routes to your app.py file

@app.route('/api/delete-activity/<int:activity_log_id>', methods=['DELETE'])
def delete_activity(activity_log_id):
    """Delete a specific user activity by its user_activities.id"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    try:
        # Verify ownership
        cursor.execute('SELECT id FROM user_activities WHERE id = %s AND user_id = %s',
                       (activity_log_id, user_id))

        if not cursor.fetchone():
            cursor.close()
            return jsonify({'error': 'Activity not found or unauthorized'}), 404

        cursor.execute('DELETE FROM user_activities WHERE id = %s', (activity_log_id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'success': True, 'message': 'Activity deleted successfully!'})

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-activities-by-date/<date>', methods=['DELETE'])
def delete_activities_by_date(date):
    """Delete all user activities for a specific date"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    try:
        cursor.execute('DELETE FROM user_activities WHERE user_id = %s AND date = %s', (user_id, date))
        mysql.connection.commit()
        deleted_count = cursor.rowcount
        cursor.close()

        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} activity/activities for {date}'
        })

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500
@app.route('/api/delete-all-activities', methods=['DELETE'])
def delete_all_activities():
    """Delete all activities for the current user"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    try:
        cursor.execute('DELETE FROM user_activities WHERE user_id = %s', (user_id,))
        mysql.connection.commit()
        deleted_count = cursor.rowcount
        cursor.close()

        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} activity/activities'
        })

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/activity-recommendations', methods=['GET'])
def get_activity_recommendations():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT goal FROM user WHERE userid = %s', (session['user_id'],))
    user = cursor.fetchone()
    user_goal = user['goal'] if user else 'maintain'

    if user_goal == 'lose':
        cursor.execute('SELECT * FROM activities WHERE goal_type IN ("lose", "all") ORDER BY calories_per_minute DESC')
        weekly_target = 150
    elif user_goal == 'gain':
        cursor.execute('SELECT * FROM activities WHERE goal_type IN ("gain", "all") ORDER BY calories_per_minute ASC')
        weekly_target = 60
    else:
        cursor.execute('SELECT * FROM activities WHERE goal_type IN ("maintain", "all")')
        weekly_target = 90

    recommendations = cursor.fetchall()

    cursor.execute('''
        SELECT SUM(duration_minutes) as total_minutes, SUM(calories_burned) as total_calories
        FROM user_activities
        WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    ''', (session['user_id'],))
    weekly = cursor.fetchone()
    cursor.close()

    return jsonify({
        'goal': user_goal,
        'recommendations': [dict(r) for r in recommendations],
        'weekly_target_minutes': weekly_target,
        'weekly_summary': {
            'total_minutes': weekly['total_minutes'] or 0,
            'total_calories': int(weekly['total_calories'] or 0),
            'remaining_minutes': max(0, weekly_target - (weekly['total_minutes'] or 0))
        },
        'message': "Stay active and healthy!"
    })


# ============= RUN THE APP =============
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('css', exist_ok=True)
    os.makedirs('js', exist_ok=True)

    with app.app_context():
        try:
            init_activities_table()
            print("✅ Database initialized")
        except Exception as e:
            print(f"⚠️ DB Error: {e}")
            print("Make sure MySQL is running and database exists")

    print("🚀 Server running at http://localhost:5000")
    app.run(debug=True, port=5000)