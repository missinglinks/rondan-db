import couchdb
from tqdm import tqdm 
from tools.config import COUCH_SERVER
from tools.ndl import getLabel
from tools.viaf import getViafMatch, getAuthorityIds
from tools.wikidata import getPersonInfos
from tools.kotobank import getKotobankEntries

couch = couchdb.Server(COUCH_SERVER)

cinii = couch["rondan_cinii"]

try:
    persons_db = couch["rondan_persons"]
except:
    persons_db = couch.create("rondan_persons")


for doc in cinii:
    mag = cinii[doc]
    print(mag["_id"])
    for article in tqdm(mag["articles"]):
        for author in article["authors"]:
            if author["id"] == "":
                #print("mine ... "+author["name"])
                name = author["name"]
                
                #print("\t check viaf")
                if name:
                    viaf = getViafMatch(name)
                    if viaf:
                        if viaf["viaf_id"] not in persons_db:

                            #print("\t get authority ids")
                            ids = getAuthorityIds(viaf["viaf_id"])
                            #print("\t get wiki info")
                            wiki = getPersonInfos(ids["wkp"])
                            #print("\t check kotobank entries")
                            kotobank = getKotobankEntries(viaf["names"][0])
                            persons_db.save({
                                "_id": viaf["viaf_id"],
                                "viaf": viaf,
                                "ids": ids,
                                "wiki": wiki,
                                "kotobank": kotobank
                            })
                        author["id"] = viaf["viaf_id"]
    cinii.save(mag)

            