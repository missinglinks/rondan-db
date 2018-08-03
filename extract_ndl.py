
import couchdb
from tqdm import tqdm 
from tools.config import COUCH_SERVER
import json
import os
import time

couch = couchdb.Server(COUCH_SERVER)

"""
cinii = couch["rondan_ndldc"]

for doc in cinii:
    data = cinii[doc]

    with open("data/ndl/{}.json".format(doc), "w") as f:
        json.dump(data, f, indent=4)
"""

personsdb = couch["rondan_persons"]
persons = []
for doc in tqdm(personsdb):
    persons.append(personsdb[doc])



with open("data/persons.json", "w") as f:
    json.dump(persons, f, indent=4)