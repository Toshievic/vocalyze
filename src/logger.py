import logging
import os
from datetime import datetime


def get_custom_logger(file: bool = True, console: bool = True):
    # ログの設定
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # フォーマットの設定
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    if file:
        # ファイルハンドラ
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(os.getcwd(), "logs")
        if not os.path.isdir(file_path): os.makedirs(file_path)
        file_handler = logging.FileHandler(os.path.join(file_path, f'collector_{timestamp}.log'))
        file_handler.setLevel(logging.DEBUG)  # ファイルにはDEBUG以上を記録
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
    
    if console:
        # コンソールハンドラ
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # コンソールにはINFO以上を表示
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger
