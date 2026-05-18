from airflow.sdk import dag, task
from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine, MetaData, Table

import csv

@dag(dag_id="Warehouse-Municipio")
def warehouse_municipio():
    
    @task(task_id="Leer-WIKIDATA")
    def read_wikidata():
        with open("resultados/municipios_WIKIDATA.csv") as fichero:
            return list(csv.DictReader(fichero))


    @task(task_id="Leer-INE-Municipio")
    def read_ine_mun():
        with open("resultados/municipios_INE.csv") as fichero:
            return list(csv.DictReader(fichero))


    @task(task_id="Leer-INE-Provincia")
    def read_ine_prov():
        with open("resultados/provincias_INE.csv") as fichero:
            return list(csv.DictReader(fichero))


    @task(task_id="Transformar-Municipio")
    def transform_municipio(wikidata, ine_municipios, ine_provincias):
        ine_mun_index = {m["CPRO"] + m["CMUN"]: m for m in ine_municipios}
        ine_prov_index = {p["CPRO"]: p for p in ine_provincias}

        municipios = []
        for m in wikidata:
            ine_mun = ine_mun_index.get(m["codigo"])
            if ine_mun is None:
                continue

            ine_prov = ine_prov_index.get(ine_mun["CPRO"])
            if ine_prov is None:
                continue

            municipios.append({
                "id":           m["codigo"],
                "nombre":       m["label"],
                "n_habitantes": m["poblacion"],
                "latitud":      m["coordenadas"].replace("Point(", "").replace(")", "").split()[0],
                "longitud":     m["coordenadas"].replace("Point(", "").replace(")", "").split()[1],
                "provincia":    ine_prov["NOMBRE"],
                "ccaa":         ine_prov["CCAA"],
            })

        return municipios


    @task(task_id="Carga-Municipio")
    def load(data):
        conn = BaseHook.get_connection("warehouse_mariadb")
        engine = create_engine(f"mysql+pymysql://{conn.login}:{conn.password}@{conn.host}/{conn.schema}")
        with engine.connect() as c:
            tabla = Table("municipio", MetaData(), autoload_with=engine)
            c.execute(tabla.insert().prefix_with("IGNORE"), data)
            c.commit()


    wikidata = read_wikidata()
    ine_mun = read_ine_mun()
    ine_prov = read_ine_prov()
    data = transform_municipio(wikidata, ine_mun, ine_prov)
    load(data)


warehouse_municipio()