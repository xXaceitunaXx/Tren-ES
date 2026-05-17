from airflow.sdk import dag, task
from airflow.sensors.external_task import ExternalTaskSensor
from pendulum import datetime

import requests
import csv


INE_REQUEST_URL = "https://servicios.ine.es/wstempus/js/ES/VALORES_VARIABLE"
WIKIDATA_URL = "https://query.wikidata.org/sparql"
RENFE_SQL_URL = 'https://data.renfe.com/api/3/action/datastore_search_sql'


def to_csv(path, data):
    keys = data[0].keys()
    with open(path, "w", encoding="utf-8") as fichero:
        writer = csv.DictWriter(fichero, keys)
        writer.writeheader()
        writer.writerows(data)

@dag(
    dag_id="Municipio-WIKIDATA",
    tags=["pipeline", "Wikidata", "Municipios", "Tren-ES", "Población", "Geografía"],
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
                "label": item["label"]["value"],
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


@dag(
    dag_id="Municipio-INE",
    tags=["pipeline", "INE", "Municipios", "Tren-ES", "Códigos", "CCAA"],
    start_date=datetime(2026, 1, 1),
    schedule="@yearly"
)
def extraccion_INE_municipio():

    INE_MUNICIPIOS = "19"

    @task(task_id="Extracción-Municipio-INE")
    def extract():
        print(f"Request {INE_REQUEST_URL}/{INE_MUNICIPIOS}")
        municipios_response = requests.get(f"{INE_REQUEST_URL}/{INE_MUNICIPIOS}")
        print(f"Query response recived in {municipios_response.elapsed}" if municipios_response else "Query error")
        municipios_json = municipios_response.json()

        return municipios_json


    @task(task_id="Transformación-Municipio-INE")
    def transform(data):
        municipios = [
            {
                "CMUN": m["Codigo"][2:5],
                "CPRO": m["Codigo"][0:2],
                "NOMBRE": m["Nombre"]
            }
            for m in data
        ]
        
        print("Data object generated")
        
        return municipios


    @task(task_id="Carga-Municipio-INE")
    def load(data):
        path = "resultados/municipios_INE.csv"
        print(f"Guardando resultados en {path}")
        to_csv(path, data)


    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)


@dag(
    dag_id="Provincia-INE",
    tags=["pipeline", "INE", "Provincias", "Tren-ES", "Códigos", "CCAA"],
    start_date=datetime(2026, 1, 1),
    schedule="@yearly"
)
def extraccion_INE_provincias():
    INE_PROVINCIAS = "115"
    
    @task(task_id="Extracción-Provincia-INE")
    def extract():
        print(f"Request {INE_REQUEST_URL}/{INE_PROVINCIAS}?det=2")
        provincias_response = requests.get(f"{INE_REQUEST_URL}/{INE_PROVINCIAS}?det=2")
        print(f"Query response recived in {provincias_response.elapsed}" if provincias_response else "Query error")
        provincias_json = provincias_response.json()
        
        return provincias_json


    @task(task_id="Transformación-Provincia-INE")
    def transform(data):
        provincias = [
            {
                "CPRO": p["Codigo"], 
                "NOMBRE": p["Nombre"], 
                "CODAUTO": p["JerarquiaPadres"][0]["Codigo"],
                "CCAA": p["JerarquiaPadres"][0]["Nombre"].split(",")[0]
            }
            for p in data
            if p["Codigo"] and int(p["Codigo"]) in range(1, 50)
        ]
        
        print("Data object generated")
        
        return provincias


    @task(task_id="Carga-Provincia-INE")
    def load(data):
        path = "resultados/provincias_INE.csv"
        print(f"Guardando resultados en {path}")
        to_csv(path, data)


    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)


@dag(
    dag_id="Estación-Renfe",
    tags=["pipeline", "INE", "Estaciones", "Tren-ES", "Renfe"],
    start_date=datetime(2026, 1, 1),
    schedule="@yearly"
)
def extraccion_Renfe_estacion():

    query = """
    SELECT "_id" as "ID", "CODIGO", "DESCRIPCION", "LATITUD", "LONGITUD", "DIRECION" as "DIRECCION", "CP", "POBLACION", "PROVINCIA", "PAIS"
    FROM "783e0626-6fa8-4ac7-a880-fa53144654ff" 
    WHERE "FEVE" = 'NO'
    """


    @task(task_id="Extracción-Estación-Renfe")
    def extract():
        print(f"Request {RENFE_SQL_URL}:\n{query}")
        response = requests.get(RENFE_SQL_URL, params={"sql": query})
        print(f"Query response recived in {response.elapsed}" if response else "Query error")
        
        return response.json()


    @task(task_id="Transformación-Estación-Renfe")
    def transform(data):
        resultados = data.get("result", {}).get("records", [])
        
        return [res for res in resultados if all(res.values())]


    @task(task_id="Carga-Estación-Renfe")
    def load(data):
        path = "resultados/estaciones_Renfe.csv"
        print(f"Guardando resultados en {path}")
        to_csv(path, data)


    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)


@dag(
    dag_id="Horario-Ruta-Renfe",
    tags=["pipeline", "INE", "Rutas", "Horarios", "Tren-ES", "Renfe", "Mortal"],
    start_date=datetime(2026, 1, 1),
    schedule="@yearly"
)
def extraccion_Renfe_horarios_rutas():

    subset_municipios = [
        "10504", # Viana de Cega
        "10602", # Cabezón
        "10610", # Valladolid Universidad
        "10600", # Valladolid Campo Grande
        "14100", # Palencia
    ]

    # TODO: Terminar este dag XD

    @task(task_id="Extracción-Horario-Renfe")
    def extract():
        return "Hola amigo"


    raw_data = extract()


extraccion_municipio()
extraccion_INE_municipio()
extraccion_INE_provincias()
extraccion_Renfe_estacion()
extraccion_Renfe_horarios_rutas()