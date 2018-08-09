#
# Functions for NDL personal data fetching
#
# author: peter.muehleder@uni-leipzig.de
#

from ..utils import get_url_as_json, kana_to_romaji, cap_first_letters, remove_years
import re

PERSON_JSON = "http://id.ndl.go.jp/auth/ndlna/{id}.json"

def get_label(ndl_id):
    romaji = None
    penname = None
    data = get_url_as_json(PERSON_JSON.format(id=ndl_id))

    #check if name is real
    if "realName" in data:
        uri = data["realName"][0]["uri"]
        real_ndl_id = uri.split("/")[-1]
        penname = data["prefLabel"]["litearlForm"]
        data = getUrlAsJson(PERSON_JSON.format(id=real_ndl_id))

    label_lit = data["prefLabel"]["literalForm"]
    try:
        transcription = remove_years(data["prefLabel"]["transcription"])
    except:
        transcription = None
    
    if transcription is not None:
        romaji = cap_first_letters(kana_to_romaji(transcription))

    label = {
        "litearal": remove_years(label_lit),
        "transcription": transcription,
        "romaji": romaji,
        "penname": penname
    }

    return label
