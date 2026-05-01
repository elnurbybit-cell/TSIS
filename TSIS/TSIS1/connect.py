from config import USE_DATABASE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def get_connection():
    if not USE_DATABASE:
        return None

    try:
        import psycopg2

        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        return connection

    except Exception as error:
        print("Database connection failed:", error)
        return None