import requests,json
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

ENCODING = "utf-8"
PARSER = "html.parser"

def similar(a, b):
    seq = SequenceMatcher(a=a.replace(" ","").replace(",","").lower(),b=b.replace(" ","").replace(",","").lower())
    return seq.ratio()

def getUrlAsSoup(url, encoding=ENCODING, parser=PARSER):
    r = requests.get(url)
    return BeautifulSoup(r.content.decode(encoding), parser)

def getUrlAsJson(url):
    r = requests.get(url)
    return r.json()