from airflow.sdk import dag, task
from sqlalchemy import MetaData, Table
from utils.utils import connect_database
from geopy.distance import geodesic

import csv

@dag(
    dag_id="Warehouse-Parada",
    tags=["Parada", "Ruta", "Renfe", "Estaciones", "ETL", "Pipeline"]
)
def warehouse_parada():

    @task(task_id="Leer-Renfe-Rutas")
    def read_rutas():
        with open("resultados/rutas_renfe.csv") as fichero:
            return list(csv.DictReader(fichero))

    @task(task_id="Leer-Renfe-Estaciones")
    def read_estaciones():
        with open("resultados/estaciones_Renfe.csv") as fichero:
            return list(csv.DictReader(fichero))

    @task(task_id="Transformar-Paradas")
    def transform_parada(rutas: list, estaciones: list) -> list:
        estacion_index = {e["DESCRIPCION"]: e for e in estaciones}

        resultado = []
        for ruta in rutas:
            paradas = [p.strip() for p in ruta["PARADAS"].split(" | ")]
            estacion_origen = estacion_index.get(paradas[0])

            if estacion_origen is None:
                continue

            coords_origen = (float(estacion_origen["LATITUD"]), float(estacion_origen["LONGITUD"]))

            for n_secuencia, nombre_parada in enumerate(paradas):
                estacion = estacion_index.get(nombre_parada)

                if estacion is None:
                    continue

                coords_parada = (float(estacion["LATITUD"]), float(estacion["LONGITUD"]))
                km_origen = geodesic(coords_origen, coords_parada).km

                resultado.append({
                    "ruta":        ruta["CODIGO"],
                    "estacion":    estacion["CODIGO"],
                    "n_secuencia": n_secuencia,
                    "km_origen":   round(km_origen, 2),
                })

        return resultado

    @task(task_id="Carga-Paradas")
    def load(data: list):
        engine = connect_database()
        with engine.connect() as c:
            tabla = Table("Parada", MetaData(), autoload_with=engine)
            c.execute(tabla.insert().prefix_with("IGNORE"), data)
            c.commit()

    rutas = read_rutas()
    estaciones = read_estaciones()
    load(transform_parada(rutas, estaciones))


warehouse_parada()