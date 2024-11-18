import psycopg2

def get_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="jobfinder",
            user="postgres",
            password="Luudinhkien_2003"
        )
        return connection
    except Exception as e:
        print("Database connection error:", e)
        return None
