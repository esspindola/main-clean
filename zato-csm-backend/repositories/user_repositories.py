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
            cursor.execute("SELECT id, email, full_name, role FROM users WHERE email=%s AND password=%s", (email, password))
            return cursor.fetchone()

    def find_by_user_id(self, user_id: int):
        with self._get_cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
                return cursor.fetchone()

    def create_user(self, first_name: str, last_name: str, email: str, password: str, phone: str = None, user_timezone: str = "UTC"):
        full_name = first_name + ' ' + last_name
        created_at = get_current_time_with_timezone(user_timezone)
        last_updated = get_current_time_with_timezone(user_timezone)

        if self.db_type == 'mysql':
            with self._get_cursor() as cursor:
                cursor.execute("INSERT INTO users (first_name, last_name, email, password, full_name, phone, role, created_at, last_updated) VALUES (%s, %s, %s, %s, %s, %s, 'user', %s, %s)",
                               (first_name, last_name, email, password, full_name, phone, created_at, last_updated))
                self.db.commit()
                return self.find_by_user_id(cursor.lastrowid)
        else:
            with self._get_cursor() as cursor:
                cursor.execute("INSERT INTO users (first_name, last_name, email, password, full_name, phone, role, created_at, last_updated) VALUES (%s, %s, %s, %s, %s, %s, 'user', %s, %s) RETURNING *",
                               (first_name, last_name, email, password, full_name, phone, created_at, last_updated))
                self.db.commit()
                return cursor.fetchone()

    def update_profile(self, user_id: int, updates: dict, user_timezone: str = "UTC"):
        # Validation fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'address']

        # Protecting the created_at and id Update field
        protect_fields = ['created_at', 'id']

        for field in protect_fields:
            updates.pop(field, None)

        updates['last_updated'] = get_current_time_with_timezone(user_timezone)

        full_name = None
        if updates.get('first_name') or updates.get('last_name'):
            first_name = updates.get('first_name', '')
            last_name = updates.get('last_name', '')
            full_name = first_name + ' ' + last_name
            updates['full_name'] = full_name

        with self._get_cursor() as cursor:
            cursor.execute("UPDATE users SET first_name=%s, last_name=%s, full_name=%s, phone=%s, address=%s, last_updated=%s WHERE id=%s",
                           (updates.get('first_name'), updates.get('last_name'), full_name, updates.get('phone'), updates.get('address'), updates.get('last_updated'), user_id))
            self.db.commit()
            return self.find_by_user_id(user_id)