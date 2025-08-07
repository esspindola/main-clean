import pymysql
import psycopg2.extras

class BaseRepository:
    def __init__(self, db, db_type='postgres'):
        # print(f"DEBUG: db type: {type(db)}")  # Debug temporário
        # print(f"DEBUG: db value: {db}")
        self.db = db
        self.db_type = db_type

    def _get_cursor(self):
        """
        Return appropriate cursor for each db
        But it will not be used in situations, for example, with RETURNING or lastrowid
        """
        # print(f"DEBUG: self.db type: {type(self.db)}")
        if self.db_type == 'mysql':
            return self.db.cursor()
        else:
            return self.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
