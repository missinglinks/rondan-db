from persondataminer import getUrlDataAsString
import urllib, json
import mysql.connector




connection = mysql.connector.connect(user="root", database="rondan2", password="")
cursor = connection.cursor(buffered=True)
cursor2 = connection.cursor(buffered=True)
cursor3 = connection.cursor(buffered=True)
cursor4 = connection.cursor(buffered=True)

query = 'SELECT id FROM person'
cursor.execute(query)
for row in cursor:
    print(row[0])

    sql2 = 'SELECT id FROM article_persons WHERE person_id = %(person_id)s'
    cursor2.execute(sql2, {"person_id": row[0]})

    if cursor2.rowcount == 0:
        print("no articles -- delete person")
        del_sql = 'DELETE FROM person WHERE id = %(person_id)s'
        cursor3.execute(del_sql, {"person_id": row[0]})
        connection.commit()
    else:
        print("articles found")



cursor.close()
cursor2.close()
connection.close()