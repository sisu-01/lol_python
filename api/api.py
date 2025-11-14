# api/api.py
import logging
from flask import Flask, jsonify
from db.redis_client import RedisClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

def create_app():
  app = Flask(__name__)
  redis_client = RedisClient()

  @app.route('/matchups', methods=['GET'])
  def get_random_matchups():
    try:
      keys, keys_len = redis_client.getAllKeys()
      if not keys:
        return jsonify({"error": "No matchups found"}), 404
      values = redis_client.getKeyValue(keys)
      if not values:
        return jsonify({"error": "No matchups found"}), 404
      result = [f"{k}:{v}" for k, v in zip(keys, values)]
      return jsonify({
        'lens': keys_len,
        'datas': result,
      })
    except Exception as e:
      logger.critical(f"API /matchups error: {e}", exc_info=True)
      return jsonify({"error": "Unexpected server error"}), 500
    
  return app