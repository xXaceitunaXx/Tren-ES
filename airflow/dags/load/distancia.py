from airflow.sdk import dag, task
from sqlalchemy import MetaData, Table
from utils.utils import connect_database, SUBSET_ESTACIONES
from itertools import product
from geopy.distance import geodesic

import csv

@dag(
    dag_id="Warehouse-Distancia",
    tags=["Distancia", "Renfe", "ETL", "Pipeline"]
)
def warehouse_distancia():


    def calcular_distancia(estacion_a, estacion_b):
        cords_a = float(estacion_a["LATITUD"]), float(estacion_a["LONGITUD"])
        cords_b = float(estacion_b["LATITUD"]), float(estacion_b["LONGITUD"])
        
        return geodesic(cords_a, cords_b).km


    @task(task_id="Leer-Renfe-Estacion")
    def read_renfe_estaciones():
        with open("resultados/estaciones_Renfe.csv") as fichero:
            return list(csv.DictReader(fichero))


    @task(task_id="Transformar-Distancia")
    def transform_distancia(estaciones):

        pares_estaciones = [
            (a, b) for a, b in product(estaciones, repeat=2) 
            if a["CODIGO"] < b["CODIGO"]
            and a["CODIGO"] in SUBSET_ESTACIONES
            and b["CODIGO"] in SUBSET_ESTACIONES
        ]

        distancias = [
            {
                "estacion1": int(est_a["CODIGO"]),
                "estacion2": int(est_b["CODIGO"]),
                "distancia": calcular_distancia(est_a, est_b)
            }
             for est_a, est_b in pares_estaciones
        ]

        return distancias


    @task(task_id="Carga-Distancias")
    def load(data):
        engine = connect_database()
        with engine.connect() as c:
            tabla = Table("Distancia", MetaData(), autoload_with=engine)
            c.execute(tabla.insert().prefix_with("IGNORE"), data)
            c.commit()


    renfe = read_renfe_estaciones()
    data = transform_distancia(renfe)
    load(data)


warehouse_distancia()