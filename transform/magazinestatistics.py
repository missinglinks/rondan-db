from persondataminer import getUrlDataAsString
import urllib, json
import mysql.connector




connection = mysql.connector.connect(user="root", database="rondan2", password="")
cursor = connection.cursor(buffered=True)
cursor2 = connection.cursor(buffered=True)
cursor3 = connection.cursor(buffered=True)
cursor4 = connection.cursor(buffered=True)

query = 'SELECT id, stat_avg_age FROM magazine'
cursor.execute(query)
for row in cursor:
    print(row[0])

    avg_year_dict = []
    female_author_list = []
    first_time_list = []

    for year in range(1945,2016):
        age_query = 'SELECT AVG(%(year)s-person.year_of_birth) AS avg_year FROM person ' \
                    'JOIN article_persons ap ON ap.person_id = person.id ' \
                    'JOIN article a ON ap.article_id = a.id ' \
                    'JOIN issue i ON a.issue_id = i.id ' \
                    'WHERE person.year_of_birth > 1800 AND person.year_of_birth < 2016 AND person.year_of_birth IS NOT NULL ' \
                    'AND i.year =%(year)s AND i.magazine_id=%(magazine)s'
        cursor2.execute(age_query, {"year": year, "magazine": row[0]})
        #print(age_query)
        #print(cursor2.rowcount)
        for (avg_year) in cursor2:
            if avg_year[0] is None:
                avg = None
            else:
                avg = round(float(str(avg_year[0])),1)
            avg_year_dict.append({"year": year,
                                  "avg_age": avg})


        fa_query = 'SELECT COUNT(DISTINCT person.id) AS female_authors FROM person ' \
                    'JOIN article_persons ap ON ap.person_id = person.id ' \
                    'JOIN article a ON ap.article_id = a.id ' \
                    'JOIN issue i ON a.issue_id = i.id ' \
                    'WHERE person.sex="f" ' \
                    'AND i.year =%(year)s AND i.magazine_id=%(magazine)s'

        all_query = 'SELECT COUNT(DISTINCT person.id) AS female_authors FROM person ' \
                    'JOIN article_persons ap ON ap.person_id = person.id ' \
                    'JOIN article a ON ap.article_id = a.id ' \
                    'JOIN issue i ON a.issue_id = i.id ' \
                    'WHERE person.sex IS NOT NULL ' \
                    'AND i.year =%(year)s AND i.magazine_id=%(magazine)s'


        cursor2.execute(all_query, {"year": year, "magazine": row[0]})
        all_authors = cursor2.fetchone()
        all_authors_number = int(all_authors[0])

        cursor2.execute(fa_query, {"year": year, "magazine": row[0]})
        for (female_authors) in cursor2:
            if all_authors_number == 0:
                fa_ratio = None
            else:
                fa_ratio = int(female_authors[0])/all_authors_number * 100
            female_author_list.append({"year": year, "fa_ratio": fa_ratio})



        issues_query = 'SELECT DISTINCT id, year, month FROM issue ' \
                       'WHERE year=%(year)s AND magazine_id=%(magazine)s'

        cursor2.execute(issues_query, {"year": year, "magazine": row[0]})

        first_time = 0
        for (iid, year, month) in cursor2:

            author_query = 'SELECT DISTINCT person.id AS pid FROM person ' \
                           'JOIN article_persons ap ON ap.person_id = person.id ' \
                           'JOIN article a ON ap.article_id = a.id ' \
                           'WHERE a.issue_id = %(issue)s'

            cursor3.execute(author_query, {"issue":iid})

            for (pid) in cursor3:
                older_query = 'SELECT COUNT(DISTINCT article.id) FROM article ' \
                              'JOIN article_persons ap ON ap.article_id = article.id ' \
                              'JOIN issue i ON i.id = article.issue_id ' \
                              'WHERE ap.person_id=%(person)s AND ' \
                              '((i.year = %(year)s AND i.month < %(month)s) OR ' \
                              'i.year < %(year)s)'
                cursor4.execute(older_query, {"year": year, "month": month, "person": pid[0]})
                num = cursor4.fetchone()
                if num[0] == 0:
                    first_time += 1

        first_time_list.append({"year": year, "first_time": first_time})


    avg_age_json = json.dumps(avg_year_dict)
    female_author_json = json.dumps(female_author_list)
    first_time_json = json.dumps(first_time_list)
    print(avg_age_json)
    print(female_author_json)
    print(first_time_json)




    insertQuery = "UPDATE magazine SET stat_avg_age=%s WHERE id=%s"
    cursor2.execute(insertQuery,(avg_age_json, row[0]))
    connection.commit()
    insertQuery = "UPDATE magazine SET stat_fa_ratio=%s WHERE id=%s"
    cursor2.execute(insertQuery, (female_author_json, row[0]))
    connection.commit()

    insertQuery = "UPDATE magazine SET stat_new_authors=%s WHERE id=%s"
    cursor2.execute(insertQuery, (first_time_json, row[0]))
    connection.commit()

cursor.close()
cursor2.close()
connection.close()