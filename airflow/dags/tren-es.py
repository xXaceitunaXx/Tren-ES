from airflow.sdk import dag, task
from airflow.sensors.external_task import ExternalTaskSensor

from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup

from pendulum import datetime, now
from itertools import permutations

import requests
import pendulum
import csv


INE_REQUEST_URL = "https://servicios.ine.es/wstempus/js/ES/VALORES_VARIABLE"
WIKIDATA_URL = "https://query.wikidata.org/sparql"
RENFE_SQL_URL = 'https://data.renfe.com/api/3/action/datastore_search_sql'
RENFE_HORARIOS_URL = "https://www.renfe.com/es/es/viajar/informacion-util/horarios"
RENFE_RUTA_URL = "https://horarios.renfe.com/HIRRenfeWeb"


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
    tags=["pipeline", "Renfe", "Tren-ES"],
    start_date=datetime(2026, 1, 1),
    schedule="@daily"
)
def extraccion_Renfe_horarios_rutas():

    ESTACIONES = [
#        "10504",  # Viana de Cega
#        "10602",  # Cabezón
#        "10610",  # Valladolid Universidad
        "10600",  # Valladolid Campo Grande
        "14100",  # Palencia
    ]

    FECHAS = [
        (f"{d.day:02}", f"{d.month:02}", str(d.year))
        for d in [now().add(days=i) for i in range(1)]
    ]

    COMBINACIONES = [
        (origen, destino, *fecha)
        for origen, destino in permutations(ESTACIONES, 2)
        for fecha in FECHAS
    ]


    def extraer_linea(page, url):
        soup = BeautifulSoup(page.goto(url).text(), "html.parser")

        filas = soup.find_all("tr", class_="irf-renfe-travel__tr")
        paradas = []
        salida = None
        llegada = None

        for fila in filas:
            celdas = fila.find_all("td", class_="txt_gral")
            if not celdas:
                continue
            estacion, hora_salida, hora_llegada = celdas[:3]
            paradas.append(estacion.get_text(strip=True))
            if salida is None and hora_salida.get_text(strip=True):
                salida = hora_salida.get_text(strip=True)
            if hora_llegada.get_text(strip=True):
                llegada = hora_llegada.get_text(strip=True)

        return {"paradas": paradas, "salida": salida, "llegada": llegada}


    def calcular_duracion(salida, llegada):
        t_salida = pendulum.from_format(salida, "HH.mm")
        t_llegada = pendulum.from_format(llegada, "HH.mm")

        if t_llegada < t_salida:
            t_llegada = t_llegada.add(days=1)

        horas, resto = divmod((t_llegada - t_salida).seconds, 3600)
        return f"{horas}h {resto // 60:02}min"


    def extraer_resultado(page, origen, destino, dia, mes, agno) -> tuple[list, list]:
        page.goto(RENFE_HORARIOS_URL)
        frame = page.frame_locator("#ContenidoPrincipal")

        frame.locator("select#O").select_option(value=origen)
        frame.locator("select#D").select_option(value=destino)
        frame.locator("select#DF").select_option(value=dia)
        frame.locator("select#MF").select_option(value=mes)
        frame.locator("select#AF").select_option(value=agno)
        frame.locator('button[title="BUSCAR"]').click()
        frame.locator("tr.odd.irf-travellers-table__tr").first.wait_for(timeout=10000)

        soup = BeautifulSoup(frame.locator("body").inner_html(), "html.parser")
        trenes = soup.find_all("tr", class_="odd irf-travellers-table__tr")

        rutas, horarios = [], []

        for tren in trenes:
            celda = tren.find("td", class_="txt_borde1")
            tipo, numero = celda.get_text(strip=True).split()[:2]
            enlace = celda.find("a")["href"]

            url = f"{RENFE_RUTA_URL}/{enlace.split(chr(34))[1].replace(' ', '%20').replace(chr(10), '')}"
            linea = extraer_linea(page, url)

            rutas.append((" | ".join(linea["paradas"]), tipo, numero))
            horarios.append((tipo, linea["salida"], linea["llegada"], calcular_duracion(linea["salida"], linea["llegada"])))

        return rutas, horarios


    @task(task_id="Extracción-Horario-Ruta-Renfe")
    def extract():
        with sync_playwright() as p:
            page = p.chromium.launch(headless=True).new_page()
            return [extraer_resultado(page, *c) for c in COMBINACIONES]


    @task(task_id="Transformación-Horario-Ruta-Renfe")
    def transform(data):
        rutas = [ruta for rutas, _ in data for ruta in rutas]
        horarios = [horario for _, horarios in data for horario in horarios]
        return {"rutas": rutas, "horarios": horarios}


    @task(task_id="Carga-Ruta-Renfe")
    def load_rutas(data: dict):
        rutas = [
            {
                "CODIGO": ruta[1],
                "TIPO": ruta[2],
                "PARADAS": ruta[0],
            }
            for ruta in data["rutas"]
        ]
        to_csv("resultados/rutas_renfe.csv", rutas)


    @task(task_id="Carga-Horario-Renfe")
    def load_horarios(data: dict):
        horarios = [
            {
                "RECORRIDO": horario[0],
                "SALIDA": horario[1],
                "LLEGADA": horario[2],
                "DURACION": horario[3],
            }
            for horario in data["horarios"]
        ]
        to_csv("resultados/horarios_renfe.csv", horarios)


    raw_data = extract()
    transformed_data = transform(raw_data)
    load_rutas(transformed_data)
    load_horarios(transformed_data)

extraccion_municipio()
extraccion_INE_municipio()
extraccion_INE_provincias()
extraccion_Renfe_estacion()
extraccion_Renfe_horarios_rutas()