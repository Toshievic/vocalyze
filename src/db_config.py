import os
import psycopg2
from dotenv import load_dotenv


def get_db_connection():
    # .envファイルを読み込む
    load_dotenv()

    # 環境変数からデータベース接続情報を取得
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    
    db_name = db_name
    db_user = db_user
    db_password = db_password
    db_host = db_host
    db_port = db_port

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    return conn
