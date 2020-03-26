# -- coding: utf-8 --

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
from MySQLdb._exceptions import DatabaseError

from TLPLibrary.core import Config
from TLPLibrary.error import DataBaseException

class Mysql(object):

    __pool = None

    def __init__(self):
        self._conn = Mysql.__getConnection()
        self._cursor = self._conn.cursor()

    @staticmethod
    def __getConnection():
        '''
        @description:
        @param {type}
        @return:
        '''
        if Mysql.__pool is None:
            config = Config()
            Mysql.__pool = PooledDB(
                creator=MySQLdb,
                mincached=config.database_mincached,
                maxcached=config.database_maxcached,
                maxshared=config.database_maxshared,
                maxconnections=config.database_maxconnections,
                host=config.mysql_host,
                port=config.mysql_port,
                user=config.mysql_user,
                passwd=config.mysql_pwd,
                db=config.database_name,
                use_unicode=False,
                charset='utf8',
                cursorclass=DictCursor
            )#config.database_charset

        # print("MYSQL Manger ID: %d." % id(MysqlManager.__pool))

        return Mysql.__pool.connection()


    def selectOne(self, sql, parameter=None):
        '''查询单条记录，如果查询结果返回多条，也只会取第一条结果返回

        Args:
            sql (str): 要执行的SQL语句
            parameter (tuple): 拼接在SQL语句中的参数元组，可以不传.

        Returns (tuple):
            结果的元组，2个元素，1为查询结果的count数量，2为结果的dict.
        '''
        try:
            if parameter is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, parameter)

            if count > 0:
                result = self._cursor.fetchone()
            else:
                result = False

            return (count, result)
        except Exception as e:
            print ('Error : {}'.format(e))
            self._conn.rollback()
            raise DataBaseException(message=("select one data from database error, error sql:\n {}.".format(sql)))


    def selectAll(self, sql, parameter=None):
        '''
        @description:批量查询所有符合条件的内容。
        @param {string} sql:要执行的SQL语句
        @param {tuple} parameter:要替换到SQL语句中的占位符中的参数，会按索引进行替换
        @return: {tuple}: (查询的总条目数, 查询的结果，如果查询的结果集为空，则返回False)
        '''
        try:
            if parameter is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, parameter)

            if count > 0:
                result = self._cursor.fetchall()
            else:
                result = False

            return (count, result)
        except Exception as e:
            print ('Error : {}'.format(e))
            self._conn.rollback()
            raise DataBaseException(message=("select all data from database error, error sql:\n %s."%(sql)))


    def selectMany(self, sql, number, parameter=None):
        '''
        @description:查询指定数量的数据集结果
        @param {string} sql:要执行的SQL语句
        @param {int} number:要查询的条数
        @param {tuple} parameter:要替换到SQL语句中的占位符中的参数，会按索引进行替换
        @return: {tuple}: (查询的总条目数, 查询的结果，如果查询的结果集为空，则返回False)
        '''
        try:
            if parameter is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, parameter)

            if count > 0:
                result = self._cursor.fetchmany(number)
            else:
                result = False

            return (count, result)
        except Exception as e:
            print ('Error : {}'.format(e))
            self._conn.rollback()
            raise DataBaseException(message=("insert one data to database error, error sql:\n %s."%(sql)))


    def insertOne(self, sql, value):
        '''
        @description:单条插入数据
        @param {string} sql:插入的SQL语句
        @param {tuple} value：插入语句的值
        @return:数据库的变化结果数量
        '''
        try:
            result = self._cursor.execute(sql,value)
            self._conn.commit()
            return result
        except Exception as e:
            print ('Error : {}'.format(e))
            self._conn.rollback()
            raise DataBaseException(message=("insert one data to database error, error sql:\n %s."%(sql)))


    def insertMany(self, sql, values):
        '''
        @description:批量插入数据
        c.executemany("""INSERT INTO breakfast (name, spam, eggs, sausage, price) VALUES (%s, %s, %s, %s, %s)""",
        [
        ("Spam and Sausage Lover's Plate", 5, 1, 8, 7.95 ),
        ("Not So Much Spam Plate", 3, 2, 0, 3.95 ),
        ("Don't Wany ANY SPAM! Plate", 0, 4, 3, 5.95 )
        ])
        @param {string} sql:插入的SQL语句
        @param {array} values：数组，每个元素为tuple,tuple的每个元素为要插入的值
        @return:数据库的变化结果数量
        '''
        try:
            result = self._cursor.executemany(sql, values)
            self._conn.commit()

            return result
        except DatabaseError as e:
            # print ('Error : {}'.format(e))
            self._conn.rollback()
            raise DataBaseException(message=("insert many data to database error, error sql:\n %s."%(sql)))

    def close_transaction_insert_many(self, sql, values):
        try:
            result = self._cursor.executemany(sql, values)
            return result
        except DatabaseError as e:
            # print ('Error : {}'.format(e))
            self._conn.rollback()
            raise DataBaseException(message=("insert many data to database error, error sql:\n %s."%(sql)))


    def __query(self, sql, auto_commit, parameter=None):
        '''
        @description:执行非select的语句
        @param {string} sql:需要执行的SQL
        @param {tuple} parameter:要替换到SQL语句中的占位符中的参数，会按索引进行替换
        @return:数据库的变化结果数量
        '''
        count = 0
        try:
            if parameter is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, parameter)

            if auto_commit:
                self._conn.commit()

            return count
        except Exception as e:
            print ('Error : {}'.format(e))
            self._conn.rollback()
            raise DataBaseException(message=("execute sql error, error message, error sql:\n %s."%(sql)))


    def update(self, sql, parameter=None, auto_commit=True):
        '''
        @description:更新数据
        @param {string} sql:需要执行的SQL
        @param {tuple} parameter:要替换到SQL语句中的占位符中的参数，会按索引进行替换
        @return:数据库的变化结果数量
        '''
        return self.__query(sql, auto_commit, parameter)


    def delete(self, sql, parameter=None, auto_commit=True):
        '''
        @description:删除数据
        @param {string} sql:需要执行的SQL
        @param {tuple} parameter:要替换到SQL语句中的占位符中的参数，会按索引进行替换
        @return:数据库的变化结果数量
        '''
        return self.__query(sql, auto_commit, parameter)

    def begin(self):
        '''
        @description:开启事务
        '''
        self._conn.autocommit(0)

    def end(self, commit=True):
        '''
        @description:结束事务
        @param commit {boolean}:True表示提交事务，False表示回滚事务，默认为提交
        '''
        if commit:
            self._conn.commit()
        else:
            self._conn.rollback()

    def destory(self, is_end=True):
        '''
        @description:关闭游标及连接
        '''
        self.end(commit=is_end)

        self._cursor.close()
        self._conn.close()
