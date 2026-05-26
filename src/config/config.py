import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, '..', 'logs')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

load_dotenv(os.path.join(CONFIG_DIR, '.env'))

class Config:
    APP_NAME = "AutoOps - 自动化运维工具"
    APP_VERSION = "1.0.0"
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(LOG_DIR, 'autoops.log')
    
    DEFAULT_TIMEOUT = 30
    MAX_CONCURRENT_TASKS = 10
    
    SSH_PORT = int(os.getenv('SSH_PORT', 22))
    SSH_TIMEOUT = int(os.getenv('SSH_TIMEOUT', 10))
    
    THEME_COLOR = "#1E90FF"
    SUCCESS_COLOR = "#00CED1"
    ERROR_COLOR = "#DC143C"
    WARNING_COLOR = "#FFD700"
