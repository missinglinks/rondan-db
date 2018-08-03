from .ndl import getLabel
from .viaf import getViafMatch, getAuthorityIds
from .wikidata import getPersonInfos
from .kotobank import getKotobankEntries


def get_person_data(viaf):

    #print("\t get authority ids")
    ids = getAuthorityIds(viaf["viaf_id"])
    #print("\t get wiki info")
    wiki = getPersonInfos(ids["wkp"])
    #print("\t check kotobank entries")
    #kotobank = getKotobankEntries(viaf["names"][0])
    person_data = {
        "id": viaf["viaf_id"],
        "viaf": viaf,
        "ids": ids,
        "wiki": wiki,
        #"kotobank": kotobank
    }
    return person_data


