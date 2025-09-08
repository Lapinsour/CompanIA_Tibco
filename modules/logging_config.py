# logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler

# Remonter à la racine du projet (un niveau au-dessus de ce fichier)
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, os.pardir))  # ../

# Chemin vers le dossier logs à la racine
log_directory = os.path.join(project_root, 'logs')
os.makedirs(log_directory, exist_ok=True)

# Chemins vers les fichiers de log
log_file_path = os.path.join(log_directory, 'api.log')
error_log_file_path = os.path.join(log_directory, 'errors.log')

# Formatter
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# Handlers
info_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=3)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

error_handler = RotatingFileHandler(error_log_file_path, maxBytes=5*1024*1024, backupCount=3)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Logger
logger = logging.getLogger('my_api_logger')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
