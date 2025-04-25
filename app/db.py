# app/db.py
import mysql.connector
import app.db_config as cfg

def get_connection():
    return mysql.connector.connect(
        host=cfg.DB_HOST,
        user=cfg.DB_USER,
        password=cfg.DB_PASS,
        database=cfg.DB_NAME
    )

def run_query(query, params=None, fetch=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    if fetch:
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    conn.commit()
    cursor.close()
    conn.close()
