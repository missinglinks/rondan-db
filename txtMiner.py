# -*- coding: utf-8 -*-
from rondandatabase import RondanDatabaseHelper


def getToc(lines):
    toc = []
    i = 0
    while True:
        if i >= len(lines):
            break
        line = lines[i]
        if line == "":
            i += 1
            continue

        title = line
        if lines[i+1] != "//":
            authors = lines[i+1].split("/")
        else:
            authors = []

        print(title+" // "+str(authors))
        i += 2

        toc.append({"title": title,
                   "authors": authors,
                   "pageFrom":0,
                   "pageUntil":0})

    return toc


db = RondanDatabaseHelper("rondan2", "root", "")

with open("magazines/YASO.txt","r", encoding="utf-8") as file:
    magazine = file.readline().replace("\n","")
    publisher = file.readline()
    file.readline()
    eof = False

    all = file.read()
    i = 0
    lines = all.split("\n")
    issue_title = ""
    issue_date = ""
    issue = []

    # add magazine to DB
    publisherId = db.addPublisher(publisher)
    magazineId = db.addMagazine(magazine, publisherId)

    while eof == False:

        if i >= len(lines):
            break
        line = lines[i]

        if line[0:2] == "-*":
            if len(issue) > 0:
                toc = getToc(issue)
                db.addToc(toc, issueId, year)

            #new issue
            issue = []
            issue_date = line[2:].split("/")
            year = int(issue_date[0])
            month = int(issue_date[1])
            issue_title = lines[i+1]

            print(issue_title)
            i += 2

            issueId = db.addIssue(issue_title, year, month, magazineId)
            # add issue to DB


        else:
            issue.append(line)

        i += 1

db.close()

