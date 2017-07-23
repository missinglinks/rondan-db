# -*- coding: utf-8 -*-
from persondataminer import PersonDataminer
from rondandatabase import RondanDatabaseHelper
from bs4 import BeautifulSoup
from persondataminer import getUrlDataAsString
from urllib import request


xfile = request.urlopen('https://viaf.org/viaf/search?query=local.personalNames+all+"'+request.quote("中村雄二郎")+'"')
data = xfile.read().decode("utf-8")
soup = BeautifulSoup(data,"xml")
viaf = soup.find_all("viafID")
test = data
print(viaf)
