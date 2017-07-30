from common import getUrlAsJson

WIKIDATA_URL = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids={id}&languages=en|ja|de&format=json'

class WikidataHelper:

    def __init__(self, wiki_id):
        self.id = wiki_id
        self.data = getUrlAsJson(WIKIDATA_URL.format(id=wiki_id))

    def getLabel(self, lang):
        if self.data is not None:
            labels = self.data['entities'][self.id]['labels']
            if lang in labels:
                return labels[lang]['value']
            else:
                return None

