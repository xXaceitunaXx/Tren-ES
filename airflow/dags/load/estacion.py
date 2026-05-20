from airflow.sdk import dag, task
from sqlalchemy import MetaData, Table
from utils.utils import connect_database

import csv


@dag(
    dag_id="Warehouse-Estacion",
    tags=["Estacion", "Wikidata", "Renfe", "ETL", "Pipeline"]
)
def warehouse_estacion():

    @task(task_id="Leer-WIKIDATA")
    def read_wikidata():
        with open("resultados/municipios_WIKIDATA.csv") as fichero:
            return list(csv.DictReader(fichero))


    @task(task_id="Leer-WIKIDATA")
    def read_renfe_estaciones():
        with open("resultados/estaciones_Renfe.csv") as fichero:
            return list(csv.DictReader(fichero))


    @task
    def transform_estacion(wikidata, renfe):
        wikidata_index = {m["label"]: m["codigo"] for m in wikidata}

        return [
            {
                "id":        estacion["CODIGO"],
                "nombre":    estacion["DESCRIPCION"],
                "latitud":   float(estacion["LATITUD"]),
                "longitud":  float(estacion["LONGITUD"]),
                "municipio": wikidata_index.get(estacion["POBLACION"]),
            }
            for estacion in renfe
        ]


    @task
    def load(data):
        engine = connect_database()
        with engine.connect() as c:
            tabla = Table("Estacion", MetaData(), autoload_with=engine)
            c.execute(tabla.insert().prefix_with("IGNORE"), data)
            c.commit()


    wikidata = read_wikidata()
    renfe = read_renfe_estaciones()
    transformed_data = transform_estacion(wikidata, renfe)
    load(transformed_data)


warehouse_estacion()