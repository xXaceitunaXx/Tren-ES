import requests
import csv
import json

WIKIDATA_URL = "https://query.wikidata.org/sparql"

# Consulta para WikiData
query = """
SELECT ?codigo ?label ?poblacion ?coordenadas WHERE {
  ?municipio (wdt:P31/(wdt:P279*)) wd:Q2074737;
    wdt:P772 ?codigo;
    wdt:P1082 ?poblacion;
    wdt:P625 ?coordenadas.

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "es".
    ?municipio rdfs:label ?label.
  }
}
ORDER BY ?codigo
"""

# Importante: sin el User-Agent, Wikidata puede bloquear la consulta
headers = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "Tren-ES/0.1"
}

# Realiza la consulta
response = requests.get(
    WIKIDATA_URL,
    params={"query": query, "format": "json"},
    headers=headers,
    timeout=60
)

data = response.json()

rows = []

# Procesar los resultados
for item in data["results"]["bindings"]:
    rows.append({
        "codigo": item["codigo"]["value"],
        "label": item["label"]["value"],
        "poblacion": int(float(item["poblacion"]["value"])),
        "coordenadas": item["coordenadas"]["value"],
    })

# Guardar como JSON
with open("municipios_wikidata.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

# Guardar como CSV para SQL
with open("municipios_wikidata.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["codigo", "label", "poblacion", "coordenadas"]
    )
    writer.writeheader()
    writer.writerows(rows)