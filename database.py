import psycopg2
import os

backend_ip = os.getenv("BACKEND_IP")
database = os.getenv("DB")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")


def get_connection():
    try:
        connection = psycopg2.connect(database=database,
                              user=db_user,
                              host=backend_ip,
                              password=db_password,
                              port=db_port)
        return connection
    except Exception as e:
        print("Database connection error:", e)
        return None
