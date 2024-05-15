
import sys
import uuid
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT ?item ?articlename ?itemLabel ?itemDescription ?sl ?random
WHERE {
  VALUES ?dod {"+{%date%}"^^xsd:dateTime}
  ?dod ^wdt:P570 ?item .
  ?item wikibase:sitelinks ?sl .
  ?item ^schema:about ?article .
  ?article schema:isPartOf <https://en.wikipedia.org/>;
          schema:name ?articlename .
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
    ?item rdfs:label ?itemLabel .
    ?item schema:description ?itemDescription .
  }
  BIND(SHA512(CONCAT(STR(RAND()), STR(?item))) AS ?random)
} 
ORDER BY ?random
LIMIT 1
# {%comment%}
"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()



def get_deaths(args, timecrawler):
    
    for day in timecrawler:
        # print(date)
        timestamp = day.timestamp
        results = get_results(endpoint_url, query.replace("{%date%}", timestamp).replace("{%comment%}",str(uuid.uuid4())))

        result = results["results"]["bindings"][0]
        name = result["itemLabel"]["value"]
        uri  = result["item"]["value"]

        day.update_channel("death", [], {
              "name": name,
              "uri": uri,
        })
            


        


    