from typing import Any

from airflow.sdk import dag, task
from pendulum import datetime

from requests import get
# from bs4 import BeautifulSoup

BASE_URL_ADIF = "https://www.adif.es/"

@dag(
	dag_id="tren_es",
	description="DAG base para el flujo de trenes ES.",
	start_date=datetime(2026, 4, 14),
	schedule=None,
	params={"codigo_estacion": "MAD"},
	tags=["tren", "es"],
)
def tren_es() -> None:
	@task(task_id="resolver_codigo_estacion")
	def resolver_codigo_estacion(**context) -> str:
		dag_run = context.get("dag_run")
		dag_run_conf = getattr(dag_run, "conf", {}) or {}
		codigo = dag_run_conf.get("codigo_estacion") or context["params"]["codigo_estacion"]
		return str(codigo)


	# Tiene toda la pinta que esta web no se puede scrappear :(
	@task(task_id="salidas")
	def salidas_adif(codigo_estacion: Any) -> str:
		headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "es-ES,es;q=0.9",
		"Referer": BASE_URL_ADIF,
		} # Todas estas cosas me las ha generado Copilot, que como no soy ningún super experto en protoco http, mejor se lo dejo a él
		try:
			response = get(f"{BASE_URL_ADIF}w/{codigo_estacion}", headers=headers, timeout=10)
			response.raise_for_status()
			return response.text
		except Exception as e:
			print(f"Error al obtener datos de ADIF: {e}")
			return f"Error: {str(e)}"

	salidas_adif(resolver_codigo_estacion())


tren_es()
