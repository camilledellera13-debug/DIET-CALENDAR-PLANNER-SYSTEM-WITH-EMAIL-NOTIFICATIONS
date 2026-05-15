import sqlite3


def view_all_users():
    conn = sqlite3.connect('schema.db')
    cursor = conn.cursor()

    cursor.execute("SELECT userid, name, email, goal, weight, height FROM users")
    users = cursor.fetchall()

    print("\n" + "=" * 60)
    print("Existing Users in Database:")
    print("=" * 60)

    for user in users:
        print(f"ID: {user[0]}")
        print(f"Name: {user[1]}")
        print(f"Email: {user[2]}")
        print(f"Goal: {user[3]}")
        print(f"Weight: {user[4]} kg")
        print(f"Height: {user[5]} cm")
        print("-" * 40)

    conn.close()

    if not users:
        print("No users found in database!")


if __name__ == '__main__':
    view_all_users()