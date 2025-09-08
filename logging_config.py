# logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler

current_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(current_directory, 'api.log')
error_log_file_path = os.path.join(current_directory, 'errors.log')

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

info_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=3)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

error_handler = RotatingFileHandler(error_log_file_path, maxBytes=5*1024*1024, backupCount=3)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger('my_api_logger')
logger.setLevel(logging.DEBUG)
logger.addHandler(info_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)


