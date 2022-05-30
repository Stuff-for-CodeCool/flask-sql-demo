from os import environ as env


def establish_connection(user, password, host, db):
    from psycopg2 import connect, DatabaseError

    try:
        connection = connect(f"postgres://{user}:{password}@{host}/{db}")
        connection.autocommit = True
        return connection

    except DatabaseError:
        raise RuntimeError("Could not connect to databse")


def query(statement, vars=None, single=False, debug=False):
    from psycopg2.extras import RealDictCursor as cursor_type
    from dotenv import load_dotenv

    load_dotenv()

    dbuser = env.get("DB_USER")
    dbpassword = env.get("DB_PASS")
    dbhost = env.get("DB_HOST")
    dbdb = env.get("DB_DB")

    with establish_connection(dbuser, dbpassword, dbhost, dbdb) as conn:
        with conn.cursor(cursor_factory=cursor_type) as cursor:
            cursor.execute(statement, vars)

            if debug:
                print(cursor.query.decode("utf-8"))
            
            if single:
                return cursor.fetchone()

            return cursor.fetchall()
