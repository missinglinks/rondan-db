#
# Functions for NDL personal data fetching
#
# author: peter.muehleder@uni-leipzig.de
#

from ..utils import getUrlAsJson, kanaToRomaji
import re

PERSON_JSON = "http://id.ndl.go.jp/auth/ndlna/{id}.json"
YEAR_REGEX = r', [0-9]{4}.*'


def __capFirstLetters(st):
    st = st.title()
    # create character list
    new_st = list(st)
    # look up positions of ' character in string
    positions = [m.start() for m in re.finditer("'", st)]
    # lower the character after ' in string list
    for position in positions:
        if position < len(st):
            new_st[position+1] = new_st[position+1].lower()
    # convert list to string and return string
    return "".join(new_st)

def __removeYears(label):
    label = re.sub(YEAR_REGEX,"",label)
    return label

def getLabel(ndl_id):
    romaji = None
    penname = None
    data = getUrlAsJson(PERSON_JSON.format(id=ndl_id))

    #check if name is real
    if "realName" in data:
        uri = data["realName"][0]["uri"]
        real_ndl_id = uri.split("/")[-1]
        penname = data["prefLabel"]["litearlForm"]
        data = getUrlAsJson(PERSON_JSON.format(id=real_ndl_id))

    label_lit = data["prefLabel"]["literalForm"]
    try:
        transcription = __removeYears(data["prefLabel"]["transcription"])
    except:
        transcription = None
    
    if transcription is not None:
        romaji = __capFirstLetters(kanaToRomaji(transcription))

    label = {
        "litearal": __removeYears(label_lit),
        "transcription": transcription,
        "romaji": romaji,
        "penname": penname
    }

    return label
