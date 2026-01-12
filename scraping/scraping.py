# scraping.scraping.py
from config import HEADERS, OPGG_POSITIONS, OPGG_TIER, OPGG_REGION
from db.redis_client import RedisClient
from bs4 import BeautifulSoup
import requests
import logging
import time
import re

logger = logging.getLogger(__name__)

def get_html(url):
  for _ in range(3):  # 최대 3번 재시도
    try:
      time.sleep(1)
      response = requests.get(url, headers=HEADERS, timeout=10)
      response.raise_for_status()
      return response.text
    except:
      time.sleep(10)
  logger.error(f"scraping.py get_html {url} 3 times failed")
  return ""

def get_json(url):
  for _ in range(3):  # 최대 3번 재시도
    try:
      time.sleep(1)
      response = requests.get(url, headers=HEADERS, timeout=10)
      response.raise_for_status()
      return response.json()
    except:
      time.sleep(10)
  logger.error(f"scraping.py get_json {url} 3 times failed")
  return {}

def get_matchCount_and_check_opgg_update_time():
  """
    OP.GG의 최근 업데이트와 총 표본 수를 return 한다.
  """
  html =  get_html(f'https://op.gg/ko/lol/champions?region={OPGG_REGION}&tier={OPGG_TIER}')
  pattern = r'\{\\"analyzedAt\\"\s*:\s*\\"([^"]+)\\",\s*\\"matchCount\\"\s*:\s*(\d+)\}'
  match = re.search(pattern, html)
  if match:
    return match.group(1), match.group(2)
  else:
    return None, 0

def get_dataDragon_chmpJson_and_visited():
  try:
    version = get_json('https://ddragon.leagueoflegends.com/api/versions.json')[0]
    champion_json = get_json(f'https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/champion.json')
    chmp_json = dict()
    initVisited = dict()
    for eng_name, champ_data in champion_json["data"].items():
      kor_name = champ_data["name"]
      chmp_json[kor_name] = {
          "eng": eng_name,
          "key": champ_data["key"]
      }
      initVisited[kor_name] = False
    return chmp_json, initVisited
  except Exception as e:
    logger.critical(f"get_dataDragon error: {e}", exc_info=True)
    return {}, {}
  
def get_champions_list_by_position(position, tier, region):
  """
  position 별 챔피언 목록 return.
  """
  try:
    url = f'https://op.gg/ko/lol/champions?position={position}&tier={tier}&region={region}'
    html = get_html(url)
    soup_list = BeautifulSoup(html, 'html.parser').select('tbody > tr')
    chmp_list = list()
    for soup in soup_list:
      if soup.get('class') is None:
        td = soup.select_one('td:nth-of-type(2)')
        chmp_name = td.div.a.strong.get_text(strip=True)
        chmp_list.append(chmp_name)
    return chmp_list
  except Exception as e:
    logger.critical(f"scraping.py get_champions_list_by_position error: {e}", exc_info=True)
    return None

def get_matchup_list(dataDragon_chmp_json, visited, chmp, position, tier, region):
  """
  특정 챔피언의 카운터 목록 key value 반환

  Return:
    keys: {position:A_id:B_id}
    values: {A_win:B_win:count}
  """
  try:
    visited[chmp] = True
    # print(chmp)
    url = f'https://op.gg/ko/lol/champions/{dataDragon_chmp_json[chmp]['eng']}/counters/{position}?tier={tier}&region={region}'
    html = get_html(url)
    soup_list = BeautifulSoup(html, 'html.parser').select('aside > div > div:nth-of-type(2) > ul > li')
    keys = list()
    values = list()
    for soup in soup_list:
      _, tempA, tempB, tempC = soup.find_all("div", recursive=False)
      name = tempA.span.get_text(strip=True)
      winRate = float(tempB.strong.get_text(strip=True)[:-1])
      count = re.sub(r'\D', '', tempC.span.get_text(strip=True))
      if visited[name]:
        continue
      # print(f'\tvs {name}({dataDragon_chmp_json[name]['eng']} {dataDragon_chmp_json[name]['key']}) ')
      temp_keys, temp_values = make_keys_and_values(dataDragon_chmp_json, position, chmp, name, winRate, count)
      keys.append(temp_keys)
      values.append(temp_values)
    return keys, values
  except Exception as e:
    logger.critical(f"scraping.py get_matchup_list error: {e}", exc_info=True)
    return None

def make_keys_and_values(chmp_json, position, chmpA, chmpB, AwinRate, count):
  try:
    BwinRate = round(100-AwinRate, 2)
    if chmpA < chmpB:
      left = chmpA
      right = chmpB
      leftWinRate = AwinRate
      rightWinRate = BwinRate
    else:
      left = chmpB
      right = chmpA
      leftWinRate = BwinRate
      rightWinRate = AwinRate
    # key = f'{position}:{left}:{chmp_json[left]['key']}:{right}:{chmp_json[right]['key']}'
    # value = f'{position}:{left}:{right}:{leftWinRate}:{rightWinRate}:{count}'
    key = f'{position}:{chmp_json[left]['key']}:{chmp_json[right]['key']}'
    value = f'{leftWinRate}:{rightWinRate}:{count}'
    return key, value
  except Exception as e:
    logger.critical(f"scraping.py make_keys_and_values error: {e}", exc_info=True)
    return None, None

def run(dataDragon_chmp_json, initVisited):
  try:
    logger.info(f"scraping.py scrap start")
    key_sets = dict()
    matchups = list()
    for position in OPGG_POSITIONS:
      key_sets[position] = list()
      chmp_list = get_champions_list_by_position(position, OPGG_TIER, OPGG_REGION)
      visited = initVisited.copy()
      for chmp in chmp_list:
        keys, values = get_matchup_list(dataDragon_chmp_json, visited, chmp, position, OPGG_TIER, OPGG_REGION)
        key_sets[position].extend(keys)
        matchups.extend(values)
    redis_client = RedisClient()
    redis_client.setKeyAndValue(key_sets, matchups)
    logger.info(f"scraping.py scrap complete, matchups len: {len(matchups)}")
  except Exception as e:
    logger.critical(f"scraping.py run error: {e}", exc_info=True)

def main():
  dataDragon_chmp_json , initVisited = get_dataDragon_chmpJson_and_visited()
  last_update_time = ''
  while True:
    update_time, matchCount = get_matchCount_and_check_opgg_update_time()
    logger.info(f'last_update_time: {last_update_time}, update_time: {update_time}')
    if update_time is None:
      time.sleep(600)
      continue
    if last_update_time != update_time:
      logger.info(f'{last_update_time} != {update_time}다르다 간다.')
      last_update_time = update_time
      run(dataDragon_chmp_json, initVisited)
    else:
      logger.info(f'에잉 똑같네..')
    time.sleep(600)