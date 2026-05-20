from airflow.sdk import dag, task
from pendulum import datetime
from utils.utils import to_csv, normalize_unicode

import requests


WIKIDATA_URL = "https://query.wikidata.org/sparql"


@dag(
    dag_id="Municipio-WIKIDATA",
    tags=["Wikidata", "Municipios", "Tren-ES", "Población", "Geografía"],
    start_date=datetime(2026, 1, 1),
    schedule="@monthly"
)
def extraccion_municipio():

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

    @task(task_id="Extracción-WIKIDATA")
    def extract():
        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "Tren-ES/0.1",
        }

        print(f"Request {WIKIDATA_URL}:\n{query}")

        response = requests.get(
            WIKIDATA_URL,
            params={"query": query, "format": "json"},
            headers=headers,
            timeout=60,
        )
        
        print(f"Query response recived in {response.elapsed}" if response else "Query error")

        return response.json()


    @task(task_id="Transformación-WIKIDATA")
    def transform(data):
        rows = [
            {
                "codigo": item["codigo"]["value"],
                "label": normalize_unicode(item["label"]["value"]),
                "poblacion": int(float(item["poblacion"]["value"])),
                "coordenadas": item["coordenadas"]["value"],
            }
            for item in data["results"]["bindings"]
        ]
        
        print("Data object generated")
        
        return rows


    @task(task_id="Carga-WIKIDATA")
    def load(data):
        path = "resultados/municipios_WIKIDATA.csv"
        print(f"Storing data in {path}")
        to_csv(path, data)


    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)



extraccion_municipio()
