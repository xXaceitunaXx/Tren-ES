import requests

WIKIDATA_URL = "https://query.wikidata.org/sparql"

query = """
SELECT ?codigo ?label ?poblacion ?coordenadas WHERE {
  ?municipio (wdt:P31/(wdt:P279*)) wd:Q2074737;
    wdt:P772 ?codigo.
  ?municipio wdt:P1082 ?poblacion.
  ?municipio wdt:P625 ?coordenadas.
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "es".
    ?municipio rdfs:label ?label.
  }
}
"""

response = requests.get(WIKIDATA_URL, params={"query": query})