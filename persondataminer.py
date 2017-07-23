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


    def getViafData(self):
        print("checking viaf data")
        data = getUrlDataAsString("http://viaf.org/viaf/"+self.viaf+"/rdf.xml")
        if data is not None:
            soup = BeautifulSoup(data, "lxml")
            names = soup.find_all('schema:name')
            for name in names:
                if name is not None:
                    if name.get("xml:lang") in ("en", "en-US", "de", "de-DE"):
                        tmp = name.text
                        if len(tmp) > 1:
                            if tmp[1].islower():
                                self.name_en = tmp
                                break
            for name in names:
                if name is not None:
                    if name.get("xml:lang") in ("jp-JP", "jp"):
                        tmp = name.text
                        self.name_jp = tmp.replace(" ","")

            data = getUrlDataAsString("http://viaf.org/viaf/"+self.viaf + "/marc21.xml")
            if data is not None:
                soup = BeautifulSoup(data, "lxml")
                subfields = soup.find_all("mx:subfield")
                for sub in subfields:
                    if sub.get("code") == "d":
                        years = sub.text.replace(u"(", "").replace(u")", "")
                        years = years.split("-")
                        try:
                            self.birth = int(years[0])
                        except:
                            pass

                        if len(years) > 1:
                            try:
                                self.death = int(years[1])
                            except:
                                pass
                        break


    def checkRealName(self):
        print("Checking if real name")
        url = "http://id.ndl.go.jp/auth/ndlna/"+self.ndl+".json"
        data = getUrlDataAsString(url)
        try:
            ndl = json.loads(data)
        except:
            print("Could not load NDL data")
            ndl = []

        if "realName" in ndl:
            uri = ndl["realName"][0]["uri"]
            label =  ndl["realName"][0]["label"]
            realname = label.split(u",")[0]+label.split(u",")[1]
            self.penname = self.name_jp
            self.name_jp = realname.replace("","").encode("utf8")
            print("Real name: "+realname+" "+uri)

            data = getUrlDataAsString(uri + ".json")
            try:
                ndl = json.loads(data)
                uri = ndl["exactMatch"][0]["uri"]
                data = getUrlDataAsString(uri+"/justlinks.json")
                links = json.loads(data)
                self.viaf = uri
                if "viafID" in links:
                    self.viaf = "http://viaf.org/viaf/"+links["viafID"]
                if "NDL" in links:
                    self.ndl = links["NDL"][0]
                if "WKP" in links:
                    self.wkp = links["WKP"][0]
                if "NII" in links:
                    self.nii = links["NII"][0]
            except:
                pass
        else:
            print("Name is real")


    def getWikidata(self):
        wikidata = WikidataHelper().getJson(self.wkp)
        if wikidata is not None:
            labels = wikidata['entities'][self.wkp]['labels']
            claims = wikidata['entities'][self.wkp]['claims']
            links = wikidata['entities'][self.wkp]['sitelinks']
            if "en" in labels:
                self.name_en = labels['en']['value']
            if "ja" in labels:
                self.name_jp = labels['ja']['value']
            if "P19" in claims:
                if "datavalue" in claims['P19'][0]['mainsnak']:
                    placeOfBirthID = claims['P19'][0]['mainsnak']['datavalue']['value']['id']
                    placeOfBirthLabel = WikidataHelper().getLabel(placeOfBirthID, "en")
                    self.birthplace = {'name': placeOfBirthLabel,
                                       'wkp': placeOfBirthID}
            if "P69" in claims:
                for edu in claims['P69']:
                    educatedAtID = edu['mainsnak']['datavalue']['value']['id']
                    educatedAtLabel_en = WikidataHelper().getLabel(educatedAtID, "en")
                    educatedAtLabel_jp = WikidataHelper().getLabel(educatedAtID, "ja")
                    self.education.append({'name': educatedAtLabel_en,
                                           'name_jp': educatedAtLabel_jp,
                                           'wkp': educatedAtID})
            if "P569" in claims:
                if "datavalue" in claims['P569'][0]['mainsnak']:
                    birthdate =  claims['P569'][0]['mainsnak']['datavalue']['value']['time']
                    self.birth = birthdate[1:5]
            if "P570" in claims:
                if "datavalue" in claims['P570'][0]['mainsnak']:
                    deathdate = claims['P570'][0]['mainsnak']['datavalue']['value']['time'][1:5]
                    self.death = deathdate
            if "P21" in claims:
                if "datavalue" in claims['P21'][0]['mainsnak']:
                    gender = claims['P21'][0]['mainsnak']['datavalue']['value']['id']
                    if gender == 'Q6581097':
                        self.sex = "m"
                    if gender == 'Q6581072':
                        self.sex = "f"
                        print("!!female!!")
            if "enwiki" in links:
                self.wikiLink_en = "https://en.wikipedia.org/wiki/"+links['enwiki']['title']
            if "jawiki" in links:
                self.wikiLink_ja = "https://ja.wikipedia.org/wiki/" + links['jawiki']['title']


    def getAuthorityIDs(self):
        if self.viaf is not None:
            data = getUrlDataAsString("http://viaf.org/viaf/"+self.viaf + "/justlinks.json")

            if data is not None:
                links = json.loads(data)
                if "NDL" in links:
                    self.ndl = links["NDL"][0]
                    self.possibleEntries += 1
                    print(self.ndl)
                if "WKP" in links:
                    self.wkp = links["WKP"][0]
                    print(self.wkp)
                if "NII" in links:
                    self.nii = links["NII"][0]
                    print(self.nii)

                self.numberLinks = len(links)
