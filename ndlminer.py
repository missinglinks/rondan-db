from rondan.magazines import ndldc_issues
from pit.prov import Provenance
import pandas as pd
import json
import os

MAGAZINE_FILE = "data/magazines.csv"

OUT_DIR = "data/ndl"

def load_magazines():
    magazines = pd.read_csv(MAGAZINE_FILE)
    #remove brackets from titles
    magazines["title"] = magazines["title"].apply(lambda x: str(x).replace("『", "").replace("』", ""))
    magazines["until"] = magazines["until"].fillna(2015)
    return json.loads(magazines.to_json(orient="records"))

def is_dataset_available(title, publisher):
    filename =  os.path.join(OUT_DIR, "{}_{}.json".format(title, publisher))
    if os.path.exists(filename):
        return True
    else:
        return False

def filter_magazines(magazines):
    for mag in magazines:
        if mag["use"] == "y":
            if not is_dataset_available(mag["title"], mag["publisher"]):
                yield mag

def check_availability(magazines):
    for mag in filter_magazines(magazines):
        data = []
        print(mag["title"])
        #print(mag["from"], mag["until"])
        for year in range(int(mag["from"]), int(mag["until"])):
            print(year)
            results = ndldc_issues(mag["title"], mag["publisher"], year, year)
            data += results
            print(" ")

        if len(data) > 0:
            filename = os.path.join(OUT_DIR, "{}_{}.json".format(mag["title"], mag["publisher"]))
            json.dump(data, open(filename, "w"), indent=4)





def main():
    magazines = load_magazines()
    check_availability(magazines)


if __name__ == "__main__":
    main()





# mags = [
#     ["思想","岩波書店"],
#     ["世界","岩波書店"],
#     ["現代思想","青土社"],    
#     ["文芸春秋","文芸春秋"],
#     ["文化評論","新日本出版社"],
#     ["中央公論","中央公論新社"],
#     ["インパクション","インパクト"],
#     ["ユリイカ","青土社"],
#     ["諸君","文芸春秋"],
#     ["海","中央公論社"],
#     ["創","創出版"],
#     ["文学","岩波書店"],
#     ["朝日ジャーナル",""],
#     ["現代の理論",""],
#     ["群像","講談社"],
#     ["文芸","河出書房"],
#     ["文學界","文芸春秋"],
#     ["すばる","集英社"],
#     ["文化評論","新日本文学会"],
#     ["新日本文学","新日本文学会"],
#     ["前衛","日本共産党"],
#     ["公明","公明"]
# ]


# for mag in mags:
#     print("mining {}".format(mag[0]))
#     magazine = []  
#     mag_id = "{}.{}".format(mag[0],mag[1])
#     if mag_id not in db:


#         for year in range(1920, 2017):
#             results = ndldc_get_issues(mag[0], mag[1], year, year)

#             #print(results)
#             magazine += results
#             print("\t {} - {}".format(year, len(results)))

# #print(articles)