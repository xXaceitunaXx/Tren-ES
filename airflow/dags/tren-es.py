from typing import Any

from airflow.sdk import dag, task
from airflow.providers.standard.operators.empty import EmptyOperator
from pendulum import datetime

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

import csv


BASE_URL_ADIF = "https://www.adif.es/"


@dag(
    dag_id="ADIF_salidas",
    description="DAG para extracción y almacenamiento de horarios de salidas desde ADIF.",
    start_date=datetime(2026, 4, 14),
    schedule=None,
    params={
        "codigo_estacion": "10600-valladolid-c.-g.",
    },
    tags=["tren", "es", "ADIF", "salidas"],
)
def salidas() -> None:
    @task(task_id="resolver_codigo_estacion")
    def resolver_codigo_estacion(**context) -> str:
        dag_run = context.get("dag_run")
        dag_run_conf = getattr(dag_run, "conf", {}) or {}
        codigo = (
            dag_run_conf.get("codigo_estacion") or context["params"]["codigo_estacion"]
        )
        print(codigo)
        return str(codigo)

    @task(task_id="adif_extraer_salidas")
    def salidas_adif(codigo_estacion: Any) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                channel="chromium",
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                locale="es-ES",
            )

            page = context.new_page()
            page.goto(
                f"https://www.adif.es/w/{codigo_estacion}#tab-salidas",
                wait_until="domcontentloaded",
            )

            page.locator('a[href="#tab-salidas"]').click()

            filas_salidas = page.locator("#tab-salidas tbody tr")
            filas_salidas.first.wait_for(state="attached", timeout=20000)
            salidas_html = page.locator("#horas-trenes-estacion-salidas").inner_html()

            return salidas_html

    @task(task_id="extraer_tabla")
    def extraer_tabla(html: str) -> list[dict]:
        tabla = BeautifulSoup(html, "html.parser")
        filas = tabla.find_all("tr")

        lista = [
            {
                "hora_llegada": fila.find("td", {"class": "col-hora"})
                .text.strip()
                .split(),
                "destino": fila.find("td", {"class": "col-destino"}).text.strip(),
                "via": fila.find("td", {"class": "col-via"}).text.strip(),
                "tren": fila.find("td", {"class": "col-tren"}).text.strip(),
            }
            for fila in filas
            if fila.find("td", {"class": "col-hora"}) is not None
        ]

        return lista

    @task(task_id="guardar_csv")
    def guardar(lista: list[dict], codigo_estacion: str) -> None:
        print(lista)

        with open(
            f"./{codigo_estacion.split('-')[0]}_salidas.csv", "w", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(f, fieldnames=lista[0].keys())
            writer.writeheader()
            writer.writerows(lista)

            print(f"CSV guardado en: {f.name}")

    codigo_estacion = resolver_codigo_estacion()
    salidas_html = salidas_adif(codigo_estacion)
    tabla = extraer_tabla(salidas_html)
    guardar_datos = guardar(tabla, codigo_estacion)

    (
        EmptyOperator(task_id="inicio")
        >> codigo_estacion
        >> salidas_html
        >> tabla
        >> guardar_datos
        >> EmptyOperator(task_id="fin")
    )


@dag(
    dag_id="ADIF_llegadas",
    description="DAG para extracción y almacenamiento de horarios de llegadas desde ADIF.",
    start_date=datetime(2026, 4, 14),
    schedule=None,
    params={
        "codigo_estacion": "10600-valladolid-c.-g.",
    },
    tags=["tren", "es", "ADIF", "llegadas"],
)
def llegadas() -> None:
    @task(task_id="resolver_codigo_estacion")
    def resolver_codigo_estacion(**context) -> str:
        dag_run = context.get("dag_run")
        dag_run_conf = getattr(dag_run, "conf", {}) or {}
        codigo = (
            dag_run_conf.get("codigo_estacion") or context["params"]["codigo_estacion"]
        )
        print(codigo)
        return str(codigo)

    @task(task_id="adif_extraer_llegadas")
    def llegadas_adif(codigo_estacion: Any) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                channel="chromium",
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                locale="es-ES",
            )

            page = context.new_page()
            page.goto(
                f"https://www.adif.es/w/{codigo_estacion}",
                wait_until="domcontentloaded",
            )

            llegadas_locator = page.locator("#horas-trenes-estacion-llegadas")
            llegadas_locator.wait_for(state="attached")
            llegadas_html = llegadas_locator.inner_html()

            return llegadas_html

    @task(task_id="extraer_tabla")
    def extraer_tabla(html: str) -> list[dict]:
        tabla = BeautifulSoup(html, "html.parser")
        filas = tabla.find_all("tr")
        lista = [
            {
                "hora_llegada": fila.find("td", {"class": "col-hora"})
                .text.strip()
                .split(),
                "origen": fila.find("td", {"class": "col-destino"}).text.strip(),
                "via": fila.find("td", {"class": "col-via"}).text.strip(),
                "tren": fila.find("td", {"class": "col-tren"}).text.strip(),
            }
            for fila in filas
            if fila.find("td", {"class": "col-hora"}) is not None
        ]

        return lista

    @task(task_id="guardar_csv")
    def guardar(lista: list[dict], codigo_estacion: str) -> None:
        print(lista)

        with open(
            f"./{codigo_estacion.split('-')[0]}_llegadas.csv", "w", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(f, fieldnames=lista[0].keys())
            writer.writeheader()
            writer.writerows(lista)

            print(f"CSV guardado en: {f.name}")

    codigo_estacion = resolver_codigo_estacion()
    html = llegadas_adif(codigo_estacion)
    tabla = extraer_tabla(html)

    (
        EmptyOperator(task_id="inicio")
        >> codigo_estacion
        >> html
        >> tabla
        >> guardar(tabla, codigo_estacion)
        >> EmptyOperator(task_id="fin")
    )


salidas()
llegadas()
