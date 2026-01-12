# scraper_app.py
import time
from logger.logger import init_logger
from scraping.scraping import main as run_scraping

logger = init_logger('scraper')

def start_scraping():
  while True:
    try:
      run_scraping()
      break
    except Exception as e:
      logger.critical(f"Scraper error: {e}", exc_info=True)
      time.sleep(5)

if __name__ == "__main__":
  logger.info('Scraper start')
  start_scraping()