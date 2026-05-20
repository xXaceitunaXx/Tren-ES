from airflow.sdk import dag, task
from pendulum import datetime
from utils.utils import to_csv, normalize_unicode

import requests


INE_REQUEST_URL = "https://servicios.ine.es/wstempus/js/ES/VALORES_VARIABLE"


@dag(
    dag_id="Municipio-INE",
    tags=["INE", "Municipios", "Tren-ES", "Códigos"],
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
                "NOMBRE": normalize_unicode(m["Nombre"])
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
    tags=["INE", "Provincias", "Tren-ES", "CCAA"],
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


extraccion_INE_municipio()
extraccion_INE_provincias()