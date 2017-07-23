# -*- coding: utf-8 -*-
from rondandatabase import RondanDatabaseHelper


def checkAuthors(authors):
    au = []
    for author in authors:
        tmp = author.split("）")
        if len(tmp) == 2:
            author = tmp[1]
        au.append(author)
    return au


def getDetails(detailstring):
    year = int(detailstring.split(",")[0].replace("年",""))
    month = 0
    title = " ".join(detailstring.split(",")[1:])

    return dict({"issue_title": title,
                 "year": year,
                 "month": month})




db = RondanDatabaseHelper("rondan2", "root", "")

YEAR = "1944"

with open("magazines/ChuoKoron"+YEAR+".txt","r", encoding="utf-8") as file:
    lines = file.read().splitlines()
    #print(lines)

    articles = []
    i = 0
    while i < len(lines) -3:
        title = lines[i]
        authors = lines[i+1].split("、")
        authors = checkAuthors(authors)
        details = getDetails(lines[i+2])
        print(title)
        print(authors)
        print(details)
        i += 4

        articles.append({
            "title": title,
            "authors": authors,
            "issue": details["issue_title"],
            "year": details["year"],
            "month": details["month"],
            "source": "zassaku",
            "pageFrom": 0,
            "pageUntil": 0,
            "link": ""
        })


    publisherID = db.addPublisher("中央公論新社")
    magazineID = db.addMagazine("中央公論",publisherID)

    for article in articles:
        db.addArticle(article, magazineID)

db.close()

