
from ..utils import get_url_as_soup

KOTOBANK_JINMEI = "https://kotobank.jp/word/{name}?dic=nihonjinmei"

def get_kotobank_entries(name):
    articles = []
    real_name = None
    year_of_birth = None
    year_of_death = None

    yearsbd = None

    url = KOTOBANK_JINMEI.format(name=name)
    soup = get_url_as_soup(url)
    article_set = soup.findAll('article')
    for article in article_set:
        dic = article.find('h2').text
        years = article.find('yearsbd')
        if years is not None and yearsbd is None:
            yearsbd = years.text
        text = article.find('section').text
        articles.append({'dictionary': dic,
                            'entry': text.replace("\n","").strip(),
                            'link': url})

        if "→" in text[0:5]:
            real_name = text.split("→")[1].replace(" ","")
        
    #print(yearsbd)
    if yearsbd is not None:
        tmp = yearsbd.replace("*","").replace("(","").replace(")","")
        tmp = tmp.split("－")
        if len(tmp) > 0:
            try:
                year_of_birth = int(tmp[0])
            except:
                pass
        if len(tmp) > 1:
            try:
                year_of_death = int(tmp[1])
            except:
                pass        

    kotobank = {
        "name": name,
        "articles": articles,
        "real_name": real_name,
        "year_of_birth": year_of_birth,
        "year_of_death": year_of_death
    }
    return kotobank