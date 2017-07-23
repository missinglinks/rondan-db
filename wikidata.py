import urllib, json
from urllib.error import HTTPError, URLError

def getUrlDataAsString(url):
    try:
        xfile = urllib.request.urlopen(url)
        data = xfile.read().decode("utf-8")
        xfile.close()
        return data
    except HTTPError:
        return None
    except URLError:
        return None

class WikidataHelper:
    def getJson(self,id):
        url = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids=' + id + '&languages=en|ja|de&format=json'
        data = getUrlDataAsString(url)
        if data is not None:
            return json.loads(data)
        else:
            return None

    def getLabel(self, id, lang):
        wikidata = self.getJson(id)
        if wikidata is not None:
            labels = wikidata['entities'][id]['labels']
            if lang in labels:
                return labels[lang]['value']
            else:
                return None