from flask import Flask
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dietcalendarplannersys'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def add_foods():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM fooditem")
        count = cursor.fetchone()['count']

        if count == 0:
            foods = [
                # Low calorie foods (for weight loss)
                ('Greek Yogurt (plain)', 100, 17, 6, 0.4),
                ('Apple', 95, 0.5, 25, 0.3),
                ('Broccoli (steamed)', 55, 3.7, 11.2, 0.6),
                ('Chicken Breast (grilled)', 165, 31, 0, 3.6),
                ('Quinoa Salad', 120, 4.4, 21.3, 1.9),
                ('Oatmeal', 158, 5.5, 27, 3.2),
                ('Banana', 105, 1.3, 27, 0.4),
                ('Almonds (10 pieces)', 69, 2.5, 2.5, 6),
                ('Cottage Cheese (1/2 cup)', 110, 12, 4, 5),
                ('Egg White Scramble', 85, 18, 2, 1),
                ('Tuna Salad', 150, 22, 5, 5),
                ('Vegetable Soup', 120, 4, 20, 2),
                ('Brown Rice (1 cup)', 216, 5, 45, 1.8),
                ('Grilled Salmon', 208, 22, 0, 13),
                ('Sweet Potato', 114, 2, 27, 0.1),

                # Medium calorie foods (for maintenance)
                ('Turkey Wrap', 320, 28, 35, 10),
                ('Chicken Bowl', 380, 32, 40, 12),
                ('Lentil Soup', 250, 18, 40, 4),
                ('Avocado Toast', 280, 8, 25, 15),
                ('Protein Shake', 150, 24, 8, 3),
                ('Hummus with Veggies', 180, 6, 20, 10),
                ('Whole Wheat Pasta', 350, 12, 70, 2),

                # High calorie foods (for weight gain)
                ('Peanut Butter Sandwich', 380, 15, 40, 20),
                ('Protein Pancakes', 450, 25, 55, 15),
                ('Cheeseburger', 600, 35, 45, 30),
                ('Steak with Potatoes', 700, 45, 50, 35),
                ('Chicken Alfredo', 650, 35, 70, 25),
                ('Trail Mix (1/2 cup)', 350, 10, 30, 22),
                ('Full Breakfast Platter', 750, 35, 60, 40),
                ('Beef Burrito', 650, 35, 75, 25),
            ]

            for food in foods:
                cursor.execute('''
                    INSERT INTO fooditem (foodname, calories, protein, carbs, fats)
                    VALUES (%s, %s, %s, %s, %s)
                ''', food)

            mysql.connection.commit()
            print(f"✅ Added {len(foods)} food items to database!")
        else:
            print(f"✅ Database already has {count} food items")

        cursor.close()


if __name__ == '__main__':
    add_foods()