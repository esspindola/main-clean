import pymysql
import psycopg2.extras

class BaseRepository:
    def __init__(self, db, db_type='postgres'):
        self.db = db
        self.db_type = db_type

    def _get_cursor(self):
        """
        Return appropriate cursor for each db
        But it will not be used in situations, for example, with RETURNING or lastrowid
        """
        if self.db_type == 'mysql':
            return self.db.cursor()
        else:
            return self.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
