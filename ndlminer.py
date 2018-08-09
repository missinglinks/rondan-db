from rondan.magazines import ndldc_issues


mags = [
    ["思想","岩波書店"],
    ["世界","岩波書店"],
    ["現代思想","青土社"],    
    ["文芸春秋","文芸春秋"],
    ["文化評論","新日本出版社"],
    ["中央公論","中央公論新社"],
    ["インパクション","インパクト"],
    ["ユリイカ","青土社"],
    ["諸君","文芸春秋"],
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
    magazine = []  
    mag_id = "{}.{}".format(mag[0],mag[1])
    if mag_id not in db:


        for year in range(1920, 2017):
            results = ndldc_get_issues(mag[0], mag[1], year, year)

            #print(results)
            magazine += results
            print("\t {} - {}".format(year, len(results)))

#print(articles)