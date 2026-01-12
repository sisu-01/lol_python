# db/redis_client.py
import time
import logging
import redis
from itertools import chain
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, OPGG_POSITIONS

logger = logging.getLogger(__name__)

class RedisClient():
  _instance = None

  def __new__(cls):
    try:
      if cls._instance == None:
        cls._instance = super().__new__(cls)
        cls._instance.r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
      return cls._instance
    except Exception as e:
      logger.critical(f"redis.py __new__ error: {e}", exc_info=True)

  def setKeyAndValue(self, keys, values):
    try:
      pipe = self.r.pipeline()
      for position in OPGG_POSITIONS:
        pipe.sadd(position, *keys[position])
        # *: unpacking, 리스트를 각 요소로 개별 인자 전달.
        # sadd: SADD key member sets에 하는거임 
      all_keys = chain.from_iterable(keys[pos] for pos in OPGG_POSITIONS)
      # keys = {"top": ["k1", "k2"],"jungle": ["k3"]} -> ["k1", "k2", "k3"]
      pipe.mset(dict(zip(all_keys, values)))
      # zip으로 key value 1:1 묶은 뒤 dict로 변환
      pipe.execute()
    except Exception as e:
      logger.critical(f"redis.py setKeyAndValue error: {e}", exc_info=True)

  # def getKeys(self, name):
  #   try:
  #     if name == 'all':
  #       pipe = self.r.pipeline()
  #       for position in OPGG_POSITIONS:
  #         pipe.smembers(position)
  #       result = pipe.execute()
  #       ordered_keys = []
  #       for r in result:
  #         ordered_keys.extend(r)
  #       return ordered_keys
  #     else:
  #       return list(self.r.smembers(name))
  #   except Exception as e:
  #     logger.critical(f"redis.py getRandomKeys error: {e}", exc_info=True)
  #     return None
  
  def getAllKeys(self):
    try:
      pipe = self.r.pipeline()
      for position in OPGG_POSITIONS:
        pipe.smembers(position)
      result = pipe.execute()
      ordered_keys = []
      keys_len = []
      for r in result:
        ordered_keys.extend(r)
        keys_len.append(len(r))
      return ordered_keys, keys_len
    except Exception as e:
      logger.critical(f"redis.py getRandomKeys error: {e}", exc_info=True)
      return None

  def getKeyValue(self, keys):
    try:
      return self.r.mget(keys)
    except Exception as e:
      logger.critical(f"redis.py getKeyValue error: {e}", exc_info=True)
      return None

  def setUpdateTime(self):
    try:
      self.r.set("last_update_time", int(time.time()))
    except Exception as e:
      logger.critical(f"redis.py setUpdateTime error: {e}", exc_info=True)

  def getUpdateTime(self):
    try:
      value = self.r.get("last_update_time")
      return int(value) if value is not None else None
    except Exception as e:
      logger.critical(f"redis.py getUpdateTime error: {e}", exc_info=True)
      return None