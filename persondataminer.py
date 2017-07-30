from common import getUrlAsJson, similar

VIAF_URL = 'http://www.viaf.org/viaf/search?query=local.personalNames+all+"{name}"&maximumRecords=50&httpAccept=application/json&recordSchema=info:srw/schema/1/briefmarcxml-v1.1&sortKeys=holdingscount'

# Search viaf.org for a Name and returns the best match (based on name similarity)
# if more entries match with the same similarity, best match will be based on number of name entries (= number of mentions in national libraries)
def getViafMatch(name):
    viafs = []
    results = getUrlAsJson(VIAF_URL.format(name=name))
    records = results["searchRetrieveResponse"]["records"]

    for record in records:
        viaf_id = record["record"]["recordData"]["viafID"]
        birth_date = record["record"]["recordData"]["birthDate"]
        death_date = record["record"]["recordData"]["deathDate"]
        headings = record["record"]["recordData"]["mainHeadings"]["mainHeadingEl"]
        names = []
        if isinstance(headings, list):
            for heading in headings:
                if isinstance(heading["datafield"]["subfield"], list):
                    names.append(heading["datafield"]["subfield"][0]["#text"])
                else:
                    names.append(heading["datafield"]["subfield"]["#text"])
        else:
            if isinstance(headings["datafield"]["subfield"], list):
                names.append(headings["datafield"]["subfield"][0]["#text"])
            else:
                names.append(headings["datafield"]["subfield"]["#text"])
        names= list(set(names))
        best_match = 0
        for viaf_name in names:
            match = similar(viaf_name.replace(" ","").replace(",","").lower(), name.replace(" ","").replace(",","").lower())
            if match > best_match:
                best_match = match

        viafs.append({
            "viaf_id": viaf_id,
            "names": names,
            "birth_date": birth_date,
            "death_date": death_date,
            "match_ratio": best_match
        })


    viafs.sort(key=lambda x:x["match_ratio"],reverse=True)
    if len(viafs) == 1:
        return viafs[0]
    elif len(viafs) > 1:
        best_match = viafs[0]
        for viaf in viafs:
            if viaf["match_ratio"]  < best_match["match_ratio"]:
                break
            if len(viaf["names"]) > len(best_match["names"]):
                best_match = viaf
        return best_match
    else:
        return None

print(getViafMatch("蓮見重彦"))

"""
import xml.etree.ElementTree as etree
import urllib, json
from urllib import request
from wikidata import WikidataHelper
from kotobank import KotobankPersonHelper
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
import mysql.connector


def getUrlDataAsString(url):
    while True:
        try:
            xfile = request.urlopen(url)
            data = xfile.read().decode("utf-8")
            xfile.close()
            return data
        except HTTPError:
            print("ouch! HTTP Error!!")
            return None
        except URLError:
            break
        except:
            continue

def getViafs(name):
    viafs = []
    name = urllib.parse.quote(name)
    name = name.replace("訳","")
    url = 'https://viaf.org/viaf/search?query=local.personalNames+all+"' + name + '"'
    data = getUrlDataAsString(url)
    if data is not None:
        soup = BeautifulSoup(data, "xml")
        viaftags = soup.find_all("viafID")
        for v in viaftags:
            viafs.append(v.text)
    return viafs


def isPersonInDb(viaf, dbname, user, pwd):
    if viaf is None:
        return False
    else:
        connection = mysql.connector.connect(user=user, database=dbname, password=pwd)
        cursor = connection.cursor(buffered=True)
        query = 'SELECT id FROM person WHERE viaf="' + viaf + '"'
        cursor.execute(query)
        if cursor.rowcount > 0:
            connection.commit()
            cursor.close()
            connection.close()
            return True
        else:
            connection.commit()
            cursor.close()
            connection.close()
            return False


class PersonDataminer:

    def __init__(self, viaf, name):
        self.name_jp = name.decode("utf-8")
        self.name_en = None
        self.birth = 0
        self.death = 0
        self.birthplace = {'name': "",
                           'wkp': "",}
        self.sex = None
        self.penname = None
        self.education = []
        self.dictionaryEntries = []
        self.viaf = viaf
        self.ndl = None
        self.wkp = None
        self.nii = None
        self.wikiLink_ja = None
        self.wikiLink_en = None
        self.possibleEntries = 0
        self.comments=""
        self.needCheck = False
        self.numberLinks = 0
 
    def loadData(self):

        tmp = self.name_jp.replace(" ","").replace(".","")
        try:
            tmp.encode("ASCII")
            print("Western Name detected")
        except:
            self.name_jp = self.name_jp.replace(" ","")
            self.name_jp = self.name_jp.replace('"', "")

        self.getAuthorityIDs()
        if self.viaf is not None:
            self.getViafData()



        if isPersonInDb(self.viaf, "rondan2", "root", ""):
            print("Person already in DB")
        else:
            if self.ndl is not None:
                self.checkRealName()
            if self.wkp is not None:
                self.getWikidata()

            kotobank = KotobankPersonHelper(self.name_jp)
            if self.birth == 0:
                self.birth = kotobank.birth
                self.death = kotobank.death
            self.dictionaryEntries = kotobank.entries

            if kotobank.realName is not None:
                print ("Real Name according to kotobank.jp "+kotobank.realName)

            if self.possibleEntries > 1:
                self.comments = '<B><span style="color: red">PLEASE CHECK DATA</span></B>'

        if self.name_en is not None and self.name_en != "":
            if " " in self.name_en:
                name_split = self.name_en.split(" ")
                last_name = name_split[len(name_split)-1]
                first_name = ""
                for fn in name_split[:len(name_split)-1]:
                    if fn != name_split[len(name_split)-2]:
                        first_name += fn+" "
                    else:
                        first_name += fn
                self.name_en = last_name+" "+str(first_name)



