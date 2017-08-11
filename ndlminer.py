from tools.common import getUrlAsSoup

ARTICLE_URL = 'http://iss.ndl.go.jp/api/opensearch?dpgroupid=digitalcontents&from={year_from}-01&until={year_to}-12&title={magazine}&publisher={publisher}'


def getToC(permalink):
    soup = getUrlAsSoup(permalink+".rdf", parser="xml")
    toc = []

    issueTitle = soup.find("title").text
    volume = soup.find("volume")
    value = soup.find("value").text
    print(value)

    #get time of publication
    issued = soup.find("issued").text
    datesplit = issued.split('-')
    if len(datesplit) >= 2:
        year = int(datesplit[0])
        month = int(datesplit[1])
    else:
        year = int(datesplit[0])
        month = 0

    if volume and soup:
        vol = volume.Description.value.text

        toctree = soup.find("tableOfContents")
        if toctree:
            print("Mining " + issueTitle + " ...")
            for item in toctree.find_all("title"):
                articlestr = item.text.replace("//", "").replace("@@", "")

                title = ""
                pages = ""
                authors = ""

                parts = articlestr.split('/')

                if len(parts) == 1:
                    title = parts[0]
                elif len(parts) == 2:
                    title = parts[0]
                    if "p" in parts[1] and "(" in parts[1]:
                        pages = parts[1]
                    else:
                        authors = parts[1].trip().split(";")
                else:
                    last = parts[len(parts) - 1]
                    if "p" in last and "(" in last:
                        pages = last
                        if len(parts[len(parts)-2]) > 15 and ";" not in parts[len(parts)-2]:
                            content = parts[:len(parts)-1]
                        else:
                            authors = parts[len(parts) - 2].strip().split(";")
                            content = parts[0:len(parts) - 2]
                        for c in content:
                            title += c
                    else:
                        authors = last.strip().split(";")
                        content = parts[0:len(parts) - 2]
                        for c in content:
                            title += c
                pageFrom = 0
                pageUntil = 0
                if pages != "":
                    if pages[0] == " ":
                        pages = pages[1:len(pages)].split(" ")[0]
                    else:
                        pages = pages.split(" ")[0]


                pages = pages.replace('p',"")
                pages = pages.split('～')
                pageFrom = str(pages[0])
                if len(pages) > 1:
                    if pages[1] != "":
                        pageUntil = str(pages[1])

                toc.append({'title': title.replace("-","ー"),
                            'authors': authors,
                            'pageFrom': pageFrom,
                            'pageUntil': pageUntil})

    return {'title': issueTitle,
            'year': year,
            'month': month,
            'toc': toc }



def getArticles(magazine, publisher, year_from, year_to):
    articles = []

    soup = getUrlAsSoup(ARTICLE_URL.format(magazine=magazine, publisher=publisher, year_from=year_from, year_to=year_to), parser="xml")
    total_results = int(soup.find("totalResults").text)
    print("Issues found: "+repr(total_results))

    for item in soup.find_all("item"):
        title = item.find("title").text
        print (title)
        
        if magazine in title:
            permalink = item.find("link").text
            vol = item.find("volume")
            toc = getToC(permalink)
            print(toc)
            break
            #issue = self.getIssueData(permalink)
            #if len(issue["toc"]) > 0:
                #self.issueList.append(issue)
        

    return articles


getArticles("思想","岩波書店",1999,1999)



"""
# -*- coding: utf-8 -*-
from urllib import request
from persondataminer import getUrlDataAsString
from rondandatabase import RondanDatabaseHelper
from bs4 import BeautifulSoup

class NDLDataminer:

    def __init__(self):
        self.issueList = []
        self.magazine = ""
        self.magazineISSN = ""
        self.publisher = ""


    def getIssueData (self, permalink):
        data = getUrlDataAsString(permalink+".rdf")
        issueData = []
        toc = []

        if data is not None:
            soup = BeautifulSoup(data, "xml")
            issueTitle = soup.find("title").text
            volume = soup.find("volume")
            value = soup.find("value").text
            print(value)

            issued = soup.find("issued").text
            datesplit = issued.split('-')
            if len(datesplit) >= 2:
                year = int(datesplit[0])
                month = int(datesplit[1])
            else:
                year = int(datesplit[0])
                month = 0

            if volume is not None and soup is not None:
                vol = volume.Description.value.text


                toctree = soup.find("tableOfContents")
                if toctree is not None:
                    print("Mining " + issueTitle + " ...")
                    for item in toctree.find_all("title"):
                        articlestr = item.text.replace("//", "").replace("@@", "")

                        title = ""
                        pages = ""
                        authors = ""

                        parts = articlestr.split('/')

                        if len(parts) == 1:
                            title = parts[0]
                        elif len(parts) == 2:
                            title = parts[0]
                            if "p" in parts[1] and "(" in parts[1]:
                                pages = parts[1]
                            else:
                                authors = parts[1].replace(" ", "").split(";")
                        else:
                            last = parts[len(parts) - 1]
                            if "p" in last and "(" in last:
                                pages = last
                                if len(parts[len(parts)-2]) > 15 and ";" not in parts[len(parts)-2]:
                                    content = parts[:len(parts)-1]
                                else:
                                    authors = parts[len(parts) - 2].replace(" ", "").split(";")
                                    content = parts[0:len(parts) - 2]
                                for c in content:
                                    title += c
                            else:
                                authors = last.replace(" ", "").split(";")
                                content = parts[0:len(parts) - 2]
                                for c in content:
                                    title += c
                        pageFrom = 0
                        pageUntil = 0
                        if pages != "":
                            if pages[0] == " ":
                                pages = pages[1:len(pages)].split(" ")[0]
                            else:
                                pages = pages.split(" ")[0]


                        pages = pages.replace('p',"")
                        pages = pages.split('～')
                        pageFrom = str(pages[0])
                        if len(pages) > 1:
                            if pages[1] != "":
                                pageUntil = str(pages[1])

                        toc.append({'title': title.replace("-","ー"),
                                    'authors': authors,
                                    'pageFrom': pageFrom,
                                    'pageUntil': pageUntil})

            return {'title': issueTitle,
                    'year': year,
                    'month': month,
                    'toc': toc }
        else:
            return None



    def getMagazineData (self, name, publisher, year):
        self.issueList = []
        self.magazine = name
        self.publisher = publisher

        url = 'http://iss.ndl.go.jp/api/opensearch?dpgroupid=digitalcontents&from='+ repr(year) +'-01&until='+ repr(year) +'-12&title='+request.quote(name)+'&publisher='+request.quote(publisher)
        print (url)
        data = getUrlDataAsString(url)

        soup = BeautifulSoup(data,"xml")
        totalResults = int(soup.find("totalResults").text)
        print("Issues found: "+repr(totalResults))

        for item in soup.find_all("item"):
            title = item.find("title").text
            if name in title:
                permalink = item.find("link").text
                vol = item.find("volume")
                issue = self.getIssueData(permalink)
                if len(issue["toc"]) > 0:
                    self.issueList.append(issue)

    def saveMagazineDataToDb(self):
        if len(self.issueList) > 0:
            db = RondanDatabaseHelper("rondan2", "root", "")
            publisherID = db.addPublisher(self.publisher)
            magazineID = db.addMagazine(self.magazine, publisherID)

            for issue in self.issueList:
                if issue is not None:
                    issueID = db.addIssue(issue['title'],issue['year'],issue['month'], magazineID)
                    db.addToc(issue["toc"], issueID, issue['year'])

            db.close()


#booksPerYear("岩波書店", 1966, 1977)
miner = NDLDataminer()
for i in range(1991,2016):
    miner.getMagazineData("Sapio","小学館",i)
    miner.saveMagazineDataToDb()

"""