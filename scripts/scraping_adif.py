from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

import csv


BASE_URL_ADIF = "https://www.adif.es/"

def salidas_adif(codigo_estacion: str) -> str:
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


def llegadas_adif(codigo_estacion: str) -> str:
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


def extraer_tabla(html: str, salida: bool) -> list[dict]:
    tabla = BeautifulSoup(html, "html.parser")
    filas = tabla.find_all("tr")

    lista = [
        {
            f"hora_{"salida" if salida else "llegada"}": fila.find("td", {"class": "col-hora"})
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


def guardar(lista: list[dict], codigo_estacion: str, salidas: bool) -> None:

    with open(
        f"./{codigo_estacion.split('-')[0]}_{"salidas" if salidas else "llegadas"}.csv", "w", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=lista[0].keys())
        writer.writeheader()
        writer.writerows(lista)

        print(f"CSV guardado en: {f.name}")


valladolid = "10600-valladolid-c.-g."

html_salidas = salidas_adif(valladolid)
html_llegadas = llegadas_adif(valladolid)

guardar(extraer_tabla(html_salidas, salida=True), valladolid, salidas=True)
guardar(extraer_tabla(html_llegadas, salida=False), valladolid, salidas=False)
