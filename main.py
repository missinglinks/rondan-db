from tools.ndl import getLabel
from tools.viaf import getViafMatch, getAuthorityIds
from tools.wikidata import getPersonInfos
from tools.kotobank import getKotobankEntries

viaf = getViafMatch("浅田彰")
print(viaf)
ids = getAuthorityIds(viaf["viaf_id"])
print(ids)
print(getLabel(ids["ndl"]))

wiki = getPersonInfos(ids["wkp"])
print(wiki)

print(getKotobankEntries("浅田彰"))