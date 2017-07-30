from SPARQLWrapper import SPARQLWrapper, JSON

SEARCH_QUERY = """
SELECT ?genderLabel ?place_of_birth ?place_of_birthLabel  ?country ?countryLabel ?educationLabel ?image
WHERE 
{{
  OPTIONAL {{ wd:{id} wdt:P21 ?gender . }}
  OPTIONAL {{ wd:{id} wdt:P19 ?place_of_birth  . }}
  OPTIONAL {{ wd:{id} wdt:P27 ?country  . }}
  OPTIONAL {{ wd:{id} wdt:P69 ?education  . }}
  OPTIONAL {{ wd:{id} wdt:P18 ?image . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
}}
"""

def getPersonInfos(wiki_id):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(SEARCH_QUERY.format(id=wiki_id))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    bindings = results["results"]["bindings"]
    
    gender = None
    image = None
    place_of_birth = None
    country = None
    education = []

    for binding in bindings:
        if "genderLabel" in binding:
            gender = binding["genderLabel"]["value"]
        if "image" in binding:
            image = binding["image"]["value"]
        if "place_of_birth" in binding:
            place_of_birth = {
                "label": binding["place_of_birthLabel"]["value"],
                "wkp": binding["place_of_birth"]["value"].split("/")[-1]
            }
        if "country" in binding:
            country = {
                "label": binding["countryLabel"]["value"],
                "wkp": binding["country"]["value"].split("/")[-1]
            }
        if "educationLabel" in binding:
            education.append(binding["educationLabel"]["value"])
    
    person_info = {
        "gender": gender,
        "image": image,
        "place_of_birth": place_of_birth,
        "country": country,
        "education": education
    }
    return person_info