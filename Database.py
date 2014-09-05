import MySQLdb
import Config

db = MySQLdb.connect( Config.DB_HOST, Config.DB_USER, Config.DB_PASS, Config.DB_NAME )