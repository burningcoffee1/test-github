# 系统库
import time
# 第三方库
import pymysql

from .logger import log_decorator

config_db = {
    'DATABASE_HOST' : '43.142.181.55',
    'DATABASE_PORT' : 3306,
    'DATABASE_USER' : 'shengjm',
    'DATABASE_PASSWORD' : 'abcd1234',
    'DATABASE_NAME' : 'house_data_db'
}

class MySQLDatabase:
    """
    数据库操作类。
    """
    def __init__(self, max_retries=30):
        self.host = config_db['DATABASE_HOST']
        self.user =  config_db['DATABASE_USER']
        self.password = config_db['DATABASE_PASSWORD']
        self.database =  config_db['DATABASE_NAME']
        self.connection = None
        self.cursor = None
        self.max_retries = max_retries
        self.connect()
        
    @log_decorator
    def connect(self):
        for retry in range(self.max_retries):
            try:
                self.connection = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=True
                )
                self.cursor = self.connection.cursor()  # 获取游标
                # logger.log_info("数据库连接成功")
                break
            except pymysql.Error:
                if retry < self.max_retries - 1:
                    time.sleep(30)
                else:
                    raise

    @log_decorator
    def insert(self, table, data):
        """向指定表插入单条数据"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        with self.connection.cursor() as cursor:
            cursor.execute(sql, list(data.values()))
            self.connection.commit()

    @log_decorator
    def insert_many(self, table, data_list):
        """
        向指定表批量插入多条数据
        :param table: 表名
        :param data_list: 包含多个字典的列表，每个字典代表一条记录
        """
        if not data_list:
            return
        
        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['%s'] * len(data_list[0]))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        values_list = [tuple(data.values()) for data in data_list]
        
        with self.connection.cursor() as cursor:
            cursor.executemany(sql, values_list)
            self.connection.commit()

    @log_decorator
    def insert_data(self, table_name, data):
        if not data:  # 检查是否是空字典
            return  # 跳过空字典
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = tuple(data.values())
        sql = f"REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            self.cursor.execute(sql, values)
            self.connection.commit()
        except Exception:
            self.connection.rollback()

    @log_decorator
    def insert_data_list(self, table_name, data_list):
        try:
            for data in data_list:
                if not data:  # 检查是否是空字典
                    continue  # 跳过空字典
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                values = tuple(data.values())
                sql = f"REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
                self.cursor.execute(sql, values)
            self.connection.commit()
        except Exception:
            self.connection.rollback()

    @log_decorator
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def __del__(self):
        self.disconnect()

if __name__ == "__main__":
    db = MySQLDatabase()
    db.insert_data('house_data', {'id': 1, 'name': 'test'})
    db.disconnect()
    