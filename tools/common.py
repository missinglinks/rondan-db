import requests,json
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

ENCODING = "utf-8"

def similar(a, b):
    seq = SequenceMatcher(a=a.replace(" ","").replace(",","").lower(),b=b.replace(" ","").replace(",","").lower())
    return seq.ratio()

def getUrlAsSoup(url, encoding=ENCODING):
    r = requests.get(url)
    return BeautifulSoup(r.content.decode(encoding), "html.parser")

def getUrlAsJson(url):
    r = requests.get(url)
    return r.json()