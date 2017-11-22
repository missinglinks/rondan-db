from tools.cinii import getArticles
import couchdb
from tools.config import COUCH_SERVER

couch = couchdb.Server(COUCH_SERVER)
try:
    db = couch["rondan_cinii"]
except:
    db = couch.create("rondan_cinii")


mags = [
    ["思想","岩波書店"],
    ["世界","岩波書店"],
    ["現代思想","青土社"],    
    ["文芸春秋","文芸春秋"],
    ["文化評論","新日本出版社"],
    ["中央公論","中央公論新社"],
    ["インパクション","インパクト"],
    ["ユリイカ","青土社"],
    ["海","中央公論社"],
    ["創","創出版"],
    ["文学","岩波書店"],
    ["朝日ジャーナル",""],
    ["現代の理論",""],
    ["群像","講談社"],
    ["文芸","河出書房"],
    ["文學界","文芸春秋"],
    ["すばる","集英社"],
    ["文化評論","新日本文学会"],
    ["新日本文学","新日本文学会"],
    ["前衛","日本共産党"],
    ["公明","公明"]
]


for mag in mags:
    print("mining {}".format(mag[0]))
    articles = []  
    mag_id = "{}.{}".format(mag[0],mag[1])
    if mag_id not in db:
        year_min = None
        year_max = None
        first = True

        for year in range(1945, 2017):
            results = getArticles(mag[0], mag[1], year, year)
            if len(articles) > 0:
                if first:
                    year_min = year
                    first = False
                year_max = year
            articles += results
            print("{} - {}".format(year, len(results)))


        if articles != []:
            db.save(
                {
                    "_id": mag_id,
                    "magazine": mag[0],
                    "publisher": mag[1],
                    "articles": articles,
                    "year_from": year_min,
                    "year_to": year_max
                }
            )

#print(articles)