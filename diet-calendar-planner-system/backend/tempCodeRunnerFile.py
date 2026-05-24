from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_cors import CORS
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import hashlib
import os
import threading
import random
from datetime import datetime, timedelta
from notification_service import NotificationService

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
# To enable email notifications:
# 1. Create a Gmail account or use existing one
# 2. Enable 2-Step Verification: https://myaccount.google.com/security
# 3. Generate App Password: https://myaccount.google.com/apppasswords
# 4. Replace the credentials below with your Gmail and App Password
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')  # Set via environment or directly
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')  # Set via environment or directly
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')  # Same as MAIL_USERNAME

mysql = MySQL(app)
mail = Mail(app)
CORS(app, supports_credentials=True)
notification_service = NotificationService()

# Global error handler to always return JSON
@app.errorhandler(Exception)
def handle_error(error):
    """Catch all errors and return JSON instead of HTML"""
    print(f"❌ Unhandled error: {error}")
    return jsonify({
        'success': False,
        'message': str(error),
        'error': 'Internal server error'
    }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found',
        'error': '404 Not Found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'message': 'Method not allowed',
        'error': '405 Method Not Allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'error': '500 Internal Server Error'
    }), 500

# Ensure notifications table exists in MySQL
try:
    cur = mysql.connection.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            type ENUM('action','warning','motivational') DEFAULT 'action',
            is_read TINYINT(1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(userid) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    ''')
    mysql.connection.commit()
    cur.close()
except Exception as _:
    # If DB schema is managed externally, ignore errors here
    pass


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
    """Send email notification when a meal is logged by the user"""
    try:
        if not app.config['MAIL_USERNAME']:
            print("⚠️ Mail not configured - skipping email")
            return False

        # Create professional HTML email
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ background: white; padding: 30px; }}
                .meal-info {{ background: #f9f9f9; border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-item {{ text-align: center; }}
                .stat-label {{ color: #666; font-size: 12px; text-transform: uppercase; }}
                .stat-value {{ color: #667eea; font-size: 24px; font-weight: bold; }}
                .footer {{ background: #f0f0f0; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .emoji {{ font-size: 24px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="emoji">🍽️</div>
                    <h1 style="margin: 10px 0;">Meal Successfully Logged!</h1>
                    <p style="margin: 0; opacity: 0.9;">Keep up with your diet plan</p>
                </div>
                <div class="content">
                    <h2 style="color: #333; margin-top: 0;">Hey {user_name}! 👋</h2>
                    <p style="color: #666; line-height: 1.6;">Your meal has been successfully recorded in your Diet Calendar Planner.</p>
                    
                    <div class="meal-info">
                        <strong style="color: #667eea; font-size: 16px;">{meal_data.get('meal_type', 'Meal').upper()}</strong>
                        <p style="margin: 10px 0 0 0; color: #333;">
                            <strong>Food:</strong> {meal_data.get('food_name', 'N/A')}
                        </p>
                    </div>

                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-label">Calories</div>
                            <div class="stat-value">{meal_data.get('calories', 0)}</div>
                            <div style="color: #999; font-size: 12px;">kcal</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Date</div>
                            <div class="stat-value">📅</div>
                            <div style="color: #999; font-size: 12px;">{meal_data.get('date', 'Today')}</div>
                        </div>
                    </div>

                    <p style="background: #e3f2fd; padding: 15px; border-radius: 5px; color: #1565c0; font-size: 14px;">
                        <strong>💡 Tip:</strong> Remember to log all meals to get accurate daily calorie tracking and personalized recommendations!
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from Diet Calendar Planner System</p>
                    <p style="margin: 5px 0;">Stay healthy, stay consistent! 💪</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg = Message("🍽️ Meal Logged - Diet Planner", recipients=[user_email], html=html)
        mail.send(msg)
        print(f"✅ Meal notification email sent to {user_email}")
        return True
    except Exception as e:
        print(f"❌ Email error sending meal notification: {e}")
        return False


def send_activity_notification_email(user_email, user_name, activity_data):
    """Send email notification when an activity/exercise is logged by the user"""
    try:
        if not app.config['MAIL_USERNAME']:
            print("⚠️ Mail not configured - skipping email")
            return False

        emoji = activity_data.get('icon', '🏃')
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ background: white; padding: 30px; }}
                .activity-info {{ background: #fff3e0; border-left: 4px solid #f5576c; padding: 15px; margin: 15px 0; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-item {{ text-align: center; }}
                .stat-label {{ color: #666; font-size: 12px; text-transform: uppercase; }}
                .stat-value {{ color: #f5576c; font-size: 24px; font-weight: bold; }}
                .footer {{ background: #f0f0f0; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .emoji {{ font-size: 24px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="emoji">{emoji}</div>
                    <h1 style="margin: 10px 0;">Great Job! Activity Logged! 🎉</h1>
                    <p style="margin: 0; opacity: 0.9;">You're staying active and on track</p>
                </div>
                <div class="content">
                    <h2 style="color: #333; margin-top: 0;">Awesome work, {user_name}! 💪</h2>
                    <p style="color: #666; line-height: 1.6;">Your exercise has been successfully recorded in your fitness tracker.</p>
                    
                    <div class="activity-info">
                        <strong style="color: #f5576c; font-size: 16px;">{emoji} {activity_data.get('name', 'Activity').upper()}</strong>
                        <p style="margin: 10px 0 0 0; color: #333;">
                            <strong>Intensity:</strong> {activity_data.get('intensity', 'N/A').capitalize()}
                        </p>
                    </div>

                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-label">Duration</div>
                            <div class="stat-value">{activity_data.get('duration', 0)}</div>
                            <div style="color: #999; font-size: 12px;">mins</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Calories Burned</div>
                            <div class="stat-value">{activity_data.get('calories_burned', 0)}</div>
                            <div style="color: #999; font-size: 12px;">kcal</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Date</div>
                            <div class="stat-value">📅</div>
                            <div style="color: #999; font-size: 12px;">{activity_data.get('date', 'Today')}</div>
                        </div>
                    </div>

                    <p style="background: #f3e5f5; padding: 15px; border-radius: 5px; color: #6a1b9a; font-size: 14px;">
                        <strong>🔥 Motivational Tip:</strong> You're burning calories and building a healthier you! Keep up this amazing momentum!
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from Diet Calendar Planner System</p>
                    <p style="margin: 5px 0;">Keep moving, keep achieving! 🚀</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg = Message(f"🏃 Activity Logged - Diet Planner", recipients=[user_email], html=html)
        mail.send(msg)
        print(f"✅ Activity notification email sent to {user_email}")
        return True
    except Exception as e:
        print(f"❌ Email error sending activity notification: {e}")
        return False


def send_daily_reminder_email(user_email, user_name, scheduled_items):
    """Send daily reminder email with scheduled meals and activities for the user"""
    try:
        if not app.config['MAIL_USERNAME']:
            print("⚠️ Mail not configured - skipping email")
            return False

        # Create HTML content for scheduled items
        items_html = ""
        for item in scheduled_items:
            if item['type'] == 'meal':
                items_html += f"""
                <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 12px; margin: 10px 0; border-radius: 3px;">
                    <strong style="color: #2e7d32;">🍽️ {item['meal_type'].upper()}</strong>
                    <p style="margin: 5px 0; color: #333;">Food: {item.get('food_name', 'TBD')}</p>
                    <p style="margin: 5px 0; color: #666; font-size: 12px;">Calories: {item.get('calories', 'N/A')} kcal</p>
                </div>
                """
            else:  # activity
                items_html += f"""
                <div style="background: #fce4ec; border-left: 4px solid #e91e63; padding: 12px; margin: 10px 0; border-radius: 3px;">
                    <strong style="color: #c2185b;">{item.get('icon', '🏃')} {item['name'].upper()}</strong>
                    <p style="margin: 5px 0; color: #333;">Duration: {item.get('duration', 'N/A')} minutes</p>
                    <p style="margin: 5px 0; color: #666; font-size: 12px;">Planned Calories: {item.get('calories', 'N/A')} kcal</p>
                </div>
                """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ background: white; padding: 30px; }}
                .footer {{ background: #f0f0f0; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 10px 0;">📆 Today's Schedule</h1>
                    <p style="margin: 0; opacity: 0.9;">Your personalized meal and activity plan</p>
                </div>
                <div class="content">
                    <h2 style="color: #333; margin-top: 0;">Good Morning, {user_name}! 🌟</h2>
                    <p style="color: #666; line-height: 1.6;">Here's what you have planned for today. Stay focused and achieve your health goals!</p>
                    
                    <h3 style="color: #667eea; margin-top: 25px; margin-bottom: 10px;">📋 Today's Plan:</h3>
                    {items_html if items_html else '<p style="color: #999;">No meals or activities scheduled for today. Add your plan now!</p>'}

                    <p style="background: #e3f2fd; padding: 15px; border-radius: 5px; color: #1565c0; font-size: 14px; margin-top: 20px;">
                        <strong>💡 Reminder:</strong> Make sure to log your meals and activities as you complete them throughout the day for accurate tracking!
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from Diet Calendar Planner System</p>
                    <p style="margin: 5px 0;">Have a productive and healthy day! 🏃‍♀️🥗</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg = Message("📆 Your Daily Schedule - Diet Planner", recipients=[user_email], html=html)
        mail.send(msg)
        print(f"✅ Daily reminder email sent to {user_email}")
        return True
    except Exception as e:
        print(f"❌ Email error sending daily reminder: {e}")
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
    """Health check endpoint"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        return jsonify({
            'success': True,
            'message': 'Backend is working and MySQL is connected',
            'status': 'healthy'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'MySQL connection error: {str(e)}',
            'status': 'unhealthy'
        }), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'success': False, 'message': 'Invalid request format'})
            
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return jsonify({'success': False, 'message': 'Email and password required'})

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            try:
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
            except Exception as db_error:
                print(f"Database error during login: {db_error}")
                return jsonify({'success': False, 'message': 'Database connection error. Make sure MySQL is running'}), 500
        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({'success': False, 'message': f'Login error: {str(e)}'}), 500

    return render_template('login.html')


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request format'})
        
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
        
        try:
            cursor = mysql.connection.cursor()

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
            cursor.close()

            return jsonify({'success': True, 'message': 'Registration successful!'})
        except Exception as db_error:
            mysql.connection.rollback()
            print(f"Registration database error: {db_error}")
            if 'Duplicate' in str(db_error):
                return jsonify({'success': False, 'message': 'Email already exists'}), 400
            return jsonify({'success': False, 'message': 'Database error: ' + str(db_error)}), 500
        finally:
            try:
                cursor.close()
            except:
                pass
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'message': f'Registration error: {str(e)}'}), 500


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
                   SELECT u.weight,
                          u.height,
                          u.age,
                          u.gender,
                          u.goal,
                          COALESCE(p.weight, u.weight) as current_weight
                   FROM user u
                            LEFT JOIN progresslog p ON u.userid = p.user_id
                   WHERE u.userid = %s
                   ORDER BY p.date DESC LIMIT 1
                   ''', (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        return jsonify({'error': 'User not found'}), 404

    current_weight = float(user['current_weight'] or user['weight'] or 70)
    goal = user['goal'] or 'maintain'

    # Auto-determine goal based on target weight
    auto_goal = goal
    if target_weight > 0:
        if target_weight < current_weight:
            auto_goal = 'lose'
        elif target_weight > current_weight:
            auto_goal = 'gain'
        else:
            auto_goal = 'maintain'

    calorie_target = MealPlanner.calculate_calorie_target(
        weight=current_weight,
        height=float(user['height'] or 170),
        age=int(user['age'] or 30),
        gender=user['gender'] or 'Male',
        goal=auto_goal
    )

    cursor.close()

    # Generate meal plan with specific date range
    meal_plan = {}
    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')

        # Use direct generation from database
        daily_meals = generate_daily_meals_from_database_fixed(auto_goal, calorie_target)

        if daily_meals:
            # Calculate total calories for the day
            total_calories = sum([
                daily_meals['breakfast']['calories'],
                daily_meals['lunch']['calories'],
                daily_meals['dinner']['calories'],
                daily_meals['snack']['calories']
            ])
            daily_meals['total_calories'] = total_calories
            daily_meals['target_calories'] = calorie_target
            meal_plan[date] = daily_meals

    if not meal_plan:
        return jsonify({'error': 'No food items found in database'}), 404

    return jsonify({
        'success': True,
        'goal': auto_goal,
        'current_weight': current_weight,
        'target_weight': target_weight,
        'calorie_target': calorie_target,
        'meal_plan': meal_plan,
        'recommendations': get_goal_recommendations(auto_goal),
        'nutrition_tips': {
            'breakfast': MealPlanner.get_nutrition_tips(auto_goal, 'breakfast'),
            'lunch': MealPlanner.get_nutrition_tips(auto_goal, 'lunch'),
            'dinner': MealPlanner.get_nutrition_tips(auto_goal, 'dinner'),
            'snack': MealPlanner.get_nutrition_tips(auto_goal, 'snack')
        }
    })

def generate_daily_meals_from_database_fixed(goal, calorie_target):
    """Generate a single day's meals from database - Fixed version"""
    cursor = mysql.connection.cursor()

    # Get all foods from database
    cursor.execute('SELECT foodid, foodname, calories, protein, carbs, fats FROM fooditem')
    all_foods = cursor.fetchall()
    cursor.close()

    if not all_foods:
        return None

    # Categorize foods based on goal
    if goal == 'lose':
        breakfast_foods = [f for f in all_foods if f['calories'] <= 300] or all_foods[:10]
        lunch_foods = [f for f in all_foods if 200 <= f['calories'] <= 450] or all_foods[5:15]
        dinner_foods = [f for f in all_foods if 250 <= f['calories'] <= 500] or all_foods[10:20]
        snack_foods = [f for f in all_foods if f['calories'] <= 150] or all_foods[:8]
    elif goal == 'gain':
        breakfast_foods = [f for f in all_foods if f['calories'] >= 400] or all_foods[-10:]
        lunch_foods = [f for f in all_foods if f['calories'] >= 500] or all_foods[-15:-5]
        dinner_foods = [f for f in all_foods if f['calories'] >= 600] or all_foods[-20:-10]
        snack_foods = [f for f in all_foods if f['calories'] >= 200] or all_foods[-8:]
    else:  # maintain
        breakfast_foods = [f for f in all_foods if 200 <= f['calories'] <= 400] or all_foods[5:15]
        lunch_foods = [f for f in all_foods if 350 <= f['calories'] <= 550] or all_foods[10:20]
        dinner_foods = [f for f in all_foods if 400 <= f['calories'] <= 650] or all_foods[15:25]
        snack_foods = [f for f in all_foods if 100 <= f['calories'] <= 250] or all_foods[3:12]

    # Select meals (choose once per meal type)
    breakfast = random.choice(breakfast_foods) if breakfast_foods else all_foods[0]
    lunch = random.choice(lunch_foods) if lunch_foods else all_foods[1]
    dinner = random.choice(dinner_foods) if dinner_foods else all_foods[2]
    snack = random.choice(snack_foods) if snack_foods else all_foods[3]

    return {
        'breakfast': {
            'name': breakfast['foodname'],
            'calories': float(breakfast['calories']),
            'protein': float(breakfast.get('protein', 0) or 0),
            'carbs': float(breakfast.get('carbs', 0) or 0),
            'fats': float(breakfast.get('fats', 0) or 0),
            'foodid': breakfast['foodid']
        },
        'lunch': {
            'name': lunch['foodname'],
            'calories': float(lunch['calories']),
            'protein': float(lunch.get('protein', 0) or 0),
            'carbs': float(lunch.get('carbs', 0) or 0),
            'fats': float(lunch.get('fats', 0) or 0),
            'foodid': lunch['foodid']
        },
        'dinner': {
            'name': dinner['foodname'],
            'calories': float(dinner['calories']),
            'protein': float(dinner.get('protein', 0) or 0),
            'carbs': float(dinner.get('carbs', 0) or 0),
            'fats': float(dinner.get('fats', 0) or 0),
            'foodid': dinner['foodid']
        },
        'snack': {
            'name': snack['foodname'],
            'calories': float(snack['calories']),
            'protein': float(snack.get('protein', 0) or 0),
            'carbs': float(snack.get('carbs', 0) or 0),
            'fats': float(snack.get('fats', 0) or 0),
            'foodid': snack['foodid']
        }
    }


# Replace the static method in MealPlanner class
MealPlanner.generate_daily_meals_from_database = staticmethod(generate_daily_meals_from_database_fixed)


@app.route('/api/log-activity', methods=['POST'])
def log_activity():
    """Log a user activity from the activities page"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    user_id = session['user_id']

    # Get activity details
    activity_id = data.get('activity_id')
    duration_minutes = data.get('duration_minutes')
    notes = data.get('notes', '')

    if not activity_id or not duration_minutes:
        return jsonify({'error': 'Activity ID and duration are required'}), 400

    cursor = mysql.connection.cursor()

    try:
        # Get activity details
        cursor.execute('''
                       SELECT id, name, calories_per_minute, intensity, icon
                       FROM activities
                       WHERE id = %s
                       ''', (activity_id,))

        activity = cursor.fetchone()

        if not activity:
            cursor.close()
            return jsonify({'error': 'Activity not found'}), 404

        # Calculate calories burned
        calories_burned = int(float(activity['calories_per_minute']) * duration_minutes)

        # Use current date if not provided
        log_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Insert into user_activities
        cursor.execute('''
                       INSERT INTO user_activities (user_id, activity_id, duration_minutes, date, calories_burned, notes)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ''', (user_id, activity_id, duration_minutes, log_date, calories_burned, notes))

        mysql.connection.commit()

        # Send email notification if configured
        cursor.execute('SELECT email, name FROM user WHERE userid = %s', (user_id,))
        user = cursor.fetchone()

        if user and user['email'] and '@example.com' not in user['email'] and app.config['MAIL_USERNAME']:
            try:
                thread = threading.Thread(target=send_activity_notification_email,
                                          args=(user['email'], user['name'], {
                                              'name': activity['name'],
                                              'duration': duration_minutes,
                                              'calories_burned': calories_burned,
                                              'date': log_date,
                                              'intensity': activity['intensity'],
                                              'icon': activity['icon'] or '🏃'
                                          }))
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"Email notification error: {e}")

        # Create in-app notification
        notification_service.create_action_notification(cursor, user_id, 'activity', {
            'activity_name': activity['name'],
            'duration': duration_minutes,
            'calories_burned': calories_burned,
            'icon': activity['icon'] or '🏃'
        })
        mysql.connection.commit()

        cursor.close()

        return jsonify({
            'success': True,
            'calories_burned': calories_burned,
            'message': f'Logged {duration_minutes} minutes of {activity["name"]}'
        })

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        print(f"Error logging activity: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-generated-meals', methods=['POST'])
def save_generated_meals():
    """Save generated meal plan to database with proper calories"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    meal_plan = request.json.get('meal_plan', {})

    print(f"Received meal_plan data: {meal_plan}")  # Debug print

    cursor = mysql.connection.cursor()
    saved_count = 0
    errors = []

    try:
        for date_str, meals in meal_plan.items():
            # Skip if not a valid date string
            if not isinstance(meals, dict) or date_str == 'total_calories' or date_str == 'target_calories':
                continue

            print(f"Processing meals for date: {date_str}")

            # Get or create diet plan for this date
            cursor.execute('''
                           SELECT planid
                           FROM dietplan
                           WHERE userid = %s
                             AND startdate <= %s
                             AND (enddate >= %s OR enddate IS NULL) LIMIT 1
                           ''', (user_id, date_str, date_str))
            plan = cursor.fetchone()

            if not plan:
                cursor.execute('''
                               INSERT INTO dietplan (userid, planname, description, startdate, enddate)
                               VALUES (%s, 'AI Generated Plan', 'Auto-generated meal plan from AI', %s,
                                       DATE_ADD(%s, INTERVAL 1 MONTH))
                               ''', (user_id, date_str, date_str))
                mysql.connection.commit()
                plan = {'planid': cursor.lastrowid}
                print(f"Created new diet plan with ID: {plan['planid']}")

            # Save each meal type
            meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
            for meal_type in meal_types:
                if meal_type not in meals:
                    continue

                meal_data = meals[meal_type]

                # Skip if meal_data is not a dictionary
                if not isinstance(meal_data, dict):
                    print(f"Skipping {meal_type}: not a dictionary")
                    continue

                meal_name = meal_data.get('name', 'Unknown')
                meal_calories = float(meal_data.get('calories', 0))

                if meal_calories == 0:
                    print(f"Skipping {meal_type}: 0 calories")
                    continue

                print(f"Saving {meal_type}: {meal_name} - {meal_calories} calories")

                # Insert meal
                cursor.execute('''
                               INSERT INTO meal (planid, mealtype, mealdate, totalcalories)
                               VALUES (%s, %s, %s, %s)
                               ''', (plan['planid'], meal_type.capitalize(), date_str, meal_calories))
                meal_id = cursor.lastrowid

                # Check if food exists in database
                cursor.execute('SELECT foodid, calories FROM fooditem WHERE foodname = %s', (meal_name,))
                food = cursor.fetchone()

                if not food:
                    # Insert the food if it doesn't exist
                    cursor.execute('''
                                   INSERT INTO fooditem (foodname, calories, protein, carbs, fats)
                                   VALUES (%s, %s, %s, %s, %s)
                                   ''', (
                                       meal_name,
                                       meal_calories,
                                       meal_data.get('protein', 0),
                                       meal_data.get('carbs', 0),
                                       meal_data.get('fats', 0)
                                   ))
                    food_id = cursor.lastrowid
                    print(f"Created new food item: {meal_name}")
                else:
                    food_id = food['foodid']

                # Create relationship
                cursor.execute('''
                               INSERT INTO mealfood (mealid, foodid, quantity, servingsize)
                               VALUES (%s, %s, 1, '1 serving')
                               ''', (meal_id, food_id))

                saved_count += 1
                print(f"Successfully saved {meal_type}: {meal_name}")

        mysql.connection.commit()

        # Verify the meals were saved
        cursor.execute('''
                       SELECT COUNT(*) as count
                       FROM meal m
                           JOIN dietplan dp
                       ON m.planid = dp.planid
                       WHERE dp.userid = %s
                       ''', (user_id,))
        total_meals = cursor.fetchone()
        print(f"Total meals in database after save: {total_meals['count'] if total_meals else 0}")

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
        import traceback
        traceback.print_exc()
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

    # Get meals with proper JOIN
    cursor.execute('''
                   SELECT m.mealid,
                          m.mealtype,
                          m.mealdate,
                          m.totalcalories                                  as calories,
                          GROUP_CONCAT(DISTINCT f.foodname SEPARATOR ', ') as food_names
                   FROM meal m
                            JOIN dietplan dp ON m.planid = dp.planid
                            LEFT JOIN mealfood mf ON m.mealid = mf.mealid
                            LEFT JOIN fooditem f ON mf.foodid = f.foodid
                   WHERE dp.userid = %s
                     AND m.mealdate BETWEEN %s AND %s
                   GROUP BY m.mealid, m.mealtype, m.mealdate, m.totalcalories
                   ''', (user_id, start_date, end_date))

    for meal in cursor.fetchall():
        event_title = f"🍽️ {meal['mealtype']}"
        if meal['food_names'] and meal['food_names'] != meal['mealtype']:
            # Only show first part if it's too long
            food_preview = meal['food_names'][:20] + ('...' if len(meal['food_names']) > 20 else '')
            event_title = f"🍽️ {meal['mealtype']}: {food_preview}"

        events.append({
            'id': f"meal_{meal['mealid']}",
            'title': event_title,
            'start': str(meal['mealdate']),
            'allDay': True,
            'type': 'meal',
            'calories': float(meal['calories'] or 0),
            'color': '#48bb78',
            'extendedProps': {
                'mealtype': meal['mealtype'],
                'calories': float(meal['calories'] or 0),
                'food_names': meal['food_names'] or ''
            }
        })

    # Get activities
    cursor.execute('''
                   SELECT ua.id, a.name, a.icon, ua.date, ua.duration_minutes, ua.calories_burned
                   FROM user_activities ua
                            JOIN activities a ON ua.activity_id = a.id
                   WHERE ua.user_id = %s
                     AND ua.date BETWEEN %s AND %s
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
    print(f"Generated {len(events)} calendar events")  # Debug
    return jsonify(events)


@app.route('/api/daily-summary/<date>', methods=['GET'])
def get_daily_summary(date):
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # Get meals with proper grouping
    cursor.execute('''
                   SELECT m.mealid,
                          m.mealtype,
                          m.totalcalories,
                          GROUP_CONCAT(DISTINCT f.foodname SEPARATOR ', ') as food_names
                   FROM meal m
                            JOIN dietplan dp ON m.planid = dp.planid
                            LEFT JOIN mealfood mf ON m.mealid = mf.mealid
                            LEFT JOIN fooditem f ON mf.foodid = f.foodid
                   WHERE dp.userid = %s
                     AND m.mealdate = %s
                   GROUP BY m.mealid, m.mealtype, m.totalcalories
                   ORDER BY CASE m.mealtype
                                WHEN 'Breakfast' THEN 1
                                WHEN 'Lunch' THEN 2
                                WHEN 'Dinner' THEN 3
                                WHEN 'Snack' THEN 4
                                ELSE 5
                                END
                   ''', (user_id, date))
    meals = cursor.fetchall()

    print(f"Found {len(meals)} meals for date {date}")

    # Get activities
    cursor.execute('''
                   SELECT ua.id, a.name, ua.duration_minutes, ua.calories_burned
                   FROM user_activities ua
                            JOIN activities a ON ua.activity_id = a.id
                   WHERE ua.user_id = %s
                     AND ua.date = %s
                   ''', (user_id, date))
    activities = cursor.fetchall()

    cursor.close()

    # Process activities
    activities_list = []
    for act in activities:
        activities_list.append({
            'id': act['id'],
            'name': act['name'],
            'duration_minutes': act['duration_minutes'],
            'calories_burned': float(act['calories_burned'] or 0)
        })

    # Process meals
    meals_list = []
    for meal in meals:
        meals_list.append({
            'mealid': meal['mealid'],
            'mealtype': meal['mealtype'],
            'totalcalories': float(meal['totalcalories'] or 0),
            'food_names': meal['food_names'] or meal['mealtype']
        })

    total_meal_calories = sum(float(m.get('totalcalories', 0) or 0) for m in meals)
    total_activity_calories = sum(float(a['calories_burned'] or 0) for a in activities)

    return jsonify({
        'date': date,
        'meals': meals_list,
        'activities': activities_list,
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
        
        # Create in-app notification
        notification_service.create_action_notification(cursor, user_id, 'meal', {
            'meal_type': data['meal_type'],
            'food_name': data['foods'][0]['name'] if data['foods'] else 'Food',
            'calories': data['calories']
        })
        mysql.connection.commit()
        
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
        weekly_target_calories = 1200
        recommendation_reason = "💪 Increase your activity to achieve weight loss goals!"
    elif user_goal == 'gain':
        cursor.execute('SELECT * FROM activities WHERE goal_type IN ("gain", "all") ORDER BY calories_per_minute ASC')
        weekly_target = 60
        weekly_target_calories = 500
        recommendation_reason = "🏋️ Moderate activity to support muscle gain!"
    else:
        cursor.execute('SELECT * FROM activities WHERE goal_type IN ("maintain", "all")')
        weekly_target = 90
        weekly_target_calories = 750
        recommendation_reason = "⚖️ Stay balanced with consistent weekly activity!"

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
        'recommendation_reason': recommendation_reason,
        'recommendations': [dict(r) for r in recommendations],
        'weekly_target_minutes': weekly_target,
        'weekly_target_calories': weekly_target_calories,
        'weekly_summary': {
            'total_minutes': weekly['total_minutes'] or 0,
            'total_calories': int(weekly['total_calories'] or 0),
            'remaining_minutes': max(0, weekly_target - (weekly['total_minutes'] or 0))
        },
        'message': "Stay active and healthy!"
    })


@app.route('/api/trigger-activity-email', methods=['GET'])
def trigger_activity_email():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT email, name, goal FROM user WHERE userid = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    # Fetches the active profile mode ('MAINTAIN', 'LOSE', etc.)
    user_goal = user['goal'].upper() if user['goal'] else 'MAINTAIN'

    activities = {
        'lose': '30-minute HIIT Cardio Circuit to maximize your fat burn session 🏃',
        'maintain': '45-minute Steady Pace Cycling routine to balance your calorie intake 🚴',
        'gain': 'Heavy Weightlifting Focus Routine (Compound Squats, Bench, and Deadlifts) 🏋️'
    }

    selected_activity = activities.get(user_goal.lower(), activities['maintain'])

    # Send email notification
    email_status = "Email skipped"
    if user['email'] and '@example.com' not in user['email'] and app.config['MAIL_USERNAME']:
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; }}
                    .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .content {{ background: white; padding: 30px; }}
                    .activity-box {{ background: #fff3e0; border-left: 4px solid #f5576c; padding: 15px; margin: 15px 0; }}
                    .footer {{ background: #f0f0f0; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 10px 0;">🏃 Your Daily Activity Goal</h1>
                        <p style="margin: 0; opacity: 0.9;">Based on your meal plan for today</p>
                    </div>
                    <div class="content">
                        <h2 style="color: #333; margin-top: 0;">Hey {user['name']}! 💪</h2>
                        <p style="color: #666; line-height: 1.6;">Based on your food selection today, here's your recommended activity:</p>
                        
                        <div class="activity-box">
                            <strong style="color: #f5576c; font-size: 16px;">Today's Activity Target:</strong>
                            <p style="margin: 10px 0 0 0; color: #333; font-size: 15px;">
                                {selected_activity}
                            </p>
                        </div>

                        <p style="background: #f3e5f5; padding: 15px; border-radius: 5px; color: #6a1b9a; font-size: 14px;">
                            <strong>💡 Pro Tip:</strong> This activity recommendation is tailored to match your daily meal intake and fitness goal. Stay active and consistent!
                        </p>
                    </div>
                    <div class="footer">
                        <p>Automated notification from Diet Calendar Planner System</p>
                        <p style="margin: 5px 0;">Keep moving, keep achieving! 🚀</p>
                    </div>
                </div>
            </body>
            </html>
            """
            msg = Message("🏃 Your Daily Activity Goal", recipients=[user['email']], html=html_content)
            mail.send(msg)
            email_status = "Email sent successfully!"
        except Exception as e:
            email_status = f"Email failed: {str(e)}"
    elif not app.config['MAIL_USERNAME']:
        email_status = "Email service not configured"

    return jsonify({
        'success': True,
        'goal': user_goal,
        'activity': selected_activity,
        'message': f"📧 {email_status}"
    })


@app.route('/api/send-daily-reminder', methods=['POST'])
def send_daily_reminder():
    """Send daily reminder email with scheduled meals and activities for today"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    today_date = datetime.now().strftime('%Y-%m-%d')

    cursor = mysql.connection.cursor()

    try:
        # Get user info
        cursor.execute('SELECT email, name, goal FROM user WHERE userid = %s', (user_id,))
        user = cursor.fetchone()

        if not user or not user['email']:
            cursor.close()
            return jsonify({'error': 'User email not found'}), 404

        # Skip example emails
        if '@example.com' in user['email']:
            cursor.close()
            return jsonify({'success': False, 'message': 'Example emails cannot receive notifications'}), 400

        scheduled_items = []

        # Get meals for today
        cursor.execute('''
            SELECT m.mealid, m.mealtype, m.totalcalories,
                   GROUP_CONCAT(DISTINCT f.foodname SEPARATOR ', ') as food_names
            FROM meal m
            JOIN dietplan dp ON m.planid = dp.planid
            LEFT JOIN mealfood mf ON m.mealid = mf.mealid
            LEFT JOIN fooditem f ON mf.foodid = f.foodid
            WHERE dp.userid = %s AND m.mealdate = %s
            GROUP BY m.mealid, m.mealtype, m.totalcalories
            ORDER BY CASE m.mealtype 
                WHEN 'Breakfast' THEN 1
                WHEN 'Lunch' THEN 2
                WHEN 'Dinner' THEN 3
                WHEN 'Snack' THEN 4
                ELSE 5 END
        ''', (user_id, today_date))

        meals = cursor.fetchall()
        for meal in meals:
            scheduled_items.append({
                'type': 'meal',
                'meal_type': meal['mealtype'],
                'food_name': meal['food_names'] or 'Not specified',
                'calories': int(meal['totalcalories'] or 0)
            })

        # Get activities for today
        cursor.execute('''
            SELECT ua.id, a.name, a.icon, ua.duration_minutes, 
                   CAST(ua.duration_minutes * a.calories_per_minute AS INT) as planned_calories
            FROM user_activities ua
            JOIN activities a ON ua.activity_id = a.id
            WHERE ua.user_id = %s AND ua.date = %s
            ORDER BY ua.created_at
        ''', (user_id, today_date))

        activities = cursor.fetchall()
        for activity in activities:
            scheduled_items.append({
                'type': 'activity',
                'name': activity['name'],
                'icon': activity['icon'] or '🏃',
                'duration': activity['duration_minutes'],
                'calories': activity['planned_calories'] or 0
            })

        cursor.close()

        # Send email
        if app.config['MAIL_USERNAME']:
            thread = threading.Thread(target=send_daily_reminder_email,
                                      args=(user['email'], user['name'], scheduled_items))
            thread.daemon = True
            thread.start()
            return jsonify({
                'success': True,
                'message': f'Daily reminder sent to {user["email"]}',
                'items_count': len(scheduled_items)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Email service not configured'
            }), 503

    except Exception as e:
        cursor.close()
        print(f"Error sending daily reminder: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/send-meal-summary', methods=['POST'])
def send_meal_summary():
    """Send a summary email of all meals and activities for a specific date"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    data = request.json
    target_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    cursor = mysql.connection.cursor()

    try:
        # Get user info
        cursor.execute('SELECT email, name, goal FROM user WHERE userid = %s', (user_id,))
        user = cursor.fetchone()

        if not user or not user['email']:
            cursor.close()
            return jsonify({'error': 'User email not found'}), 404

        if '@example.com' in user['email']:
            cursor.close()
            return jsonify({'success': False, 'message': 'Example emails cannot receive notifications'}), 400

        scheduled_items = []

        # Get meals
        cursor.execute('''
            SELECT m.mealtype, m.totalcalories,
                   GROUP_CONCAT(DISTINCT f.foodname SEPARATOR ', ') as food_names
            FROM meal m
            JOIN dietplan dp ON m.planid = dp.planid
            LEFT JOIN mealfood mf ON m.mealid = mf.mealid
            LEFT JOIN fooditem f ON mf.foodid = f.foodid
            WHERE dp.userid = %s AND m.mealdate = %s
            GROUP BY m.mealtype, m.totalcalories
        ''', (user_id, target_date))

        meals = cursor.fetchall()
        for meal in meals:
            scheduled_items.append({
                'type': 'meal',
                'meal_type': meal['mealtype'],
                'food_name': meal['food_names'] or 'Not specified',
                'calories': int(meal['totalcalories'] or 0)
            })

        # Get activities
        cursor.execute('''
            SELECT a.name, a.icon, ua.duration_minutes, ua.calories_burned
            FROM user_activities ua
            JOIN activities a ON ua.activity_id = a.id
            WHERE ua.user_id = %s AND ua.date = %s
        ''', (user_id, target_date))

        activities = cursor.fetchall()
        for activity in activities:
            scheduled_items.append({
                'type': 'activity',
                'name': activity['name'],
                'icon': activity['icon'] or '🏃',
                'duration': activity['duration_minutes'],
                'calories': activity['calories_burned'] or 0
            })

        cursor.close()

        # Send email
        if app.config['MAIL_USERNAME']:
            thread = threading.Thread(target=send_daily_reminder_email,
                                      args=(user['email'], user['name'], scheduled_items))
            thread.daemon = True
            thread.start()
            return jsonify({
                'success': True,
                'message': f'Summary email sent to {user["email"]}',
                'date': target_date
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Email service not configured'
            }), 503

    except Exception as e:
        cursor.close()
        print(f"Error sending meal summary: {e}")
        return jsonify({'error': str(e)}), 500


# ============= NOTIFICATION ENDPOINTS =============

@app.route('/api/get-notifications', methods=['GET'])
def get_notifications():
    """Get all notifications for the current user"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    limit = request.args.get('limit', 50, type=int)
    unread_only = request.args.get('unread_only', False, type=bool)

    cursor = mysql.connection.cursor()
    notifications = notification_service.get_notifications(cursor, user_id, limit, unread_only)
    unread_count = notification_service.get_unread_count(cursor, user_id)
    cursor.close()

    return jsonify({
        'success': True,
        'notifications': notifications,
        'unread_count': unread_count
    })


@app.route('/api/mark-notification-read', methods=['POST'])
def mark_notification_read():
    """Mark a notification as read"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    notification_id = data.get('notification_id')
    user_id = session['user_id']

    if not notification_id:
        return jsonify({'error': 'Notification ID required'}), 400

    cursor = mysql.connection.cursor()
    success = notification_service.mark_notification_read(cursor, notification_id, user_id)
    mysql.connection.commit()
    unread_count = notification_service.get_unread_count(cursor, user_id)
    cursor.close()

    return jsonify({
        'success': success,
        'unread_count': unread_count
    })


@app.route('/api/mark-all-notifications-read', methods=['POST'])
def mark_all_notifications_read():
    """Mark all notifications as read for the current user"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    success = notification_service.mark_all_read(cursor, user_id)
    mysql.connection.commit()
    unread_count = notification_service.get_unread_count(cursor, user_id)
    cursor.close()

    return jsonify({
        'success': success,
        'unread_count': unread_count
    })


@app.route('/api/delete-notification', methods=['POST'])
def delete_notification():
    """Delete a notification"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    notification_id = data.get('notification_id')
    user_id = session['user_id']

    if not notification_id:
        return jsonify({'error': 'Notification ID required'}), 400

    cursor = mysql.connection.cursor()
    success = notification_service.delete_notification(cursor, notification_id, user_id)
    mysql.connection.commit()
    unread_count = notification_service.get_unread_count(cursor, user_id)
    cursor.close()

    return jsonify({
        'success': success,
        'unread_count': unread_count
    })


@app.route('/api/check-notifications', methods=['GET'])
def check_notifications():
    """Check for pending notifications and create new ones based on rules"""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    created_notifications = []

    try:
        # Check calorie warning
        notif_id = notification_service.check_calorie_warning(cursor, user_id)
        if notif_id:
            created_notifications.append(notif_id)

        # Check missing meals
        meal_notifs = notification_service.check_missing_meals(cursor, user_id)
        created_notifications.extend(meal_notifs)

        # Check missing activity
        notif_id = notification_service.check_missing_activity(cursor, user_id)
        if notif_id:
            created_notifications.append(notif_id)

        # Check streak
        notif_id = notification_service.check_streak(cursor, user_id)
        if notif_id:
            created_notifications.append(notif_id)

        mysql.connection.commit()

        # Get updated notifications and unread count
        notifications = notification_service.get_notifications(cursor, user_id, 50)
        unread_count = notification_service.get_unread_count(cursor, user_id)

        cursor.close()

        return jsonify({
            'success': True,
            'created_count': len(created_notifications),
            'notifications': notifications,
            'unread_count': unread_count
        })

    except Exception as e:
        print(f"❌ Error checking notifications: {e}")
        mysql.connection.rollback()
        cursor.close()
        return jsonify({'error': str(e)}), 500


# ============= RUN THE APP =============


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

