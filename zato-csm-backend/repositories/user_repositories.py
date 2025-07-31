import pymysql
import psycopg2.extras

from repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):

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

    def create_user(self, email: str, password: str, fullName: str, phone: str = None):
        if self.db_type == 'mysql':
            with self._get_cursor() as cursor:
                cursor.execute("INSERT INTO users (email, password, fullName, phone, role) VALUES (%s, %s, %s, %s, 'user')", (email, password, fullName, phone))
                self.db.commit()
                return self.find_by_user_id(cursor.lastrowid)
        else:
            with self._get_cursor() as cursor:
                cursor.execute("INSERT INTO users (email, password, fullName, phone, role) VALUES (%s, %s, %s, %s, 'user') RETURNING *", (email, password, fullName, phone))
                self.db.commit()
                return cursor.fetchone()

    def update_profile(self, user_id: int, fullName: str, phone: str, address: str):
        with self._get_cursor() as cursor:
            cursor.execute("UPDATE users SET fullName=%s, phone=%s, address=%s WHERE id=%s", (fullName, phone, address, user_id))
            self.db.commit()
            return self.find_by_user_id(user_id)