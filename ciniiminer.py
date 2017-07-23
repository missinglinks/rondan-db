# -*- coding: utf-8 -*-

import xml.etree.ElementTree as etree
import urllib
import codecs
from urllib import request
from rondandatabase import RondanDatabaseHelper
from persondataminer import getUrlDataAsString
from bs4 import BeautifulSoup


class CiniiDataminer:

    def __init__(self):
        self.articleList = []
        self.magazine = ""
        self.magazineISSN = ""
        self.publisher = ""

    def booksPerYear (self, publisher, start, end):
        csvfile = codecs.open('.\\' + publisher.decode('utf-8') + repr(start) + '-' + repr(end) + '.csv', 'w+', encoding="utf-8")
        csvfile.write(u'Year,' + publisher.decode('utf-8') + u'Shinsho,Bunko\n')

        publisher = urllib.request.quote(publisher)

        for year in range(start, end+1):
            url = 'http://ci.nii.ac.jp/books/opensearch/search?count=5000&publisher='+publisher+'&year_from='+repr(year)+'&year_to='+repr(year)+'&format=rss'
            data = getUrlDataAsString(url)

            try:
                doc = etree.parse(data.decode("utf-8"))
                root = doc.getroot()
                for child in root.iter('{http://a9.com/-/spec/opensearch/1.1/}totalResults'):
                    totalResults = int(child.text)
                    print(repr(year)+', '+ repr(totalResults))

                booksNumber = 0
                shinsho = 0
                bunko = 0

                for child in root.iter('{http://purl.org/rss/1.0/}item'):
                    booksNumber += 1
                    partof = child.findall('{http://purl.org/dc/terms/}isPartOf')
                    for part in partof:
                        if u'新書' in part.attrib['{http://purl.org/dc/elements/1.1/}title']:
                            shinsho += 1
                        if u'文庫' in part.attrib['{http://purl.org/dc/elements/1.1/}title']:
                            bunko += 1

            except etree.XMLSyntaxError:
                print('XML parsing error')

            csvfile.write(repr(year)+','+repr(totalResults)+','+repr(shinsho)+','+repr(bunko)+u'\n')

        csvfile.close()


    def getArticleDatasets(self, mag, pub, yearFrom, yearTo):
        self.magazine = mag
        self.publisher = pub
        maga = request.quote(mag)
        publi = request.quote(pub)
        url = 'http://ci.nii.ac.jp/opensearch/search?count=200&start=1&lang=ja&journal='+maga+\
              '&issn=&publisher='+publi+'&year_from='+repr(yearFrom)+'&year_to='+repr(yearTo)+\
              '&format=rss&appid=upmkTSWtpQK7f9LqGpTg'
        print(url)
        data = getUrlDataAsString(url)

        soup = BeautifulSoup(data, "xml")
        totalResults = int(soup.find("totalResults").text)
        print("Total Results: "+repr(totalResults))
        self.articleList = []
        print("Mine records ...")

        for offset in range(1, totalResults, 200):
            url = 'http://ci.nii.ac.jp/opensearch/search?count=200&start=' + repr(offset) + \
                  '&lang=ja&journal=' + repr(maga) + '&issn=&publisher=' + publi + \
                  '&year_from=' + repr(yearFrom) + '&year_to=' + repr(yearTo) + '&format=rss&appid=upmkTSWtpQK7f9LqGpTg'
            data = getUrlDataAsString(url)
            soup = BeautifulSoup(data, "xml")

            for item in soup.find_all("item"):
                pubName = item.find("publicationName")
                if pubName is not None:
                    if pubName.text.split(" ")[0].split(".")[0] == self.magazine or pubName.text.split(" ")[0].split(".")[0].replace("-","ー") == self.magazine:
                        title = item.find("title").text.replace("-","ー")
                        link = item.find("link").text
                        authors = item.find_all("creator")
                        date = item.find("publicationDate").text
                        vol = item.find("volume")
                        number = item.find("number")
                        pageFrom = item.find("startingPage")
                        pageUntil = item.find("endingPage")

                        if pageFrom == None:
                            pageFrom = ""
                        else:
                            pageFrom = pageFrom.text.replace("p", "")
                        if pageUntil == None:
                            pageUntil = ""
                        else:
                            pageUntil = pageUntil.text
                        if vol == None:
                            if number == None:
                                vol = ""
                            else:
                                vol = number.text
                        else:
                            if number != None:
                                vol = vol.text + "(" + number.text + ")"
                            else:
                                vol = vol.text

                        dates = date.split('-')
                        if len(dates) >= 2:
                            year = dates[0]
                            month = dates[1]
                        else:
                            year = dates[0]
                            month = "0"

                        self.articleList.append({'title': title,
                                                 'issue': mag + " " + vol,
                                                 'magazine': mag,
                                                 'publisher': pub,
                                                 'link': link,
                                                 'authors': authors,
                                                 'date': date,
                                                 'year': year,
                                                 'month': month,
                                                 'volume': vol,
                                                 'pageFrom': pageFrom,
                                                 'pageUntil': pageUntil,
                                                 'source':'cinii'})
        print(repr(len(self.articleList))+" records mined")



    def saveArticleDataset(self):
        if len(self.articleList) > 0:
            db = RondanDatabaseHelper("rondan2", "root", "")
            publisherID = db.addPublisher(self.publisher)
            magazineID = db.addMagazine(self.magazine, publisherID)

            for article in self.articleList:
                db.addArticle(article, magazineID)

            db.close()

    ###

miner = CiniiDataminer()
start = 2013
end = 2016

for i in range(start,end):
    miner.getArticleDatasets("文学","岩波書店",i,i)
    miner.saveArticleDataset()
    start = i