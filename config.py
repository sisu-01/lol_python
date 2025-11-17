import os
from dotenv import load_dotenv

env_file = os.environ.get("ENV", ".env")
load_dotenv(env_file)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

OPGG_POSITIONS = ['top', 'jungle', 'mid', 'adc', 'support']
OPGG_TIER = 'emerald_plus'
OPGG_REGION = 'kr'

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173")

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = 0