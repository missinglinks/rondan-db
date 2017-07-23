# -*- coding: utf-8 -*-

import mysql.connector
import time
from persondataminer import PersonDataminer, getViafs, getUrlDataAsString




class RondanDatabaseHelper:


    def __init__(self, dbname, user, pwd):
        self.connect(dbname, user, pwd)

    def connect(self, dbname, user, pwd):
        self.connection = mysql.connector.connect(user=user, database=dbname, password=pwd)
        self.cursor = self.connection.cursor(buffered=True)

    def close(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def isPersonInDb(self, viaf):
        query = 'SELECT id FROM person WHERE viaf="' + viaf + '"'
        self.cursor.execute(query)
        if self.cursor.rowcount > 0:
            return True
        else:
            return False

    def addPublisher(self, publisher):
        publisherId = 0
        query = 'SELECT id FROM publisher WHERE name_jp=%(pub)s'
        self.cursor.execute(query, {"pub": publisher})
        for row in self.cursor:
            publisherId = row[0]
        if publisherId == 0:
            addPublisher = 'INSERT INTO publisher (name_jp) VALUES (%(pub)s)'
            self.cursor.execute(addPublisher,{"pub": publisher})
            publisherId = self.cursor.lastrowid
        return publisherId

    def addMagazine(self, magazine, publisherId):
        magazineId = 0
        query = 'SELECT id FROM magazine WHERE name_jp=%(mag)s'
        self.cursor.execute(query, {"mag": magazine})
        for row in self.cursor:
            magazineId = row[0]
        if magazineId == 0:
            addMagazine = 'INSERT INTO magazine (name_jp, publisher_id) VALUES (%s, %s)'
            self.cursor.execute(addMagazine, (magazine, publisherId))
            magazineId = self.cursor.lastrowid
        return magazineId


    def addUniversity(self, university, personId):
        universityId = 0;

        query = 'SELECT id FROM university WHERE wkp=%(wkp)s'
        self.cursor.execute(query, {"wkp": university['wkp']})
        for row in self.cursor:
            universityId = row[0]
        if universityId == 0:
            addUniversity = 'INSERT INTO university(name, name_jp, wkp) VALUES (%s, %s, %s)'
            self.cursor.execute(addUniversity, (university['name'], university['name_jp'], university['wkp']))
            universityId = self.cursor.lastrowid

        educated = 0
        query = 'SELECT id FROM person_universities WHERE person_id = %s AND university_id = %s'
        self.cursor.execute(query, (personId, universityId))
        for row in self.cursor:
            educated = row[0]
        if educated == 0:
            addEducation = 'INSERT INTO person_universities (person_id, university_id) VALUES (%s,%s)'
            self.cursor.execute(addEducation, (personId, universityId))

        return universityId


    def addDictionaryEntry(self, entry, personId):
        dictId = 0;

        query = 'SELECT id FROM dictionaryentry WHERE dictionary=%(dictionary)s and person_id=%(person_id)s'
        self.cursor.execute(query, {"dictionary": entry['dictionary'],
                                    "person_id": personId})
        for row in self.cursor:
            dictId = row[0]
        if dictId == 0:
            addEntry = 'INSERT INTO dictionaryentry(dictionary, entry, date, link, person_id) VALUES (%s, %s, %s, %s, %s)'
            self.cursor.execute(addEntry, (entry['dictionary'], entry['entry'], time.strftime('%Y-%m-%d %H:%M:%S'), entry['link'], personId))
            dictId = self.cursor.lastrowid

        return dictId


    def addPenname(self, penname, personId, articleId):
        pnameId = 0;

        query = 'SELECT id FROM penname WHERE penname=%(penname)s and person_id=%(person_id)s and article_id=%(article_id)s'
        self.cursor.execute(query, {"penname": penname,
                                    "person_id": personId,
                                    "article_id": articleId})
        for row in self.cursor:
            pnameId = row[0]
        if pnameId == 0:
            addEntry = 'INSERT INTO penname(penname, person_id, article_id) VALUES (%s, %s, %s)'
            self.cursor.execute(addEntry, (penname, personId, articleId))
            dictId = self.cursor.lastrowid



    def addPerson(self, person, articleId, publication_year):

        add_new = False
        if int(publication_year) < int(person.birth)+15: #author too young
            person.viaf = None
            person.wkp = None
            person.ndl = None
            person.nii = None
            person.wikiLink_ja = ""
            person.wikiLink_en = ""
            add_new = True
            person.name_jp = person.name_jp+"*"

        personId = 0
        if '"' in str(person.name_jp):
            person.name_jp = person.name_jp.replace('"',"")

        if add_new is not True:
            if person.wkp != None:
                query = 'SELECT id FROM person WHERE wkp="'+person.wkp+'"'
            elif person.ndl != None:
                query = 'SELECT id FROM person WHERE ndl="'+person.ndl+'"'
            else:
                query = 'SELECT id FROM person WHERE name_jp="'+person.name_jp+'"'
            print(query)
            self.cursor.execute(query)
            for row in self.cursor:
                personId = row[0]
        if personId == 0 or add_new is True:
            addPerson = 'INSERT INTO person (name_jp, name, year_of_birth, year_of_death, sex, birthplace, birthplaceWKP, ndl, viaf, wkp, nii, wikipedia_en, wikipedia_jp, comments) VALUES (%(name_jp)s, %(name_en)s, %(birth)s, %(death)s, %(sex)s, %(birthplace)s, %(birthplaceWKP)s, %(ndl)s, %(viaf)s, %(wkp)s, %(nii)s, %(wikipedia_en)s, %(wikipedia_jp)s, %(comments)s)'
            self.cursor.execute(addPerson, {'name_jp': person.name_jp,
                                            'name_en': person.name_en,
                                            'birth': int(person.birth),
                                            'death': int(person.death),
                                            'sex': person.sex,
                                            'birthplace': person.birthplace['name'],
                                            'birthplaceWKP': person.birthplace['wkp'],
                                            'ndl': person.ndl,
                                            'viaf': person.viaf,
                                            'wkp': person.wkp,
                                            'nii': person.nii,
                                            'wikipedia_en': person.wikiLink_en,
                                            'wikipedia_jp': person.wikiLink_ja,
                                            'comments' : person.comments,
                                            })
            personId = self.cursor.lastrowid

        for university in person.education:
            self.addUniversity(university, personId)

        for entry in person.dictionaryEntries:
            self.addDictionaryEntry(entry, personId)

        if person.penname is not None:
            self.addPenname(person.penname, personId, articleId)

        return personId

    def addIssue(self, title, year, month, magazineId):
        issueId = 0
        query = 'SELECT id FROM issue WHERE title=%(title)s'
        self.cursor.execute(query, {"title": title})
        for row in self.cursor:
            issueId = row[0]
        if issueId == 0:
            addIssue = 'INSERT INTO issue (title, magazine_id, year, month) VALUES (%s, %s, %s, %s)'
            self.cursor.execute(addIssue, (title, magazineId, year, month))
            issueId = self.cursor.lastrowid
        return issueId

    ## for NDL miner
    def addToc(self, toc, issueId, publication_year):
        for article in toc:
            articleId = 0
            query = 'SELECT id FROM article WHERE issue_id=%s AND title=%s'
            self.cursor.execute(query, (issueId, article["title"]))
            for row in self.cursor:
                articleId = row[0]
            if articleId == 0:
                addArticle = 'INSERT INTO article (title, issue_id, page_start, page_end,source) VALUES (%s,%s,%s,%s,"ndldc")'
                self.cursor.execute(addArticle, (article['title'], issueId, article['pageFrom'], article['pageUntil']))
                articleId = self.cursor.lastrowid

            for author in article['authors']:
                person = author.replace("@@", " ")
                add_person = self.getFittingPerson(person.encode("utf8"), publication_year)

                authorId = self.addPerson(add_person, articleId, publication_year)
                writes = 0
                query = 'SELECT id FROM article_persons WHERE article_id = %s AND person_id = %s'
                self.cursor.execute(query, (articleId, authorId))
                for row in self.cursor:
                    writes = row[0]
                if writes == 0:
                    addWriter = 'INSERT INTO article_persons (article_id, person_id) VALUES (%s,%s)'
                    self.cursor.execute(addWriter, (articleId, authorId))

                if add_person.needCheck is True:  # set check-article flag
                    print("article flagged")
                    query = "UPDATE article SET check_article='1' WHERE id=%(id)s"
                    self.cursor.execute(query, {"id": articleId})

        self.connection.commit()


    def getFittingPerson(self, personname, year):
        print(personname)

        viafs = getViafs(personname)
        print("Viafs found: " + str(len(viafs)))

        i = 0
        add_person = None
        linkNumber = 0

        for viaf in viafs:
            i += 1
            person = PersonDataminer(viaf, personname)
            person.loadData()
            if person.name_en is not None:
                if (int(person.birth) + 16) < int(year):
                    if person.numberLinks > linkNumber:
                        add_person = person
                        linkNumber = person.numberLinks

            if i == len(viafs) and add_person == None:
                add_person = person

        if len(viafs) == 0:
            add_person = PersonDataminer(None, personname)
            add_person.loadData()
        elif len(viafs) > 1:
            add_person.needCheck=True
        return add_person

    ## for Cinii miner
    def addArticle(self, article, magazineId):
        issueId = self.addIssue(article['issue'], article['year'], article['month'], magazineId)

        articleId = 0
        query = 'SELECT id FROM article WHERE issue_id=%s AND title=%s'
        self.cursor.execute(query, (issueId, article["title"]))
        for row in self.cursor:
            articleId = row[0]
        if articleId == 0:
            addArticle = 'INSERT INTO article (title, issue_id, page_start, page_end, permalink, source) VALUES (%s,%s,%s,%s,%s,%s)'
            self.cursor.execute(addArticle,
                           (article['title'], issueId, article['pageFrom'], article['pageUntil'], article['link'], article['source']))
            articleId = self.cursor.lastrowid

        for author in article['authors']:
            try:
                pers = author.text.replace("@@", " ")
            except:
                pers = author
            add_person = self.getFittingPerson(pers.encode("utf-8"), article["year"])

            authorId = self.addPerson(add_person, articleId, article['year'])
            writes = 0
            query = 'SELECT id FROM article_persons WHERE article_id = %s AND person_id = %s'
            self.cursor.execute(query, (articleId, authorId))
            for row in self.cursor:
                writes = row[0]
            if writes == 0:
                addWriter = 'INSERT INTO article_persons (article_id, person_id) VALUES (%s,%s)'
                self.cursor.execute(addWriter, (articleId, authorId))

            if add_person.needCheck is True:  # set check-article flag
                print("article flagged")
                query = "UPDATE article SET check_article='1' WHERE id=%(id)s"
                self.cursor.execute(query, {"id": articleId})

        self.connection.commit()

    def resetAll(self):
        cnx = mysql.connector.connect(user='root', database='rondan')
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM university WHERE 1")
        cursor.execute("DELETE FROM person WHERE 1")
        cursor.execute("DELETE FROM issue WHERE 1")
        cursor.execute("DELETE FROM article WHERE 1")
        cursor.execute("DELETE FROM article_persons WHERE 1")
        cursor.execute("DELETE FROM magazine WHERE 1")
        cursor.execute("DELETE FROM university WHERE 1")
        cursor.execute("DELETE FROM person_universities WHERE 1")
        cursor.execute("DELETE FROM dictionaryentry WHERE 1")
        cnx.commit()
        cursor.close()
        cnx.close()
