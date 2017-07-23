from persondataminer import getUrlDataAsString
import urllib, json
import mysql.connector


def mecabString(str):
    str = urllib.parse.quote(str)
    url = "http://chasen.org/~taku/software/mecapi/mecapi.cgi?sentence="+str+"&response=surface&filter=noun,uniq&format=json"

    data = getUrlDataAsString(url)
    return data




connection = mysql.connector.connect(user="root", database="rondan2", password="")
cursor = connection.cursor(buffered=True)
cursor2 = connection.cursor(buffered=True)

query = 'SELECT id, title FROM article WHERE title_morph IS NULL'
cursor.execute(query)
for row in cursor: 
    print(row[0])
    print(row[1])
    title_morph = mecabString(row[1]).replace("\n","")
    insertQuery = "UPDATE article SET title_morph=%s WHERE id=%s"
    cursor2.execute(insertQuery,(title_morph, row[0]))
    connection.commit()

cursor.close()
cursor2.close()
connection.close()