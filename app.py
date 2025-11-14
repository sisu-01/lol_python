# app.py
import sys
import time
import threading

from flask import got_request_exception
from api.api import create_app
from logger.logger import init_logger
from scraping.scraping import main as run_scraping


logger = init_logger()

def start_scraping():
  while True:
    try:
      run_scraping()
      break
    except Exception as e:
      logger.critical(f"start_scraping error: {e}", exc_info=True)
      time.sleep(5)

scraping_thread = threading.Thread(target=start_scraping, daemon=True)
scraping_thread.start()

app = create_app()

def log_flask_exceptions(sender, exception, **extra):
  logger.critical(f"Flask exception: {exception}", exc_info=True)
got_request_exception.connect(log_flask_exceptions, app)

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
  if issubclass(exc_type, KeyboardInterrupt):
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    return
  logger.critical('main thread exception', exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_uncaught_exception

if __name__ == "__main__":
  logger.info('lol-python start')
  app.run(host='0.0.0.0', port=5000, debug=False)