
import sys
import uuid
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from io import BytesIO
from PIL import Image
import json
from pathlib import Path
endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT ?item ?articlename ?itemLabel ?itemDescription ?sl ?random
WHERE {
  VALUES ?dod {"+{%date%}"^^xsd:dateTime}
  ?dod ^wdt:P585 ?item .
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

def get_image(uri):
    wikidata_id = uri.split("/")[-1]
    wikidata_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={wikidata_id}&format=json&props=sitelinks"
    response = requests.get(wikidata_url)
    data = response.json()

    wikipedia_title = data['entities'][wikidata_id]['sitelinks'].get('enwiki', {}).get('title')
    if not wikipedia_title:
        return None, None

    wikipedia_api_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={wikipedia_title}&format=json&prop=pageimages&pithumbsize=300"
    response = requests.get(wikipedia_api_url)
    pages = response.json()['query']['pages']

    image_url = None
    for page_id in pages:
      page = pages[page_id]
      image_url = page.get('thumbnail', {}).get('source')
      if image_url:
        break

    if not image_url:
      return None, None
    
    response = requests.get(image_url, headers={'User-Agent': 'Mozilla/5.0'})

    if response.status_code != 200:
      raise Exception(f"Failed to fetch image: {response.status_code}")


    img = Image.open(BytesIO(response.content))
    return img, image_url



def get_events(args, timecrawler):
    
    for day in timecrawler:
        timestamp = day.timestamp
        results = get_results(endpoint_url, query.replace("{%date%}", timestamp).replace("{%comment%}",str(uuid.uuid4())))
        # print(json.dumps(results, indent=2))
        try:
          result = results["results"]["bindings"][0]
          name   = result["itemLabel"]["value"]
          # description = result["itemDescription"]["value"]
          uri  = result["item"]["value"]

          image, image_url = get_image(uri)
        except Exception as e:
           print(e)
           continue

        if image is not None:
          ext = image_url.split(".")[-1]
          img_path = Path(day.directory, f"event.{ext}")
          image.save(img_path)

          print(f"{day.timestamp} - got image")
          day.update_channel("event", [img_path], {
                "name": name,
                "uri": uri,
                # "description": description,
                "image_url" : image_url,
          })
        else:
          print(f"{day.timestamp} - no image")

          day.update_channel("event", [], {
                "name": name,
                "uri": uri,
                # "description": description,
                "image_url" : None,
          })


            


        


    