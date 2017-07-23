# -*- coding: utf-8 -*-

import urllib
from bs4 import BeautifulSoup

class KotobankPersonHelper:

    def __init__(self, name):
        self.name = name
        self.url = 'https://kotobank.jp/word/' + urllib.parse.quote(name) + '?dic=nihonjinmei'
        self.entries = []

        self.birth = 0
        self.death = 0

        self.realName = None
        self.entryCount = 0


            ## URL ERROR ABRAGE UEBERARBEITEN!!!!!
        print("checking for dictionary entries ...")
        try:
            xfile = urllib.request.urlopen(self.url)
        except:
            print ("URL Error")
            return None

        data = xfile.read().decode("utf-8")
        xfile.close()

        soup = BeautifulSoup(data, "lxml")
        articles = soup.findAll('article')
        yearsbd = None
        for article in articles:
            dic = article.find('h2').text
            years = article.find('yearsbd')
            if years != None:
                yearsbd = years.text
            text = article.find('section').text
            self.entries.append({'dictionary': dic,
                                'entry': text,
                                'link': self.url})

            if u"→" in text[0:5]:
                self.realName = text.split(u"→")[1].replace(" ","")
            self.entryCount += 1

        if yearsbd is not None:
            tmp = yearsbd.replace(u"*","").replace(u"(","").replace(u")","")
            tmp = tmp.split(u"－")
            if len(tmp) > 0:
                try:
                    self.birth = int(tmp[0])
                except:
                    pass
            if len(tmp) > 1:
                try:
                    self.death = int(tmp[1])
                except:
                    pass

        print(str(self.entryCount)+" entries found")