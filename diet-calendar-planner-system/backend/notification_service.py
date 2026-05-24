from datetime import datetime, timedelta
from typing import Dict, List, Optional

class NotificationService:
    """Service for managing in-app notifications with persistent storage (MySQL)"""

    def __init__(self):
        """Initialize notification service"""
        pass

    def create_notification(self, cursor, user_id: int, message: str, notification_type: str, data: Dict = None) -> int:
        """
        Create and store a new notification in MySQL
        
        Args:
            cursor: MySQL cursor from connection
            user_id: The user ID to notify
            message: The notification message
            notification_type: Type of notification ('action', 'warning', 'motivational')
            data: Optional dict with additional data
        
        Returns:
            Notification ID or None
        """
        try:
            cursor.execute('''
                INSERT INTO notifications (user_id, message, type, is_read, created_at)
                VALUES (%s, %s, %s, 0, NOW())
            ''', (user_id, message, notification_type))
            
            notification_id = cursor.lastrowid
            print(f"✅ Notification created (ID: {notification_id}): {message}")
            return notification_id
            
        except Exception as e:
            print(f"❌ Error creating notification: {e}")
            return None

    def create_action_notification(self, cursor, user_id: int, action_type: str, data: Dict) -> int:
        """Create action notification when meal/activity is logged"""
        if action_type == 'meal':
            message = f"🍽️ Meal logged: {data.get('meal_type', 'Meal')} - {data.get('food_name', 'Food')} ({data.get('calories', 0)} cal)"
        elif action_type == 'activity':
            emoji = data.get('icon', '🏃')
            message = f"{emoji} Activity logged: {data.get('activity_name', 'Exercise')} ({data.get('duration', 0)} min, {data.get('calories_burned', 0)} cal burned)"
        else:
            message = f"✅ Action completed"
        
        return self.create_notification(cursor, user_id, message, 'action', data)

    def create_warning_notification(self, cursor, user_id: int, warning_type: str, data: Dict) -> int:
        """Create warning notification for goal-related alerts"""
        messages = {
            'calorie_limit': f"⚠️ Approaching calorie limit ({data.get('consumed', 0)}/{data.get('goal', 2000)} cal)",
            'missing_breakfast': "🌅 You haven't logged breakfast yet",
            'missing_lunch': "🌤️ You haven't logged lunch yet",
            'missing_dinner': "🌙 You haven't logged dinner yet",
            'missing_activity': "🏃 You haven't logged any activity today",
            'low_water': "💧 Remember to drink water!",
            'exceeds_goal': f"⚠️ You've exceeded your daily calorie goal by {data.get('excess', 0)} cal"
        }
        
        message = messages.get(warning_type, "⚠️ Goal warning")
        return self.create_notification(cursor, user_id, message, 'warning', data)

    def create_motivational_notification(self, cursor, user_id: int, motivation_type: str, data: Dict) -> int:
        """Create motivational notifications for streaks, achievements, summaries"""
        if motivation_type == 'streak':
            streak_count = data.get('streak_days', 0)
            fire = "🔥" * min(streak_count // 5, 3)
            message = f"🎉 Amazing! {streak_count}-day logging streak! {fire}"
        elif motivation_type == 'weekly_summary':
            calories = data.get('total_calories', 0)
            activities = data.get('total_activities', 0)
            net_calories = data.get('net_calories', 0)
            message = f"📊 Weekly Summary: {calories} cal logged, {activities} activities, {net_calories} net calories"
        elif motivation_type == 'calorie_goal_met':
            message = f"✨ Great job! You've met your daily calorie goal!"
        elif motivation_type == 'activity_goal_met':
            message = f"💪 Excellent! You've completed your activity goal for the day!"
        elif motivation_type == 'suggestion':
            message = f"💡 Try this: {data.get('suggestion', 'Stay hydrated!')}"
        else:
            message = f"🌟 Keep up the great work!"
        
        return self.create_notification(cursor, user_id, message, 'motivational', data)

    def get_notifications(self, cursor, user_id: int, limit: int = 50, unread_only: bool = False) -> List[Dict]:
        """Fetch notifications for a user using provided MySQL cursor"""
        try:
            if unread_only:
                cursor.execute('''
                    SELECT id, message, type, is_read, 
                           DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at
                    FROM notifications
                    WHERE user_id = %s AND is_read = 0
                    ORDER BY created_at DESC
                    LIMIT %s
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT id, message, type, is_read, 
                           DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as created_at
                    FROM notifications
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                ''', (user_id, limit))

            rows = cursor.fetchall()
            # If cursor returns tuples, convert to dicts where possible
            try:
                notifications = [dict(row) for row in rows]
            except Exception:
                # fallback: map columns manually
                notifications = []
                cols = [d[0] for d in cursor.description]
                for row in rows:
                    notifications.append({cols[i]: row[i] for i in range(len(cols))})

            return notifications

        except Exception as e:
            print(f"❌ Error fetching notifications: {e}")
            return []

    def mark_notification_read(self, cursor, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read using provided MySQL cursor"""
        try:
            cursor.execute('''
                UPDATE notifications
                SET is_read = 1
                WHERE id = %s AND user_id = %s
            ''', (notification_id, user_id))
            success = cursor.rowcount > 0
            if success:
                print(f"✅ Notification {notification_id} marked as read")
            return success

        except Exception as e:
            print(f"❌ Error marking notification as read: {e}")
            return False

    def mark_all_read(self, cursor, user_id: int) -> bool:
        """Mark all notifications as read for a user using provided MySQL cursor"""
        try:
            cursor.execute('''
                UPDATE notifications
                SET is_read = 1
                WHERE user_id = %s AND is_read = 0
            ''', (user_id,))
            count = cursor.rowcount
            print(f"✅ Marked {count} notifications as read")
            return count > 0

        except Exception as e:
            print(f"❌ Error marking notifications as read: {e}")
            return False

    def delete_notification(self, cursor, notification_id: int, user_id: int) -> bool:
        """Delete a notification using provided MySQL cursor"""
        try:
            cursor.execute('''
                DELETE FROM notifications
                WHERE id = %s AND user_id = %s
            ''', (notification_id, user_id))
            success = cursor.rowcount > 0
            if success:
                print(f"✅ Notification {notification_id} deleted")
            return success

        except Exception as e:
            print(f"❌ Error deleting notification: {e}")
            return False

    def clean_old_notifications(self, user_id: int, days: int = 30) -> int:
        """Delete notifications older than specified days"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM notifications
                WHERE user_id = ? AND created_at < datetime('now', '-' || ? || ' days')
            ''', (user_id, days))
            
            conn.commit()
            deleted_count = cursor.rowcount
            print(f"✅ Deleted {deleted_count} old notifications for user {user_id}")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error cleaning notifications: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    def get_unread_count(self, cursor, user_id: int) -> int:
        """Get count of unread notifications using provided MySQL cursor"""
        try:
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM notifications
                WHERE user_id = %s AND is_read = 0
            ''', (user_id,))
            result = cursor.fetchone()
            # result may be tuple or dict
            if not result:
                return 0
            try:
                return result['count']
            except Exception:
                return list(result.values())[0] if hasattr(result, 'values') else int(result[0])
        except Exception as e:
            print(f"❌ Error getting unread count: {e}")
            return 0

    # ============= NOTIFICATION RULES ENGINE =============

    def check_calorie_warning(self, cursor, user_id: int) -> Optional[int]:
        """Check if user has exceeded 80% of daily calorie goal"""
        try:
            # Get user's goal
            cursor.execute('''
                SELECT goal FROM user WHERE userid = %s
            ''', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return None
            
            # Determine daily calorie goal based on goal type (default: 2000 for lose, 2500 for gain/maintain)
            daily_goal = 2000 if user.get('goal') == 'lose' else 2500
            warning_threshold = daily_goal * 0.8
            
            # Get today's meal calories
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COALESCE(SUM(totalcalories), 0) as total
                FROM meal
                WHERE planid IN (SELECT planid FROM dietplan WHERE userid = %s)
                AND mealdate = %s
            ''', (user_id, today))
            
            meal = cursor.fetchone()
            consumed = meal['total'] if meal else 0
            
            # Check if warning already exists for today
            today_start = f"{today} 00:00:00"
            cursor.execute('''
                SELECT id FROM notifications
                WHERE user_id = %s AND type = 'warning' 
                AND message LIKE %s
                AND created_at > %s
            ''', (user_id, '%Approaching calorie%', today_start))
            if cursor.fetchone():
                return None  # Already warned today
            
            # Create warning if threshold exceeded
            if consumed >= warning_threshold:
                return self.create_warning_notification(cursor, user_id, 'calorie_limit', {
                    'consumed': int(consumed),
                    'goal': daily_goal
                })
            
            return None
            
        except Exception as e:
            print(f"❌ Error checking calorie warning: {e}")
            return None

    def check_missing_meals(self, cursor, user_id: int) -> List[int]:
        """Check if user hasn't logged meals at typical times"""
        notifications = []
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            current_hour = datetime.now().hour
            
            # Check each meal type based on current time
            meal_checks = [
                ('Breakfast', 6, 10),      # Breakfast between 6-10 AM
                ('Lunch', 11, 14),         # Lunch between 11 AM-2 PM
                ('Dinner', 17, 20)         # Dinner between 5-8 PM
            ]
            
            for meal_type, start_hour, end_hour in meal_checks:
                if current_hour >= end_hour:  # Time has passed for this meal
                    cursor.execute('''
                        SELECT COUNT(*) as count
                        FROM meal
                        WHERE planid IN (SELECT planid FROM dietplan WHERE userid = %s)
                        AND mealdate = %s AND mealtype = %s
                    ''', (user_id, today, meal_type.capitalize()))
                    
                    result = cursor.fetchone()
                    if result and (result.get('count') if isinstance(result, dict) else result[0]) == 0:
                        # Check if warning already exists (within last 2 hours)
                        cursor.execute('''
                            SELECT id FROM notifications
                            WHERE user_id = %s AND type = 'warning' 
                            AND message LIKE %s
                            AND created_at > DATE_SUB(NOW(), INTERVAL 2 HOUR)
                        ''', (user_id, f"%{meal_type}%"))
                        
                        if not cursor.fetchone():
                            notif_id = self.create_warning_notification(
                                cursor,
                                user_id,
                                f'missing_{meal_type.lower()}',
                                {'meal_type': meal_type}
                            )
                            if notif_id:
                                notifications.append(notif_id)
            
            return notifications

        except Exception as e:
            print(f"❌ Error checking missing meals: {e}")
            return []

    def check_missing_activity(self, cursor, user_id: int) -> Optional[int]:
        """Check if user hasn't logged activity by evening (8 PM)"""
        try:
            current_hour = datetime.now().hour
            if current_hour < 20:
                return None

            today = datetime.now().strftime('%Y-%m-%d')

            cursor.execute('''
                SELECT COUNT(*) as count
                FROM user_activities
                WHERE user_id = %s AND date = %s
            ''', (user_id, today))
            row = cursor.fetchone()
            count = row['count'] if isinstance(row, dict) else (row[0] if row else 0)

            if count == 0:
                # check existing warning within 24 hours
                cursor.execute('''
                    SELECT id FROM notifications
                    WHERE user_id = %s AND type = 'warning'
                    AND message LIKE %s
                    AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
                ''', (user_id, '%activity%'))

                if not cursor.fetchone():
                    return self.create_warning_notification(cursor, user_id, 'missing_activity', {})

            return None

        except Exception as e:
            print(f"❌ Error checking missing activity: {e}")
            return None

    def check_streak(self, cursor, user_id: int) -> Optional[int]:
        """Check for logging streak and create notification if milestone reached"""
        try:
            streak_days = 0
            check_date = datetime.now()

            while True:
                check_date_str = check_date.strftime('%Y-%m-%d')

                cursor.execute('''
                    SELECT COUNT(*) as meal_count FROM meal
                    WHERE planid IN (SELECT planid FROM dietplan WHERE userid = %s)
                    AND mealdate = %s
                ''', (user_id, check_date_str))
                row = cursor.fetchone()
                meal_count = row['meal_count'] if isinstance(row, dict) else (row[0] if row else 0)

                cursor.execute('''
                    SELECT COUNT(*) as activity_count FROM user_activities
                    WHERE user_id = %s AND date = %s
                ''', (user_id, check_date_str))
                row = cursor.fetchone()
                activity_count = row['activity_count'] if isinstance(row, dict) else (row[0] if row else 0)

                if meal_count > 0 or activity_count > 0:
                    streak_days += 1
                    check_date -= timedelta(days=1)
                else:
                    break

            if streak_days > 0 and streak_days in [7, 14, 30]:
                cursor.execute('''
                    SELECT id FROM notifications
                    WHERE user_id = %s AND type = 'motivational'
                    AND message LIKE %s
                    AND created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
                ''', (user_id, f"%{streak_days}-day%"))

                if not cursor.fetchone():
                    return self.create_motivational_notification(cursor, user_id, 'streak', {'streak_days': streak_days})

            return None

        except Exception as e:
            print(f"❌ Error checking streak: {e}")
            return None
