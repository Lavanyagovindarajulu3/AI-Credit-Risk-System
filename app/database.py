import MySQLdb
from MySQLdb.cursors import DictCursor


def get_db_connection():
    """
    Create and return a MySQL database connection.
    """

    return MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="Lavanya@39.",
        database="credit_risk",
        cursorclass=DictCursor
    )


def execute_query(query, params=None, fetch=False, many=False):
    """
    Execute a MySQL query safely using parameterized SQL.

    Args:
        query: SQL query string.
        params: Query parameters.
        fetch: Whether to return selected rows.
        many: Whether executemany should be used.

    Returns:
        Selected rows when fetch=True.
        Last inserted ID for INSERT operations.
        Otherwise True.
    """

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        # Because get_db_connection() uses DictCursor,
        # SELECT results will be dictionaries.
        cursor = connection.cursor()

        if many:

            cursor.executemany(
                query,
                params or []
            )

        else:

            cursor.execute(
                query,
                params or ()
            )

        # SELECT query
        if fetch:

            result = cursor.fetchall()

            return result

        # INSERT / UPDATE / DELETE
        connection.commit()

        # Return inserted ID for INSERT
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
    """
    Fetch one record from the database.

    Returns:
        Dictionary containing one record,
        or None if no record exists.
    """

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            query,
            params or ()
        )

        return cursor.fetchone()

    except MySQLdb.Error:

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


def fetch_all(query, params=None):
    """
    Fetch multiple records from the database.

    Returns:
        List of dictionaries.
    """

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            query,
            params or ()
        )

        return cursor.fetchall()

    except MySQLdb.Error:

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()