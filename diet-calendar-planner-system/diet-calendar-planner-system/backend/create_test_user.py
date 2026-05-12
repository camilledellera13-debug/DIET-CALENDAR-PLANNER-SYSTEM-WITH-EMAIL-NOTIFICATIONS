from database import get_db_connection
import hashlib

def create_test_user():
    conn = get_db_connection()

    email = "test@example.com"
    password = "password123"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn.execute('''
            INSERT INTO users (name, email, password, goal, age, weight, height)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("Test User", email, hashed_password, "maintain", 25, 70, 175))
        conn.commit()
        print(f"Test user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"User might already exist: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    create_test_user()