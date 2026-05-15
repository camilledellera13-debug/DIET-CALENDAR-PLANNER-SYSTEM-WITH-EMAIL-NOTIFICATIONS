from flask_mysqldb import MySQL
from app import app


def add_sample_foods():
    with app.app_context():
        cursor = mysql.connection.cursor()

        # Sample foods for weight loss (low calorie)
        low_cal_foods = [
            ('Greek Yogurt (plain)', 100, 17, 6, 0.4),
            ('Apple', 95, 0.5, 25, 0.3),
            ('Broccoli (steamed)', 55, 3.7, 11.2, 0.6),
            ('Chicken Breast (grilled)', 165, 31, 0, 3.6),
            ('Quinoa Salad', 120, 4.4, 21.3, 1.9),
            ('Oatmeal', 158, 5.5, 27, 3.2),
            ('Banana', 105, 1.3, 27, 0.4),
            ('Almonds (10 pieces)', 69, 2.5, 2.5, 6),
        ]

        # Sample foods for weight gain (high calorie)
        high_cal_foods = [
            ('Peanut Butter Sandwich', 380, 15, 40, 20),
            ('Protein Shake', 250, 30, 15, 8),
            ('Brown Rice Bowl', 350, 8, 70, 4),
            ('Salmon Fillet', 208, 22, 0, 13),
            ('Avocado', 234, 2.9, 12, 21),
            ('Sweet Potato with Butter', 250, 3, 45, 7),
            ('Trail Mix (1/2 cup)', 350, 10, 30, 25),
            ('Whole Milk (1 cup)', 150, 8, 12, 8),
        ]

        # Insert foods
        for food in low_cal_foods + high_cal_foods:
            cursor.execute('''
                INSERT INTO fooditem (foodname, calories, protein, carbs, fats)
                SELECT %s, %s, %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM fooditem WHERE foodname = %s)
            ''', (food[0], food[1], food[2], food[3], food[4], food[0]))

        mysql.connection.commit()
        cursor.close()
        print("Sample foods added successfully!")


if __name__ == '__main__':
    add_sample_foods()