import pymysql
import psycopg2.extras

from repositories.base_repository import BaseRepository
from utils.timezone_utils import get_current_time_with_timezone

class UserRepository(BaseRepository):
    def find_all_users(self):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()

    def find_by_email(self, email: str):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            return cursor.fetchone()

    def find_by_credentials(self, email: str, password: str):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, email, fullName, role FROM users WHERE email=%s AND password=%s", (email, password))
            return cursor.fetchone()

    def find_by_user_id(self, user_id: int):
        with self._get_cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
                return cursor.fetchone()

    def create_user(self, first_name: str, last_name: str, email: str, password: str, phone: str = None, user_timezone: str = "UTC"):
        fullName = first_name + ' ' + last_name
        created_at = get_current_time_with_timezone(user_timezone)
        lastUpdated = get_current_time_with_timezone(user_timezone)

        if self.db_type == 'mysql':
            with self._get_cursor() as cursor:
                cursor.execute("INSERT INTO users (firstName, lastName, email, password, fullName, phone, role, created_at, lastUpdated) VALUES (%s, %s, %s, %s, %s, %s, 'user', %s, %s)",
                               (first_name, last_name, email, password, fullName, phone, created_at, lastUpdated))
                self.db.commit()
                return self.find_by_user_id(cursor.lastrowid)
        else:
            with self._get_cursor() as cursor:
                cursor.execute("INSERT INTO users (firstName, lastName, email, password, fullName, phone, role, created_at, lastUpdated) VALUES (%s, %s, %s, %s, %s, %s, 'user', %s, %s) RETURNING *",
                               (first_name, last_name, email, password, fullName, phone, created_at, lastUpdated))
                self.db.commit()
                return cursor.fetchone()

    def update_profile(self, user_id: int, updates: dict, user_timezone: str = "UTC"):
        # Validation fields
        allowed_fields = ['firstName', 'lastName', 'phone', 'address']

        # Protecting the created_at and id Update field
        protect_fields = ['createdAt', 'id']

        for field in protect_fields:
            updates.pop(field, None)

        updates['lastUpdated'] = get_current_time_with_timezone(user_timezone)

        fullName = None
        if updates.get('firstName') or updates.get('lastName'):
            firstName = updates.get('firstName', '')
            lastName = updates.get('lastName', '')
            fullName = firstName + ' ' + lastName
            updates['fullName'] = fullName

        with self._get_cursor() as cursor:
            cursor.execute("UPDATE users SET firstName=%s, lastName=%s, fullName=%s, phone=%s, address=%s WHERE id=%s",
                           (updates.get('firstName'), updates.get('lastName'), fullName, updates.get('phone'), updates.get('address'), user_id))
            self.db.commit()
            return self.find_by_user_id(user_id)