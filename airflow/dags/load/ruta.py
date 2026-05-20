from airflow.sdk import dag, task
from sqlalchemy import MetaData, Table
from utils.utils import connect_database

import csv

@dag(
    dag_id="Warehouse-Ruta",
    tags=["Ruta", "Renfe", "Estaciones", "ETL", "Pipeline"]
)
def warehouse_ruta():


    @task(task_id="Leer-Renfe-Ruta")
    def read_ruta_renfe():
        with open("resultados/rutas_renfe.csv") as fichero:
            return list(csv.DictReader(fichero))


    @task(task_id="Leer-Renfe-Estaciones")
    def read_renfe_estaciones():
        with open("resultados/estaciones_Renfe.csv") as fichero:
            return list(csv.DictReader(fichero))


    @task(task_id="Transformar-Renfe-Rutas")
    def transform_ruta(rutas, estaciones):

        estacion_index = {e["DESCRIPCION"]: e["CODIGO"] for e in estaciones}

        resultado = []
        for ruta in rutas:
            paradas = [p.strip() for p in ruta["PARADAS"].split(" | ")]
            origen  = estacion_index.get(paradas[0])
            destino = estacion_index.get(paradas[-1])

            if origen is None or destino is None:
                continue

            resultado.append({
                "id":      ruta["CODIGO"],
                "origen":  origen,
                "destino": destino,
                "tipo":    ruta["TIPO"],
            })

        return resultado


    @task(task_id="Carga-Renfe-Rutas")
    def load(data):
        engine = connect_database()
        with engine.connect() as c:
            tabla = Table("Ruta", MetaData(), autoload_with=engine)
            c.execute(tabla.insert().prefix_with("IGNORE"), data)
            c.commit()


    rutas = read_ruta_renfe()
    estaciones = read_renfe_estaciones()
    data = transform_ruta(rutas, estaciones)
    load(data)


warehouse_ruta()