# -*- coding: utf-8 -*-

from persondataminer import getUrlDataAsString
import urllib, json, re
import mysql.connector
from geotext import GeoText


def removeUmlaut(my_string):
    mapping = [('Ö', 'Oe'), ('Ä', 'Ae'), ('Ü', 'Ue'), ('ö', 'oe'), ('ä', 'ae'), ('ü', 'ue')]
    for k, v in mapping:
        my_string = my_string.replace(k, v)
    return my_string

def addUmlaut(my_string):
    mapping = [('Ö', 'Oe'), ('Ä', 'Ae'), ('Ü', 'Ue'), ('ö', 'oe'), ('ä', 'ae'), ('ü', 'ue')]
    for k, v in mapping:
        my_string = my_string.replace(v, k)
    return my_string

def decodeInstitutions(my_string):
    mapping = [('JE', 'Japanische Eisenbahn (Nihon Tetsudô 日本鉄道)'),
               ('JKR', 'Japanisches Rotes Kreuz (Nihon Sekijûji 日本赤十字)'),
               ('KG', 'Aktiengesellschaft (Kabushishiki Gaisha株式会社)'),
               ("LB","Lokale Behörde (chihô seifu 地方政府)"),
               ("MfA","Ministerium für Auswärtiges (Gaimushô 外務省)"),
               ("MfI","Ministerium für Inneres (Naimushô 内務省)"),
               ("MfB","Ministerium für Bildung und Kultur (Monbushô 文部省)"),
               ("MfF","Ministerium für Finanzen (Ôkurashô 大蔵省)"),
               ("MfJ","Ministerium für Justiz (Shihôshô 司法省)"),
               ("MfLH","Ministerium für Landwirtschaft und Handel (Nôshômushô 農商務省)"),
               ("MfK","Ministerium für Kaiserlichen Haushalt (Kunaishô 宮内省)"),
               ("MfKom","Ministerium für Kommunikation (Tsûshinshô 通信省)"),
               ("MfN","Ministerium für Nachrichtenwesen oder Kommunikation (Tsûshinshô 通信省)"),
               ("RI","Regierungsinstitution (nicht näher definiert)"),
               ("SME","Südmandschurische Eisenbahn (Mantetsu 満鉄)")]
    for k, v in mapping:
        my_string = my_string.replace(k, v)
    return my_string


connection = mysql.connector.connect(user="root", database="rondan2", password="")

cursor = connection.cursor(buffered=True)
cursor2 = connection.cursor(buffered=True)

query = 'SELECT text, id FROM jade_person'


cursor.execute(query)
for row in cursor:
    infos = row[0].splitlines()[0].split("♦")

    first = infos[0]
    year_regex = r"([1-2][0-9]{3})"
    years = re.findall(r"\d{4}", first)
    first = first.split(" - ")[0].split(" – ")[0].replace ("U ", "u ").replace("TH ", "th")
    print (first)
    first = removeUmlaut(first)
    sending_institution = re.findall(r"[\d|?|-|–] \(([A-Z]\w*)\)", first)
    disziplin = re.findall(r"[\d|\)|-|?|–] ([A-Z]\w*)", first)

    if len(years) > 0:
        year_min =  int(years[0])
        year_max = int(years[0])
        for year in years:
            if int(year) > year_max:
                year_max = int(year)
    if len(sending_institution) > 0:
        sending_institution = decodeInstitutions(sending_institution[0])
    else:
        sending_institution = "NULL"
    if len(disziplin) > 0:
        disziplin = disziplin[0]
        disziplin = disziplin.replace("NW","Naturwissenschaften")
        disziplin = addUmlaut(disziplin)
    else:
        disziplin = "NULL"
    if sending_institution == "Musik":
        disziplin = "Musik"
        sending_institution = "NULL"

    print(str(year_min) +"-"+ str(year_max))
    print(sending_institution)
    print(disziplin)

    places = GeoText(row[0].splitlines()[0].replace("U ", "u ").replace("TH ", "th "))
    print(places.cities)
    print("------------------------------------------------------------")


    sql = "UPDATE jade_person SET year_from=%(year_from)s, year_until=%(year_until)s, disziplin=%(disziplin)s, " \
          "sending_institution=%(sending_institution)s WHERE id=%(id)s"
    cursor2.execute(sql,{"year_from": str(year_min),
                         "year_until": str(year_max),
                         "disziplin": str(disziplin),
                         "sending_institution": str(sending_institution),
                         "id": int(row[1])})


cursor.close()