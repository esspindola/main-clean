from fastapi import HTTPException

from repositories.base_repository import BaseRepository

from utils.timezone_utils import get_current_time_with_timezone


class ProductRepository(BaseRepository):

    def create_product(self, name: str, description: str, price: float, stock: int, category: str, images: str, user_timezone: str = "UTC"):
        lastUpdated = get_current_time_with_timezone(user_timezone)
        createdAt = get_current_time_with_timezone(user_timezone)

        if self.db_type == 'mysql':
            with self._get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO products (name, description, price, stock, category, images, lastUpdated, createdAt) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (name, description, price, stock, category, images, lastUpdated, createdAt)
                )
                self.db.commit()
                return self.find_by_id(cursor.lastrowid)
        else:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO products (name, description, price, stock, category, images, lastUpdated, createdAt) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
                    (name, description, price, stock, category, images, lastUpdated, createdAt)
                )
                self.db.commit()
                return cursor.fetchone()

    def update_product(self, product_id, updates: dict, user_timezone: str = "UTC"):
        # Protecting the created_at and id Update field
        protect_fields = ['createdAt', 'id']
        for field in protect_fields:
            updates.pop(field, None)

        updates['lastUpdated'] = get_current_time_with_timezone(user_timezone)

        # For construction dynamic SQL
        set_clauses = []
        values = []

        for field, value in updates.items():
            set_clauses.append(f"{field}=%s")
            values.append(value)

        values.append(product_id)

        sql = f"UPDATE products SET {','.join(set_clauses)} WHERE id =%s"

        if self.db_type == 'mysql':
            with self._get_cursor() as cursor:
                cursor.execute(sql, values)
                self.db.commit()
                return self.find_by_id(product_id)
        else:
            with self._get_cursor() as cursor:
                cursor.execute(f"{sql} RETURNING *", values)
                self.db.commit()
                return cursor.fetchone()

    def find_all(self):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM products")
            return cursor.fetchall()

    def find_by_id(self, product_id: int):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
            return cursor.fetchone()

    def find_by_category(self, category: str):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE category=%s", (category, ))
            return cursor.fetchall()

    def find_by_name(self, name: str):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE name=%s", (name,))
            return cursor.fetchall()

    def delete_product(self, product_id: int):
        if self.db_type == 'mysql':
            with self._get_cursor() as cursor:
                cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
                product = cursor.fetchone()
                if not product:
                    raise HTTPException(status_code=404, detail="Product not found")
                cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
                self.db.commit()
                return product

        else:
             with self._get_cursor() as cursor:
                 cursor.execute("DELETE FROM products WHERE id=%s RETURNING *", (product_id,))
                 self.db.commit()
                 product = cursor.fetchone()
                 if not product:
                     raise HTTPException(status_code=404, detail="Product not found")
                 return product

