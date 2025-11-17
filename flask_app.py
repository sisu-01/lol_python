# app_flask.py
import os
from api.api import create_app
from logger.logger import init_logger
from flask import got_request_exception
from flask_cors import CORS
from config import CORS_ORIGINS

logger = init_logger()
app = create_app()

CORS(app, origins=CORS_ORIGINS)

def log_flask_exceptions(sender, exception, **extra):
  logger.critical(f"Flask exception: {exception}", exc_info=True)

got_request_exception.connect(log_flask_exceptions, app)

if __name__ == "__main__":
  logger.info('lol-python Flask start')
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=False)