import pymysql
import config
from tools import logger

class Mysql:
    def __init__(self):
        self.host = config.MYSQL_HOST
        self.port = config.MYSQL_PORT
        self.user = config.MYSQL_USER
        self.password = config.MYSQL_PASSWORD
        self.database = config.MYSQL_DATABASE
        self.connection = None
        self.cursor = None

    def __enter__(self):  # 支持 with 语句
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # 支持 with 语句
        self.close()

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
        except pymysql.MySQLError as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise Exception("Failed to connect to the database.")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute(self, query, params=None):
        """Execute a query with optional parameters"""
        try:
            with self.connection.cursor() as cursor:  # 使用游标上下文管理器
                cursor.execute(query, params)
                result = cursor.fetchall()
                self.connection.commit()
                return result
        except pymysql.MySQLError as e:
            self.connection.rollback()
            logger.error(f"Error executing query: {e}")
            raise

    def read(self, table, columns: list = None, condition=None, condition_params=None):
        """Read records from a table with optional columns and condition"""
        try:
            # logger.debug(columns)
            if columns is not None:
                columns_str = ", ".join([f"`{col}`" for col in columns])
            else:
                columns_str = '*'
            
            sql = f"SELECT {columns_str} FROM `{table}`"
            
            if condition:
                sql += f" WHERE {condition}"
            
            with self.connection.cursor() as cursor:
                cursor.execute(sql, condition_params)  # 使用参数化防止SQL注入
                result = cursor.fetchall()
                return result
        except pymysql.MySQLError as e:
            logger.error(f"Error while reading records: {e}")
            return None
