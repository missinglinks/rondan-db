from ..utils import get_url_as_json

ARTICLE_URL = 'http://ci.nii.ac.jp/opensearch/search?count=200&start={offset}&lang=ja&journal={magazine}&issn=&publisher={publisher}&year_from={year_from}&year_to={year_to}&format=json&appid=upmkTSWtpQK7f9LqGpTg'


def cinii_articles(magazine, publisher, year_from, year_to):
    
    articles = []
    offset = 0

    while True:
        results = getUrlAsJson(ARTICLE_URL.format(
            offset=offset,
            magazine=magazine,
            publisher=publisher,
            year_from=year_from,
            year_to=year_to
        ))

        if "items" in results["@graph"][0]:
            article_list = results["@graph"][0]["items"]
        else:
            article_list = []
        total = int(results["@graph"][0]["opensearch:totalResults"])

        for article in article_list:
            title = article["title"]
            date = article["dc:date"]
            year = int(date.split("-")[0])
            try:
                month = int(date.split("-")[1])
            except:
                month = 0
            link = article["@id"]
            authors = [{"name": author["@value"], "id": ""} for author in article["dc:creator"]]
            try:
                vol = article["prism:number"]
            except:
                vol = None
            try:
                page_from = article["prism:startingPage"]
            except:
                page_from = None
            try:
                page_to = article["prism:endingPage"]
            except:
                page_to = None

            articles.append({
                "title": title,
                "magazine": magazine,
                "publisher": publisher,
                "volume": vol,
                "authors": authors,
                "year": year,
                "month": month,
                "page_from": page_from,
                "page_to": page_to,
                "source": "cinii",
                "link": link
            })
        
        offset += 200
        if offset > total:
            break
        
    return articles

