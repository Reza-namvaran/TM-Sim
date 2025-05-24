import os
import logging

class Config:
    ALLOWED_EXTENSIONS = {'yml', 'yaml'}

    # Logging configuration
    LOG_LEVEL = logging.DEBUG if os.getenv('FLASK_DEBUG') else logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'turing_simulator.log'