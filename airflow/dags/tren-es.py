from typing import Any

from airflow.sdk import dag, task
from pendulum import datetime

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL_ADIF = "https://www.adif.es/"

@dag(
	dag_id="tren_es",
	description="DAG base para el flujo de trenes ES.",
	start_date=datetime(2026, 4, 14),
	schedule=None,
	params={"codigo_estacion": "10600-valladolid-c.-g."},
	tags=["tren", "es"],
)
def tren_es() -> None:
	@task(task_id="resolver_codigo_estacion")
	def resolver_codigo_estacion(**context) -> str:
		dag_run = context.get("dag_run")
		dag_run_conf = getattr(dag_run, "conf", {}) or {}
		codigo = dag_run_conf.get("codigo_estacion") or context["params"]["codigo_estacion"]
		print(codigo)
		return str(codigo)


	@task(task_id="adif_salidas")
	def salidas_adif(codigo_estacion: Any) -> str:
		with sync_playwright() as p:
			browser = p.chromium.launch(headless=False)
			page = browser.new_page()
			page.goto(f"https://www.adif.es/w/10600-valladolid-c.-g.")
			llegadas = BeautifulSoup(page.locator("#tab-llegadas").inner_html())
			page.locator('a[href="#tab-salidas"]').click()
			salidas = BeautifulSoup(page.locator("#tab-salidas").inner_html())
			return llegadas.find("table").find_all("tr")
			
		
	salidas_adif(resolver_codigo_estacion())


tren_es()
