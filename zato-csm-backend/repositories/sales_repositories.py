from fastapi import HTTPException
from typing import List, Optional

import pymysql
import psycopg2.extras
# from repositories.base_repository import BaseRepository
#
# class SalesRepository(BaseRepository):
#     def create_sale(self):
