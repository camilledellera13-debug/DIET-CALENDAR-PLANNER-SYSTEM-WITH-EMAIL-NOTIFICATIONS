"""
Enhanced Notification System for Diet Calendar Planner
Sends automated email notifications for meals and activities
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import json
from typing import List, Dict, Optional


class EmailNotificationService:
    """Service for sending notification emails"""
    
    def __init__(self, smtp_server: str = 'smtp.gmail.com', smtp_port: int = 587):
        """Initialize email service with SMTP settings"""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = os.environ.get('MAIL_USERNAME', '')
        self.sender_password = os.environ.get('MAIL_PASSWORD', '')
        self.sender_name = "Diet Calendar Planner"
        
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.sender_email and self.sender_password)
    
    def send_email(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """Send email to recipient"""
        if not self.is_configured():
            print("⚠️ Email service not configured. Set MAIL_USERNAME and MAIL_PASSWORD environment variables.")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_meal_notification(self, recipient_email: str, user_name: str, meal_info: Dict) -> bool:
        """Send meal logged notification email"""
        subject = f"🍽️ Your {meal_info.get('meal_type', 'Meal').title()} is Logged!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ background: white; padding: 30px; }}
                .meal-info {{ background: #f9f9f9; border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-item {{ text-align: center; }}
                .stat-label {{ color: #666; font-size: 12px; text-transform: uppercase; }}
                .stat-value {{ color: #667eea; font-size: 24px; font-weight: bold; }}
                .tip {{ background: #e3f2fd; padding: 15px; border-radius: 5px; color: #1565c0; font-size: 14px; margin-top: 20px; }}
                .footer {{ background: #f0f0f0; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 10px 0;">🍽️ Meal Successfully Logged!</h1>
                    <p style="margin: 0; opacity: 0.9;">Great job staying on track!</p>
                </div>
                <div class="content">
                    <h2 style="color: #333; margin-top: 0;">Hey {user_name}! 👋</h2>
                    <p style="color: #666;">Your meal has been successfully recorded in your Diet Calendar Planner.</p>
                    
                    <div class="meal-info">
                        <strong style="color: #667eea; font-size: 16px;">{meal_info.get('meal_type', 'MEAL').upper()}</strong>
                        <p style="margin: 10px 0 0 0; color: #333;">
                            <strong>Food Item:</strong> {meal_info.get('food_name', 'N/A')}
                        </p>
                    </div>

                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-label">Calories</div>
                            <div class="stat-value">{meal_info.get('calories', 0)}</div>
                            <div style="color: #999; font-size: 12px;">kcal</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Date</div>
                            <div class="stat-value">📅</div>
                            <div style="color: #999; font-size: 12px;">{meal_info.get('date', 'Today')}</div>
                        </div>
                    </div>

                    <div class="tip">
                        <strong>💡 Pro Tip:</strong> Log all your meals consistently for accurate calorie tracking and personalized recommendations!
                    </div>
                </div>
                <div class="footer">
                    <p>Automated notification from Diet Calendar Planner System</p>
                    <p style="margin: 5px 0;">Stay healthy, stay consistent! 💪</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(recipient_email, subject, html_content)
    
    def send_activity_notification(self, recipient_email: str, user_name: str, activity_info: Dict) -> bool:
        """Send activity logged notification email"""
        subject = f"{activity_info.get('icon', '🏃')} Activity Logged - {activity_info.get('name', 'Exercise')}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ background: white; padding: 30px; }}
                .activity-info {{ background: #fff3e0; border-left: 4px solid #f5576c; padding: 15px; margin: 15px 0; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-item {{ text-align: center; }}
                .stat-label {{ color: #666; font-size: 12px; text-transform: uppercase; }}
                .stat-value {{ color: #f5576c; font-size: 24px; font-weight: bold; }}
                .tip {{ background: #f3e5f5; padding: 15px; border-radius: 5px; color: #6a1b9a; font-size: 14px; margin-top: 20px; }}
                .footer {{ background: #f0f0f0; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 10px 0;">🎉 Awesome! Activity Logged!</h1>
                    <p style="margin: 0; opacity: 0.9;">You're crushing your fitness goals!</p>
                </div>
                <div class="content">
                    <h2 style="color: #333; margin-top: 0;">Great Job, {user_name}! 💪</h2>
                    <p style="color: #666;">Your exercise has been successfully recorded in your fitness tracker.</p>
                    
                    <div class="activity-info">
                        <strong style="color: #f5576c; font-size: 16px;">{activity_info.get('icon', '🏃')} {activity_info.get('name', 'ACTIVITY').upper()}</strong>
                        <p style="margin: 10px 0 0 0; color: #333;">
                            <strong>Intensity:</strong> {activity_info.get('intensity', 'N/A').capitalize()}
                        </p>
                    </div>

                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-label">Duration</div>
                            <div class="stat-value">{activity_info.get('duration', 0)}</div>
                            <div style="color: #999; font-size: 12px;">min</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Calories Burned</div>
                            <div class="stat-value">{activity_info.get('calories_burned', 0)}</div>
                            <div style="color: #999; font-size: 12px;">kcal</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Date</div>
                            <div class="stat-value">📅</div>
                            <div style="color: #999; font-size: 12px;">{activity_info.get('date', 'Today')}</div>
                        </div>
                    </div>

                    <div class="tip">
                        <strong>🔥 Motivational Tip:</strong> You're burning calories and building a healthier you! Keep up this amazing momentum!
                    </div>
                </div>
                <div class="footer">
                    <p>Automated notification from Diet Calendar Planner System</p>
                    <p style="margin: 5px 0;">Keep moving, keep achieving! 🚀</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(recipient_email, subject, html_content)
    
    def send_daily_summary(self, recipient_email: str, user_name: str, meals: List[Dict], 
                          activities: List[Dict]) -> bool:
        """Send daily summary email with meals and activities"""
        subject = f"📆 Your Daily Summary - {datetime.now().strftime('%B %d, %Y')}"
        
        meals_html = ""
        total_meal_calories = 0
        for meal in meals:
            total_meal_calories += meal.get('calories', 0)
            meals_html += f"""
            <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 12px; margin: 10px 0; border-radius: 3px;">
                <strong style="color: #2e7d32;">🍽️ {meal.get('meal_type', 'MEAL').upper()}</strong>
                <p style="margin: 5px 0; color: #333;">Food: {meal.get('food_name', 'TBD')}</p>
                <p style="margin: 5px 0; color: #666; font-size: 12px;">Calories: {meal.get('calories', 'N/A')} kcal</p>
            </div>
            """
        
        activities_html = ""
        total_activity_calories = 0
        for activity in activities:
            total_activity_calories += activity.get('calories_burned', 0)
            activities_html += f"""
            <div style="background: #fce4ec; border-left: 4px solid #e91e63; padding: 12px; margin: 10px 0; border-radius: 3px;">
                <strong style="color: #c2185b;">{activity.get('icon', '🏃')} {activity.get('name', 'ACTIVITY').upper()}</strong>
                <p style="margin: 5px 0; color: #333;">Duration: {activity.get('duration_minutes', 'N/A')} minutes</p>
                <p style="margin: 5px 0; color: #666; font-size: 12px;">Calories Burned: {activity.get('calories_burned', 0)} kcal</p>
            </div>
            """
        
        net_calories = total_meal_calories - total_activity_calories
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                .content {{ background: white; padding: 30px; }}
                .summary-box {{ background: #f0f4ff; border-radius: 8px; padding: 15px; margin: 15px 0; }}
                .calorie-stat {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ddd; }}
                .calorie-stat-last {{ border-bottom: none; font-weight: bold; color: #667eea; }}
                .footer {{ background: #f0f0f0; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 10px 0;">📆 Daily Summary</h1>
                    <p style="margin: 0; opacity: 0.9;">{datetime.now().strftime('%A, %B %d, %Y')}</p>
                </div>
                <div class="content">
                    <h2 style="color: #333; margin-top: 0;">Hello {user_name}! 👋</h2>
                    <p style="color: #666;">Here's a summary of your meals and activities for today.</p>
                    
                    {'<h3 style="color: #667eea; margin-top: 25px;">🍽️ Meals:</h3>' + meals_html if meals_html else '<p style="color: #999;">No meals logged yet.</p>'}
                    
                    {'<h3 style="color: #f5576c; margin-top: 25px;">🏃 Activities:</h3>' + activities_html if activities_html else '<p style="color: #999;">No activities logged yet.</p>'}
                    
                    <div class="summary-box">
                        <h4 style="margin-top: 0; color: #667eea;">📊 Calorie Summary:</h4>
                        <div class="calorie-stat">
                            <span>Total Meal Calories:</span>
                            <strong style="color: #4caf50;">{total_meal_calories} kcal</strong>
                        </div>
                        <div class="calorie-stat">
                            <span>Total Activity Calories:</span>
                            <strong style="color: #f5576c;">{total_activity_calories} kcal</strong>
                        </div>
                        <div class="calorie-stat calorie-stat-last">
                            <span>Net Calories:</span>
                            <strong>{net_calories} kcal</strong>
                        </div>
                    </div>
                </div>
                <div class="footer">
                    <p>Automated notification from Diet Calendar Planner System</p>
                    <p style="margin: 5px 0;">Have a productive and healthy day! 🌟</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(recipient_email, subject, html_content)


# Singleton instance
_email_service = None

def get_email_service() -> EmailNotificationService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailNotificationService()
    return _email_service


# Legacy function for backward compatibility
def send_email(recipient_email: str, subject: str, body: str) -> bool:
    """Send a simple text email (backward compatible)"""
    service = get_email_service()
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 20px;">
            <div style="background: white; padding: 20px; border-radius: 5px;">
                {body.replace(chr(10), '<br>')}
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated notification from Diet Calendar Planner System
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return service.send_email(recipient_email, subject, html_body)


if __name__ == '__main__':
    # Test the email service
    service = get_email_service()
    
    if service.is_configured():
        # Test meal notification
        service.send_meal_notification(
            'test@example.com',
            'Test User',
            {
                'meal_type': 'Breakfast',
                'food_name': 'Oatmeal with Berries',
                'calories': 350,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        )
    else:
        print("⚠️ Email service not configured. Please set MAIL_USERNAME and MAIL_PASSWORD environment variables.")
