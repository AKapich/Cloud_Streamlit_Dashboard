import psycopg2
from dotenv import load_dotenv
import os
import pandas as pd


load_dotenv()
db_password = os.getenv("DB_PASSWORD")
cloud_sql_connection_name = os.getenv("DB_CONNECTION_NAME")
db_host = os.getenv("DB_HOST")


def create_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password=db_password,
        # host=f"/cloudsql/{cloud_sql_connection_name}",
        host=db_host,
        port="5432",
    )
    return conn

if __name__ == "__main__":
    conn = create_connection()

    schedule = pd.read_sql("SELECT * FROM schedule", conn)

    schedule.to_csv("schedule.csv", index=False)
    conn.close()