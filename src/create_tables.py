from logger import get_custom_logger
from db_config import get_db_connection

import os


def main():
    # テーブル作成を行うクエリファイル
    sql_file_path = os.path.join(os.getcwd(), "src", "queries", "create_tables.sql")
    logger = get_custom_logger()

    # PostgreSQLに接続
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        logger.info("Successfully connected to the DB.")

    except Exception as e:
        logger.error("Failed to connected to the DB.")
        raise

    with open(sql_file_path, 'r') as sql_file:
        sql_script = sql_file.read()

    for statement in sql_script.split(';'):
        statement = statement.strip()
        if statement:  
            cur.execute(statement)

    conn.commit()
    logger.info("Successfully executed the query file.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
