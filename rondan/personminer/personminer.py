from .ndl import get_label
from .viaf import get_viaf_match, get_authority_ids
from .wikidata import get_person_infos
from .kotobank import get_kotobank_entries


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


