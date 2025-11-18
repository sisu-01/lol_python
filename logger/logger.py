import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def init_logger(prefix):
  log_dir = "logs"
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)

  log_file = os.path.join(log_dir, f"{prefix}_app.log")

  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  if logger.hasHandlers():
    return logger

  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setLevel(logging.INFO)
  console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
  console_handler.setFormatter(console_formatter)
  logger.addHandler(console_handler)

  file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,           # 이전 로그 5개까지 저장
    encoding="utf-8"
  )
  file_handler.setLevel(logging.INFO)
  file_handler.setFormatter(console_formatter)
  logger.addHandler(file_handler)

  logger.info("Logger init complete")
  return logger