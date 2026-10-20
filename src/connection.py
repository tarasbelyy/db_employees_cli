import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_conn():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )


def test_connection():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1;')
                return cur.fetchone()[0] == 1
    except psycopg2.Error:
        return False


if __name__ == '__main__':
    print(test_connection())
