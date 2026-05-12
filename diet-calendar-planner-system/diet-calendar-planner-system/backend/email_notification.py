import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailNotifier:
    def __init__(self, email_address, email_password):
        self.email_address = email_address
        self.email_password = email_password
    
    def send_meal_notification(self, user_email, meal_data):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = user_email
        msg['Subject'] = f"🍽️ Meal Logged: {meal_data['food_name']}"
        
        body = f"""
        New meal has been logged in your diet planner:
        
        🕒 {meal_data['meal_type'].title()}
        🍲 {meal_data['food_name']}
        🔥 {meal_data['calories']} calories
        📅 {meal_data['date']}
        
        Keep up the great work! 💪
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email failed: {e}")
            return False