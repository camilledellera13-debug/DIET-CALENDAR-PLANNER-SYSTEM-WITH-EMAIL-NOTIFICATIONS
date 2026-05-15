-- Users table with goal tracking
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    goal TEXT CHECK(goal IN ('lose', 'gain', 'maintain')) DEFAULT 'maintain',
    name TEXT,
    age INTEGER,
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Foods table
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    calories INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meals table
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (food_id) REFERENCES foods (id)
);

-- Activities table
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    calories_per_minute DECIMAL(5,2) NOT NULL,
    intensity TEXT CHECK(intensity IN ('low', 'medium', 'high')),
    goal_type TEXT CHECK(goal_type IN ('lose', 'gain', 'maintain', 'all')),
    description TEXT,
    icon TEXT
);

-- User activities log
CREATE TABLE IF NOT EXISTS user_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    duration_minutes INTEGER NOT NULL,
    date DATE NOT NULL,
    calories_burned INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (activity_id) REFERENCES activities (id)
);

-- Insert sample activities
INSERT OR IGNORE INTO activities (name, calories_per_minute, intensity, goal_type, description, icon) VALUES
('🏃 Jogging', 11.5, 'high', 'lose', 'Great for burning calories and improving cardiovascular health', '🏃'),
('🏃‍♀️ Running', 13.0, 'high', 'lose', 'High-intensity cardio for maximum calorie burn', '🏃‍♀️'),
('⚡ HIIT Training', 14.5, 'high', 'lose', 'High Intensity Interval Training for rapid fat loss', '⚡'),
('跳绳 Jump Rope', 12.5, 'high', 'lose', 'Excellent full-body workout', '🎯'),
('🚶 Brisk Walking', 5.5, 'medium', 'maintain', 'Low-impact activity for daily health', '🚶'),
('🚴 Cycling', 8.0, 'medium', 'maintain', 'Great for leg strength and endurance', '🚴'),
('🏊 Swimming', 9.0, 'medium', 'maintain', 'Full-body low-impact workout', '🏊'),
('🧘 Yoga', 4.0, 'low', 'maintain', 'Improves flexibility and reduces stress', '🧘'),
('🚶 Light Walking', 3.5, 'low', 'gain', 'Gentle activity to maintain mobility', '🚶'),
('🧘‍♀️ Stretching', 2.5, 'low', 'gain', 'Improves flexibility without burning excess calories', '🧘‍♀️'),
('🚶‍♂️ Meditation Walk', 2.0, 'low', 'gain', 'Mindful walking for mental clarity', '🚶‍♂️');

-- Sample data for foods
INSERT OR IGNORE INTO foods (name, calories) VALUES
('Oatmeal with fruits', 350),
('Grilled chicken salad', 450),
('Salmon with quinoa', 550),
('Greek yogurt', 150),
('Apple', 95),
('Almonds (30g)', 180),
('Brown rice bowl', 400),
('Avocado toast', 300);

-- Sample user for testing (password: password)
INSERT OR IGNORE INTO users (email, password, goal) VALUES 
('test@example.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'maintain');