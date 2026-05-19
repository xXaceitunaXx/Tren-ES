import uuid
import os
import pandas as pd
import strawberry
from dotenv import load_dotenv
from sqlalchemy import create_engine
from typing import List

def conectar_bd():
    load_dotenv()
    user = os.getenv("DB_USER", "test")
    password = os.getenv("DB_PASSWD", "test")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB", "testdb")
    
    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(url)

@strawberry.type
class DatosConsulta1:
    id: int
    nombre_estacion: str
    nombre_municipio: str
    
@strawberry.type
class DatosConsulta2:
    id: str
    ruta_id: str
    tren: str
    destino: str

@strawberry.type
class Query:
    @strawberry.field
    def consulta1(self, n_habit: int = 10000, limite: int = 20) -> List[DatosConsulta1]:
        motor = conectar_bd()
        consulta1 = f"""
        SELECT E.id, E.nombre AS estacion, M.nombre AS municipio
        FROM Estacion AS E
        INNER JOIN Municipio AS M
            ON E.municipio = M.id
        WHERE M.n_habitantes < {n_habit}
        LIMIT {limite};"""
        
        df = pd.read_sql(consulta1, motor)
        
        lista_estaciones = []
        for _, fila in df.iterrows():
            lista_estaciones.append(DatosConsulta1(
                id=str(fila["id"]),
                nombre_estacion=str(fila["estacion"]),
                nombre_municipio=str(fila["municipio"]) 
            ))
            
        return lista_estaciones

    @strawberry.field
    async def consulta2(self, max_distancia: float = 30, limite: int = 20) -> List[DatosConsulta2]:
        motor = conectar_bd()
        consulta2 = f"""
        SELECT R.id AS ruta_id, R.origen AS estacion_origen, M.nombre AS municipio
        FROM Ruta AS R
        INNER JOIN Distancia AS D
            ON (R.origen = D.estacion1 AND R.destino = D.estacion2) OR
               (R.origen = D.estacion2 AND R.destino = D.estacion1)
        INNER JOIN Estacion AS E
            ON R.origen = E.id
        INNER JOIN Municipio AS M
            ON E.municipio = M.id
        WHERE D.distancia < {max_distancia}
        LIMIT {limite};"""
        
        df = pd.read_sql(consulta2, motor)
        lista_viajes = []
        
        for _, fila in df.iterrows():
            estacion_origen = str(fila["estacion_origen"])
            nombre_municipio = str(fila["municipio"])
            ruta_id = str(fila["ruta_id"])
            
            # Llamamos a Adif usando el origen de esa ruta
            #viajes_adif = obtener_salidas_adif(estacion_origen, nombre_municipio)
            viajes_adif = await obtener_salidas_adif(17000, "MADRID")
            print("scraper ha finalizado")
            
            # Por cada tren que encontremos en la web, "creamos" una entidad Viaje
            for tren in viajes_adif:
                lista_viajes.append(DatosConsulta2(
                    id=str(uuid.uuid4()), # Generamos un ID virtual único
                    ruta_id=ruta_id,
                    tren=tren.get("tren", "Desconocido"),
                    destino=tren.get("destino", "Desconocido")
                ))
                
        return lista_viajes

# Función integración virtual (tabla viaje)

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

schema = strawberry.Schema(query=Query)