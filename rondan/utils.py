import requests,json
import time
import re
from kanaconv import KanaConv
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from requests.exceptions import Timeout, SSLError

ENCODING = "utf-8"
PARSER = "html.parser"

TIMEOUT = 10
RETRY = 10

YEAR_REGEX = r', [0-9]{4}.*'

def similar(a, b):
    seq = SequenceMatcher(a=a.replace(" ","").replace(",","").lower(),b=b.replace(" ","").replace(",","").lower())
    return seq.ratio()

def get_url_as_soup(url, encoding=ENCODING, parser=PARSER):
    retry = True
    while retry:
        try:
            r = requests.get(url, timeout=TIMEOUT)
            retry = False
        except Timeout:
            print(" ... retry")
            time.sleep(RETRY)
            continue
  
    return BeautifulSoup(r.content.decode(encoding), parser)

def get_url_as_json(url):
    retry = True
    while retry:
        try:
            r = requests.get(url)
            retry = False
            return r.json()
        except:
            print(" ... retry")
            time.sleep(RETRY)
            continue

def cap_first_letters(st):
    st = st.title()
    # create character list
    new_st = list(st)
    # look up positions of ' character in string
    positions = [m.start() for m in re.finditer("'", st)]
    # lower the character after ' in string list
    for position in positions:
        if position < len(st):
            new_st[position+1] = new_st[position+1].lower()
    # convert list to string and return string
    return "".join(new_st).strip()

def remove_years(label):
    label = re.sub(YEAR_REGEX, "", label)
    return label.strip()

def kana_to_romaji(st):
    conv = KanaConv()
    romanji = conv.to_romaji(st)
    return romanji.strip()