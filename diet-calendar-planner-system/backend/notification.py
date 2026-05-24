import os
import sqlite3  # or your specific database library
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def get_todays_meals_from_db():
    """
    Safely reads today's data without modifying anything.
    Adjust the database name and query columns to match your setup.
    """
    today_date = "21/05/2026"  # You can use datetime.now().strftime("%d/%m/%Y") later

    # Connect to your existing database in read-only mode if possible
    conn = sqlite3.connect('meals.db')
    cursor = conn.cursor()

    # Adjust this query to match your exact database table layout
    cursor.execute("SELECT meal_type, food_name FROM meals WHERE date = ?", (today_date,))
    rows = cursor.fetchall()

    items = []
    for row in rows:
        items.append({
            "type": row[0],  # e.g., 'Breakfast'
            "name": row[1]  # e.g., 'egg'
        })

    conn.close()
    return today_date, items


def send_notification_email():
    target_date, schedule_items = get_todays_meals_from_db()

    if not schedule_items:
        print("No meals logged for today. No email sent.")
        return

    # Email configuration
    sender_email = "your_email@gmail.com"
    sender_password = "your_gmail_app_password"
    receiver_email = "user_email@gmail.com"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📅 Your Schedule for {target_date}"
    msg['From'] = f"Diet Planner <{sender_email}>"
    msg['To'] = receiver_email

    # Generate layout matches your UI colors without modifying your CSS files
    items_html = ""
    for item in schedule_items:
        bg_color = "#2ed573" if "Stretching" not in item['type'] else "#e056fd"
        items_html += f"""
        <div style="background-color: {bg_color}; color: white; padding: 6px 12px; margin: 5px 0; border-radius: 4px; font-family: Arial, sans-serif; font-size: 14px;">
            ● <strong>{item['type']}:</strong> {item['name']}
        </div>
        """

    # Clickable link pointing to your existing server address
    clickable_url = f"http://127.0.0.1:5000/calendar.html"

    html_content = f"""
    <html>
    <body style="margin: 0; padding: 20px; background-color: #f4f5f7;">
        <div style="max-width: 400px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; border: 1px solid #e1e4e8; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <div style="background-color: #6C5CE7; padding: 20px; text-align: center; color: white;">
                <h3 style="margin: 0; font-family: Arial, sans-serif;">Today's Overview</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">{target_date}</p>
            </div>
            <div style="padding: 20px;">
                {items_html}
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{clickable_url}" target="_blank" style="background-color: #6C5CE7; color: white; padding: 10px 20px; text-decoration: none; font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; border-radius: 6px; display: inline-block;">
                        ✨ Open Calendar App
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Notification email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == "__main__":
    send_notification_email()