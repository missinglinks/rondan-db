from persondataminer import getUrlDataAsString
import urllib, json, re
import mysql.connector




connection = mysql.connector.connect(user="root", database="rondan2", password="")
cursor = connection.cursor(buffered=True)
cursor2 = connection.cursor(buffered=True)
cursor3 = connection.cursor(buffered=True)
cursor4 = connection.cursor(buffered=True)



def cleanup(id, name, result):
    if "代" not in result and len(name) > 3:
        print(str(id) + " " + name)
        print(result)
        if len(result) > 3 and len(result) < len(name):
            name = name.replace(result, "").replace(" ", "")
        elif result=="ほか" or result=="他":
            name = name.replace(result, "")
        elif result=="訳":
            if name[len(name)-1] == result:
                name = name.replace(result,"")
        else:
            name = name.replace("(", "").replace(")", "").replace("[", "").replace("]", "")

        print(name)

        if name != "" or name != " ":
            query2 = "SELECT id FROM person WHERE name_jp = %(name)s"
            cursor2.execute(query2, {"name": name})

            personId = cursor2.fetchone()

            if personId is not None:
                old_personId = int(id)

                query3 = "SELECT MIN(i.year) AS year_min, MAX(i.year) AS year_max FROM issue i " \
                         "JOIN article a ON a.issue_id = i.id " \
                         "JOIN article_persons ap ON ap.article_id = a.id " \
                         "WHERE ap.person_id = %(person)s"

                cursor3.execute(query3, {"person": old_personId})
                res = cursor3.fetchone()
                current_min = res[0]
                current_max = res[1]

                personId = int(personId[0])
                print(personId)

                query3 = "SELECT MIN(i.year) AS year_min, MAX(i.year) AS year_max FROM issue i " \
                         "JOIN article a ON a.issue_id = i.id " \
                         "JOIN article_persons ap ON ap.article_id = a.id " \
                         "WHERE ap.person_id = %(person)s"

                cursor3.execute(query3, {"person": personId})
                res = cursor3.fetchone()
                check_min = int(res[0])
                check_max = int(res[1])
                print(str(current_min) + " <----> " + str(check_min))
                print(str(current_max) + " <----> " + str(check_max))

                if current_min is not None:
                    if current_min > check_min - 5:
                        print("REPLACE")
                        print(old_personId)
                        print(personId)
                        # replace article_persons Ids
                        query4 = "UPDATE IGNORE article_persons SET person_id = %(new_person)s WHERE person_id = %(old_person)s"
                        cursor4.execute(query4, {"old_person": old_personId,
                                                 "new_person": int(personId)})

                        # delete person
                        query5 = "DELETE FROM person WHERE id=%(old_person)s"
                        cursor4.execute(query5, {"old_person": old_personId})
                        connection.commit()
    return name

query = 'SELECT id, name_jp, viaf, ndl FROM person WHERE ndl IS NULL'
cursor.execute(query)
i = 0
for row in cursor:
    name = row[1]

    if "他" in name or "ほか" in name:
        print("((((((((((((((            ET AL                )))))))))))))))))))))")
        name = cleanup(row[0], name, "ほか")
        name = cleanup(row[0], name, "他")
        name = cleanup(row[0], name, "訳")

    reex = '(\[.*\]|\(.*\)|.*:)'
    results = re.findall(reex, name)
    if len(results) > 0:
        i += 1
        cleanup(row[0], name, results[0])
    else:
        reex = '(..*長官|..*教授|..*長|..*員会|..*員|.*助手|.*構成|.*編集部|インタヴュー|インタヴュアー|構成･)'
        results = re.findall(reex, name)
        if len(results) > 0:
            i += 1
            cleanup(row[0], name, results[0])




    if name == "":

        old_personId= row[0]

        query4 = "DELETE FROM article_persons WHERE person_id=%(old_person)s"
        cursor4.execute(query4, {"old_person": old_personId})
        # delete person
        query5 = "DELETE FROM person WHERE id=%(old_person)s"
        cursor4.execute(query5, {"old_person": old_personId})

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" + name)

print(i)

cursor.close()
cursor2.close()
cursor3.close()
cursor4.close()
connection.close()