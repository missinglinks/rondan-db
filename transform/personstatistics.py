from persondataminer import getUrlDataAsString
import urllib, json
import mysql.connector
import itertools
from collections import defaultdict



########### Calculate yearly social capital for all entries in table person
########### Save yearly results as JSON string in table person_statistic
########### Last change: 7.2.2017

connection = mysql.connector.connect(user="root", database="rondan2", password="")
cursor = connection.cursor(buffered=True)

"""
# get number of published magazines every year
mag_total = defaultdict(int)
query = "SELECT COUNT(DISTINCT magazine_id) FROM issue WHERE year = %(year)s"
for year in range(1945, 2016):
    cursor.execute(query, {"year": year})
    count = int(cursor.fetchone()[0])
    mag_total[year] = count

print(mag_total)
"""

query = 'SELECT id FROM person'
cursor.execute(query)
for row in cursor:
    person_id = row[0]

    #get min and max year for person
    cursor2 = connection.cursor(buffered=True)
    query = "SELECT MIN(i.year) AS year_min, MAX(i.year) AS year_max FROM issue i " \
             "JOIN article a ON a.issue_id = i.id " \
             "JOIN article_persons ap ON ap.article_id = a.id " \
             "WHERE ap.person_id = %(person)s"

    cursor2.execute(query, {"person": person_id})
    res = cursor2.fetchone()
    year_min = res[0]
    year_max = res[1]
    cursor2.close()

    sc_data = []

    for year in range(year_min, year_max+1):
        # get magazines list until specified year
        mag_query = "SELECT DISTINCT m.id FROM magazine m " \
                    "JOIN issue i ON i.magazine_id = m.id " \
                    "JOIN article a ON a.issue_id = i.id " \
                    "JOIN article_persons ap ON ap.article_id = a.id " \
                    "WHERE i.year <= %(year)s AND ap.person_id = %(person)s "

        cursor2 = connection.cursor(buffered=True)
        cursor2.execute(mag_query, {"year": year,
                                    "person": person_id})

        mag_list = list(cursor2.fetchall())


        person_query = 'SELECT ap.person_id ' \
                       'FROM article_persons ap ' \
                       'JOIN article a ON a.id = ap.article_id ' \
                       'JOIN issue i ON i.id = a.issue_id ' \
                       'WHERE i.year = %(year)s AND ap.article_id IN (SELECT article_id FROM article_persons  WHERE person_id = %(person)s) ' \
                       'GROUP BY ap.person_id '

        cursor2.execute(person_query, {"person": person_id,
                                       "year": year})
        person_list = list(itertools.chain.from_iterable(list(cursor2.fetchall())))
        if len(person_list) > 0:
            person_list.remove(person_id)

        sc_data.append({"year": year,
                        "magazines": list(itertools.chain.from_iterable(mag_list)),
                        "persons": person_list})

    print(sc_data)

cursor.close()
connection.close()