
import MySQLdb
from MySQLdb.cursors import DictCursor
from config import Config


def get_db_connection():
    """Create a secure connection to the configured MySQL-compatible database."""

    ssl_options = {}

    if Config.MYSQL_SSL_CA:
        ssl_options["ca"] = Config.MYSQL_SSL_CA

    connection_options = {
        "host": Config.MYSQL_HOST,
        "port": Config.MYSQL_PORT,
        "user": Config.MYSQL_USER,
        "passwd": Config.MYSQL_PASSWORD,
        "db": Config.MYSQL_DB,
        "cursorclass": DictCursor,
        "connect_timeout": 15,
    }

    if ssl_options:
        connection_options["ssl"] = ssl_options

    return MySQLdb.connect(**connection_options)


def execute_query(query, params=None, fetch=False, many=False):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if many:
            cursor.executemany(query, params or [])
        else:
            cursor.execute(query, params or ())

        if fetch:
            return cursor.fetchall()

        connection.commit()

        if query.strip().upper().startswith("INSERT"):
            return cursor.lastrowid

        return True

    except MySQLdb.Error:
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_one(query, params=None):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_all(query, params=None):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
