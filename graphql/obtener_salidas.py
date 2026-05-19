import urllib.parse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def obtener_salidas_adif(codigo_estacion: str, nombre_municipio: str) -> list[dict]:
    async with async_playwright() as p:
        
        browser = await p.chromium.launch(headless=True, channel="chromium")
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="es-ES",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        termino_busqueda = f"{codigo_estacion} {nombre_municipio}" # urllib.parse.quote convierte los espacios en %20 (ej: "17000%20MADRID")
        query_codificada = urllib.parse.quote(termino_busqueda)
        url_busqueda = f"https://www.adif.es/search?q={query_codificada}"
        
        await page.goto(url_busqueda, wait_until="domcontentloaded", timeout=60000)
        print(url_busqueda, flush=True)
        
        # ------ Página de resultados (ADIF tiene antibot) ------
        
        primer_resultado = page.locator('ul#search-results-display-list li.list-group-item a').first
        await primer_resultado.wait_for(state="visible", timeout=15000)
        
        url_estacion = await primer_resultado.get_attribute("href")
        # if url_estacion.startswith("/"):
        #     url_estacion = "https://www.adif.es" + url_estacion
            
        await page.goto(url_estacion, wait_until="domcontentloaded")
        
        # ------ Cambiamos de pagina ------
        
        await page.locator('a[href="#tab-salidas"]').click()
        filas_salidas = page.locator("#tab-salidas tbody tr")
        await filas_salidas.first.wait_for(state="attached", timeout=20000)
        html = await page.locator("#horas-trenes-estacion-salidas").inner_html()
        
        tabla = BeautifulSoup(html, "html.parser")
        filas = tabla.find_all("tr")
        
        lista = []
        for fila in filas:
            if fila.find("td", {"class": "col-hora"}):
                # Unimos la hora en un string para que sea más fácil en GraphQL
                hora_texto = " ".join(fila.find("td", {"class": "col-hora"}).text.strip().split())
                lista.append({
                    "hora": hora_texto,
                    "destino": fila.find("td", {"class": "col-destino"}).text.strip(),
                    "via": fila.find("td", {"class": "col-via"}).text.strip(),
                    "tren": fila.find("td", {"class": "col-tren"}).text.strip(),
                })
                
        await browser.close()
        return lista