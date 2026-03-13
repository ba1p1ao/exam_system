# 让 pymysql 以 mysqlDB 的方式来对接 ORM
from pymysql import install_as_MySQLdb
install_as_MySQLdb()