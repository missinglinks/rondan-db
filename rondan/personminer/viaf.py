#
# Functions for Viaf data fetching
#
# author: peter.muehleder@uni-leipzig.de
#

from ..utils import get_url_as_json, similar

VIAF_URL = 'http://www.viaf.org/viaf/search?query=local.personalNames+all+"{name}"&maximumRecords=50&httpAccept=application/json&recordSchema=info:srw/schema/1/briefmarcxml-v1.1&sortKeys=holdingscount'
VIAF_LINKS = "http://viaf.org/viaf/{id}/justlinks.json"


# Search viaf.org for a Name and returns the best match (based on name similarity)
# if more entries match with the same similarity, best match will be based on number of name entries (= number of mentions in national libraries)
def get_viaf_match(name):
    viafs = []
    while True:
        results = getUrlAsJson(VIAF_URL.format(name=name.replace('"', "'")))

        if not results:
            print(name)
            continue
        else:
            if "records" not in results["searchRetrieveResponse"]:
                return None
            else:
                records = results["searchRetrieveResponse"]["records"]
                for record in records:
                    viaf_id = record["record"]["recordData"]["viafID"]
                    birth_date = record["record"]["recordData"]["birthDate"]
                    death_date = record["record"]["recordData"]["deathDate"]
                    headings = record["record"]["recordData"]["mainHeadings"]["mainHeadingEl"]
                    names = []
                    if isinstance(headings, list):
                        for heading in headings:
                            if isinstance(heading["datafield"]["subfield"], list):
                                names.append(heading["datafield"]["subfield"][0]["#text"])
                            else:
                                names.append(heading["datafield"]["subfield"]["#text"])
                    else:
                        if isinstance(headings["datafield"]["subfield"], list):
                            names.append(headings["datafield"]["subfield"][0]["#text"])
                        else:
                            names.append(headings["datafield"]["subfield"]["#text"])
                    names= list(set(names))
                    best_match = 0
                    for viaf_name in names:
                        match = similar(viaf_name, name)
                        if match > best_match:
                            best_match = match

                    viafs.append({
                        "viaf_id": viaf_id,
                        "names": names,
                        "birth_date": birth_date,
                        "death_date": death_date,
                        "match_ratio": best_match
                    })

                viafs.sort(key=lambda x:x["match_ratio"],reverse=True)
                if len(viafs) == 1:
                    return viafs[0]
                elif len(viafs) > 1:
                    best_match = viafs[0]
                    for viaf in viafs:
                        if viaf["match_ratio"] < best_match["match_ratio"]:
                            break
                        if len(viaf["names"]) > len(best_match["names"]):
                            best_match = viaf
                    return best_match
                else:
                    return None


# Get ID from Viaf link list
def get_authority_ids(viaf_id):
    links = {}
    #print(viaf_id)
    links_list = getUrlAsJson(VIAF_LINKS.format(id=viaf_id))
    #print(links_list)

    if type(links_list) == int:
        new_id = str(links_list).replace(str(viaf_id),"").strip()
        print(new_id)
        links_list =  getUrlAsJson(VIAF_LINKS.format(id=new_id))


    if links_list is not None:
        if "viafID" in links_list:
            links["viaf"] = links_list["viafID"]
        else:
            links["viaf"]  = None
        if "NDL" in links_list:
            links["ndl"] = links_list["NDL"][0]
        else:
            links["ndl"]  = None
        if "WKP" in links_list:
            links["wkp"]  = links_list["WKP"][0]
        else:
            links["wkp"]  = None
        if "NII" in links_list:
            links["nii"]  = links_list["NII"][0]
        else:
            links["nii"]  = None
        if "Wikipedia" in links_list:
            links["wikipedia"] = links_list["Wikipedia"]
        else:
            links["wikipedia"] = None
    return links            
