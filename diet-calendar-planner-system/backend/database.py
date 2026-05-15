import sqlite3
import os
from datetime import datetime

DB_PATH = 'schema.db'


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            age INTEGER,
            gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
            height DECIMAL(5,2),
            weight DECIMAL(5,2),
            goal TEXT CHECK(goal IN ('lose', 'gain', 'maintain')) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dietplan (
            planid INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            planname VARCHAR(100) NOT NULL,
            description TEXT,
            startdate DATE NOT NULL,
            enddate DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userid) REFERENCES users (userid) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fooditem (
            foodid INTEGER PRIMARY KEY AUTOINCREMENT,
            foodname VARCHAR(100) UNIQUE NOT NULL,
            calories DECIMAL(6,2) NOT NULL,
            protein DECIMAL(5,2) DEFAULT 0.00,
            carbs DECIMAL(5,2) DEFAULT 0.00,
            fats DECIMAL(5,2) DEFAULT 0.00
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal (
            mealid INTEGER PRIMARY KEY AUTOINCREMENT,
            planid INTEGER NOT NULL,
            mealtype TEXT CHECK(mealtype IN ('Breakfast', 'Lunch', 'Dinner', 'Snack')) NOT NULL,
            mealdate DATE NOT NULL,
            totalcalories DECIMAL(6,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (planid) REFERENCES dietplan (planid) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mealfood (
            mealid INTEGER NOT NULL,
            foodid INTEGER NOT NULL,
            quantity DECIMAL(5,2) DEFAULT 1.00,
            servingsize VARCHAR(50),
            PRIMARY KEY (mealid, foodid),
            FOREIGN KEY (mealid) REFERENCES meal (mealid) ON DELETE CASCADE,
            FOREIGN KEY (foodid) REFERENCES fooditem (foodid) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progresslog (
            logid INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            weight DECIMAL(5,2) NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, date),
            FOREIGN KEY (user_id) REFERENCES users (userid) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS waterintake (
            intakeid INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            date DATE NOT NULL,
            amountml INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(userid, date),
            FOREIGN KEY (userid) REFERENCES users (userid) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories_per_minute DECIMAL(5,2) NOT NULL,
            intensity TEXT CHECK(intensity IN ('low', 'medium', 'high')),
            goal_type TEXT CHECK(goal_type IN ('lose', 'gain', 'maintain', 'all')),
            description TEXT,
            icon TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            duration_minutes INTEGER NOT NULL,
            date DATE NOT NULL,
            calories_burned INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (userid) ON DELETE CASCADE,
            FOREIGN KEY (activity_id) REFERENCES activities (id) ON DELETE CASCADE
        )
    ''')
    insert_sample_data(cursor)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def insert_sample_data(cursor):
    cursor.execute('''
        INSERT OR IGNORE INTO users (userid, name, email, password, age, gender, height, weight, goal)
        VALUES 
        (1, 'John Doe', 'john@example.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 30, 'Male', 175.50, 80.20, 'lose'),
        (2, 'John Smith', 'john.smith@email.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 32, 'Male', 180.50, 85.30, 'lose'),
        (3, 'Sarah Johnson', 'sarah.j@email.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 28, 'Female', 165.00, 68.50, 'maintain'),
        (4, 'Mike Chen', 'mike.chen@email.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 35, 'Male', 175.00, 92.00, 'gain')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO dietplan (planid, userid, planname, description, startdate, enddate)
        VALUES 
        (1, 1, 'Summer Cut 2026', 'High protein, low carb for fat loss', '2026-04-01', '2026-06-30'),
        (2, 1, 'Maintenance Phase', 'Balanced diet after summer cut', '2026-07-01', '2026-09-30'),
        (3, 2, 'Clean Bulk', 'Slow muscle gain with clean foods', '2026-04-01', '2026-07-31'),
        (4, 2, 'Weight Maintenance', 'Keeping current weight stable', '2026-08-01', '2026-12-31'),
        (5, 3, 'Mass Gain 3000', 'Calorie surplus for muscle gain', '2026-04-15', '2026-08-15'),
        (6, 3, 'Lean Bulk', 'Moderate surplus, cleaner foods', '2026-08-16', '2026-12-31')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO fooditem (foodid, foodname, calories, protein, carbs, fats)
        VALUES 
        (1, 'Chicken Breast', 165.00, 31.00, 0.00, 3.60),
        (2, 'Brown Rice', 112.00, 2.60, 23.50, 0.90),
        (3, 'Broccoli', 55.00, 3.70, 11.20, 0.60),
        (4, 'Apple', 95.00, 0.50, 25.00, 0.30),
        (5, 'Grilled Chicken Breast', 165.00, 31.00, 0.00, 3.60),
        (6, 'Brown Rice (cooked)', 112.00, 2.60, 23.50, 0.90),
        (7, 'Steamed Broccoli', 55.00, 3.70, 11.20, 0.60),
        (8, 'Scrambled Eggs (2)', 140.00, 12.00, 1.00, 10.00),
        (9, 'Oatmeal with Berries', 158.00, 5.50, 27.00, 3.20),
        (10, 'Greek Yogurt', 100.00, 17.00, 6.00, 0.40),
        (11, 'Salmon Fillet', 208.00, 22.00, 0.00, 13.00),
        (12, 'Sweet Potato', 114.00, 2.00, 27.00, 0.10),
        (13, 'Avocado', 234.00, 2.90, 12.00, 21.00),
        (14, 'Protein Shake (whey)', 120.00, 24.00, 3.00, 1.50),
        (15, 'Quinoa Salad', 120.00, 4.40, 21.30, 1.90),
        (16, 'Banana', 105.00, 1.30, 27.00, 0.40),
        (17, 'Almonds (10 pcs)', 69.00, 2.50, 2.50, 6.00),
        (18, 'Whole Wheat Bread (2 slices)', 160.00, 6.00, 30.00, 2.00),
        (19, 'Peanut Butter (1 tbsp)', 94.00, 4.00, 3.50, 8.00)
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO meal (mealid, planid, mealtype, mealdate, totalcalories)
        VALUES 
        (1, 1, 'Breakfast', '2026-04-03', 340.00),
        (2, 1, 'Lunch', '2026-04-03', 450.00),
        (3, 1, 'Dinner', '2026-04-03', 520.00),
        (4, 1, 'Snack', '2026-04-03', 120.00),
        (5, 1, 'Breakfast', '2026-04-04', 340.00),
        (6, 1, 'Lunch', '2026-04-04', 465.00),
        (7, 1, 'Dinner', '2026-04-04', 510.00),
        (8, 1, 'Snack', '2026-04-04', 100.00)
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO mealfood (mealid, foodid, quantity, servingsize)
        VALUES 
        (1, 5, 1.00, '1 bowl'),
        (1, 6, 1.00, '1 cup'),
        (2, 1, 1.50, '150g'),
        (2, 2, 1.00, '1 cup'),
        (2, 3, 1.00, '1 cup'),
        (4, 13, 1.00, '10 almonds')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO progresslog (logid, user_id, date, weight, notes)
        VALUES 
        (1, 1, '2026-04-01', 85.30, 'Starting weight'),
        (2, 1, '2026-04-08', 84.50, 'Down 0.8kg, feeling good'),
        (3, 1, '2026-04-15', 83.90, 'Steady progress'),
        (4, 2, '2026-04-01', 68.50, 'Starting weight'),
        (5, 2, '2026-04-08', 68.40, 'Stable'),
        (6, 3, '2026-04-15', 92.00, 'Starting bulk'),
        (7, 3, '2026-04-22', 92.80, 'Up 0.8kg, good start')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO waterintake (intakeid, userid, date, amountml)
        VALUES 
        (1, 1, '2026-04-03', 2500),
        (2, 1, '2026-04-04', 2700),
        (3, 1, '2026-04-05', 2600),
        (4, 2, '2026-04-03', 2100),
        (5, 2, '2026-04-04', 2300),
        (6, 3, '2026-04-16', 3000)
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO activities (id, name, calories_per_minute, intensity, goal_type, description, icon)
        VALUES 
        (1, 'Jogging', 11.5, 'high', 'lose', 'Great for burning calories and improving cardiovascular health', '🏃'),
        (2, 'Running', 13.0, 'high', 'lose', 'High-intensity cardio for maximum calorie burn', '🏃‍♀️'),
        (3, 'HIIT Training', 14.5, 'high', 'lose', 'High Intensity Interval Training for rapid fat loss', '⚡'),
        (4, 'Jump Rope', 12.5, 'high', 'lose', 'Excellent full-body workout', '🎯'),
        (5, 'Brisk Walking', 5.5, 'medium', 'maintain', 'Low-impact activity for daily health', '🚶'),
        (6, 'Cycling', 8.0, 'medium', 'maintain', 'Great for leg strength and endurance', '🚴'),
        (7, 'Swimming', 9.0, 'medium', 'maintain', 'Full-body low-impact workout', '🏊'),
        (8, 'Yoga', 4.0, 'low', 'maintain', 'Improves flexibility and reduces stress', '🧘'),
        (9, 'Light Walking', 3.5, 'low', 'gain', 'Gentle activity to maintain mobility', '🚶'),
        (10, 'Stretching', 2.5, 'low', 'gain', 'Improves flexibility without burning excess calories', '🧘‍♀️'),
        (11, 'Meditation Walk', 2.0, 'low', 'gain', 'Mindful walking for mental clarity', '🚶‍♂️')
    ''')

    print("Sample data inserted successfully!")


def migrate_existing_db():
    if os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} already exists. Checking structure...")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Creating new tables...")
            conn.close()
            init_database()
        else:
            print("Database already has tables. Checking for missing tables...")
            tables_to_create = ['activities', 'user_activities']
            for table in tables_to_create:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    print(f"Creating missing table: {table}")
                    if table == 'activities':
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS activities (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                calories_per_minute DECIMAL(5,2) NOT NULL,
                                intensity TEXT CHECK(intensity IN ('low', 'medium', 'high')),
                                goal_type TEXT CHECK(goal_type IN ('lose', 'gain', 'maintain', 'all')),
                                description TEXT,
                                icon TEXT
                            )
                        ''')
                        cursor.execute('''
                            INSERT OR IGNORE INTO activities (id, name, calories_per_minute, intensity, goal_type, description, icon)
                            VALUES 
                            (1, 'Jogging', 11.5, 'high', 'lose', 'Great for burning calories', '🏃'),
                            (2, 'Running', 13.0, 'high', 'lose', 'High-intensity cardio', '🏃‍♀️'),
                            (3, 'Light Walking', 3.5, 'low', 'gain', 'Gentle activity', '🚶'),
                            (4, 'Yoga', 4.0, 'low', 'maintain', 'Improves flexibility', '🧘')
                        ''')
                    elif table == 'user_activities':
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS user_activities (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                activity_id INTEGER NOT NULL,
                                duration_minutes INTEGER NOT NULL,
                                date DATE NOT NULL,
                                calories_burned INTEGER,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id) REFERENCES users (userid) ON DELETE CASCADE,
                                FOREIGN KEY (activity_id) REFERENCES activities (id) ON DELETE CASCADE
                            )
                        ''')

            conn.commit()
            conn.close()
            print("Migration completed!")

    else:
        print("Creating new database...")
        init_database()


if __name__ == '__main__':
    migrate_existing_db()