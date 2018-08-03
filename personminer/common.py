import requests,json
import time
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from requests.exceptions import Timeout, SSLError

ENCODING = "utf-8"
PARSER = "html.parser"

TIMEOUT = 10
RETRY = 10

def similar(a, b):
    seq = SequenceMatcher(a=a.replace(" ","").replace(",","").lower(),b=b.replace(" ","").replace(",","").lower())
    return seq.ratio()

def getUrlAsSoup(url, encoding=ENCODING, parser=PARSER):
    retry = True
    while retry:
        try:
            r = requests.get(url, timeout=TIMEOUT)
            retry = False
        except Timeout:
            print(" ... retry")
            time.sleep(RETRY)
            continue
        # except SSLError:
        #     print(" ... retry")
        #     time.sleep(RETRY)
        #     continue            
    return BeautifulSoup(r.content.decode(encoding), parser)

def getUrlAsJson(url):
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