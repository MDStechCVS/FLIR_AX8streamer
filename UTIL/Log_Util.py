import logging
from datetime import datetime
import os 



def Init_Logger():
    now = datetime.now()
    YM = now.strftime('%Y_%m')
    YMD = now.strftime('%Y_%m_%d')
    log_dir_path = f'./log/{YM}'

    if not os.path.exists(f'{log_dir_path}'):
        os.makedirs(f'{log_dir_path}')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 로거 생성 및 설정
    logger = logging.getLogger('TRACE')
    logger.setLevel(logging.INFO)
    file_handler1 = logging.FileHandler(f'{log_dir_path}/{YMD}.txt')
    file_handler1.setFormatter(formatter)
    logger.addHandler(file_handler1)

    debug = logging.getLogger('DEBUG')
    debug.setLevel(logging.INFO)
    file_handler2 = logging.FileHandler(f'{log_dir_path}/{YMD}_debug.txt')
    file_handler2.setFormatter(formatter)
    debug.addHandler(file_handler2)

