import couchdb
from tqdm import tqdm 
from tools.config import COUCH_SERVER
from tools.ndl import getLabel
from tools.viaf import getViafMatch, getAuthorityIds
from tools.wikidata import getPersonInfos
from tools.kotobank import getKotobankEntries
import time
import json
import os

DATA_DIR = "data/ndl"


couch = couchdb.Server(COUCH_SERVER)

cinii = couch["rondan_ndldc"]

try:
    persons_db = couch["rondan_persons"]
except:
    persons_db = couch.create("rondan_persons")

person_list = [doc for doc in persons_db]

for doc in cinii:

    mag_filepath = os.path.join(DATA_DIR, "{}.json".format(doc))

    done = False
    while not done:
        try:
            if os.path.exists(mag_filepath):
                with open(mag_filepath) as f:
                    mag = json.load(f)  
            else:
                mag = cinii[doc]
            done = True
        except:
            print("... db reading failed, retry ...")
            time.sleep(1)

    
    print(mag["_id"])
    for issue in tqdm(mag["issues"]):
        changed = False
        for article in issue["toc"]:
            

            if "authors_viaf" not in article:

                authors = []
                for author in article["authors"]:
                    #print("mine ... "+author["name"])
                    name = author
                    
                    #print("\t check viaf")
                    if name:

                        if "#" in name:
                            name = name.split("#")[0]

                        viaf = getViafMatch(name)
                        if viaf:
                            if viaf["viaf_id"] not in person_list:

                                #print("\t get authority ids")
                                ids = getAuthorityIds(viaf["viaf_id"])
                                #print("\t get wiki info")
                                wiki = getPersonInfos(ids["wkp"])
                                #print("\t check kotobank entries")
                                kotobank = getKotobankEntries(viaf["names"][0])
                                inserted = False
                                while not inserted:
                                    try:
                                        persons_db.save({
                                            "_id": viaf["viaf_id"],
                                            "viaf": viaf,
                                            "ids": ids,
                                            "wiki": wiki,
                                            "kotobank": kotobank
                                        })
                                        inserted = True
                                    except:
                                        print("... db insert failed, retry ...")
                                        time.sleep(1)

                                person_list.append(viaf["viaf_id"])
                        authors.append({"name": name, "viaf": viaf})
                        
                changed = True
                article["authors_viaf"] = authors

        #if changed:
        
        with open(mag_filepath, "w") as f:
            json.dump(mag, f, indent=4)
            
            """
            try:
                cinii.save(mag)
            except:
                print("... db insert failed, retry ...")
                time.sleep(1)    
            """
            