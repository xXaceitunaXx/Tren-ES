from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import sys
import csv 
from datetime import datetime, timedelta

def buscar_horarios_trenes(entrada, verbose = False):
    with sync_playwright() as p:
        
        # Separamos laa entrada
        origen = entrada[0]
        destino = entrada[1]
        dia = entrada[2]
        mes = entrada[3]
        anio = entrada[4]

        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            locale="es-ES",
        )
        page = context.new_page()
        
        
        
        if(verbose): 
            print("[LOG] Iframe encontrado: Rellenando datos de búsqueda...")

        page.goto(
            f"https://horarios.renfe.com/HIRRenfeWeb/buscar.do?O={origen}&D={destino}&AF={anio}&MF={mes}&DF={dia}",
            wait_until="domcontentloaded",
            timeout=10000
        )
        
        page.wait_for_selector('#ContenidoPrincipal', timeout=10000)

# 3. Extraer el HTML del contenedor en lugar de usar un frame_locator
        contenedor = page.locator('#ContenidoPrincipal')
        html_resultados = contenedor.inner_html()

        # 4. Pasarlo a BeautifulSoup
        soup = BeautifulSoup(html_resultados, "html.parser")
        trenes = soup.find_all("tr", class_="odd irf-travellers-table__tr")
        
        # Escogemos el contenedor dentro del iframe
        html_resultados = page.locator('body').inner_html()
        soup = BeautifulSoup(html_resultados, 'html.parser')
        
        trenes = soup.find_all('tr', class_='odd irf-travellers-table__tr')
        
        # ARCHIVOS CSV
        with open("horarios_renfe_RUTA.csv", mode='a', newline='', encoding='utf-8') as archivo_csv, \
        open("horarios_renfe_HORARIO.csv", mode='a', newline='', encoding='utf-8') as archivo_rutas:

            escritor = csv.writer(archivo_csv)
            escritor_rutas = csv.writer(archivo_rutas)
            
            for tren in trenes:                          
                tds = tren.find_all('td', class_='txt_borde1')
                
                info_tren = tds[0].get_text(strip=True).split()
                enlace_js = tds[0].find('a').get('href', '')
                    
                if "abrirNuevaVentana" in enlace_js:
                    ruta_sucia = enlace_js.split('"')[1]
                    lineas = ruta_sucia.split('\n')
                    ruta_limpia = "".join([linea.strip() for linea in lineas]) # La ruta sale con varios saltos de linea
                    ruta_limpia = ruta_limpia.replace(' ', '%20') # Espacios reemplazados por %20
                    url_completa = f"https://horarios.renfe.com/HIRRenfeWeb/{ruta_limpia}"
                    
                    if verbose:
                        print(f"[LOG] URL busqueda: {url_completa}")
                        
                    # Para cada ruta creamos una "entrada de tabla"
                    pagina_linea = page
                    pagina_linea.goto(url_completa)
                    resultados_linea = pagina_linea.content()
                    
                    soup2 = BeautifulSoup(resultados_linea, 'html.parser')
                    filas_paradas = soup2.find_all('tr', class_='irf-renfe-travel__tr')
                    lista_paradas = []
                    primera_salida = None
                    ultima_llegada = None
                    
                    for fila in filas_paradas:
                        # Iteramos sobre las filas de la tabla
                        celdas = fila.find_all('td', class_='txt_gral')
                        
                        if len(celdas) >= 3:
                            estacion = celdas[0].get_text(strip=True)
                            horaSalida = celdas[1].get_text(strip=True)
                            horaLlegada = celdas[2].get_text(strip=True)
                            
                            if estacion:
                                lista_paradas.append(f"{estacion}")
                                if primera_salida is None and horaSalida: 
                                    primera_salida = horaSalida
                                if horaLlegada:
                                    ultima_llegada = horaLlegada
                    
                    
                    if lista_paradas and len(info_tren) >= 2:
                        paradas_string = " | ".join(lista_paradas)
                        escritor.writerow([paradas_string, info_tren[0], info_tren[1]])
                        
                        # Calculamos duración y escribimos segunda tabla
                        if primera_salida and ultima_llegada:
                            
                            t_salida = datetime.strptime(primera_salida, "%H.%M")
                            t_llegada = datetime.strptime(ultima_llegada, "%H.%M")

                            if t_llegada < t_salida:           # Tren de medianoche
                                t_llegada += timedelta(days=1)

                            duracion = t_llegada - t_salida
                            horas, resto = divmod(duracion.seconds, 3600)
                            minutos = resto // 60
                            duracion_str = f"{horas}h {minutos:02d}min"

                            escritor_rutas.writerow([info_tren[0], primera_salida, ultima_llegada, duracion_str])

                        if verbose:
                            print(f"\n{info_tren} -> Paradas: {lista_paradas}\n")

        browser.close()
if __name__ == "__main__":
    # Ejemplo de entrada: 10600-14100-16-04-2026
    
    verbose = False
    if(len(sys.argv)>1):
        verbose = sys.argv[1] == "--verbose" # Para ver logs
        
    # Leemos la entrada, por guiones
    entrada = sys.stdin.read().strip()
    if entrada:
        try:
            # Dividimos el string usando el guion
            partes = entrada.split('-')
            if len(partes) == 5:
                buscar_horarios_trenes(partes, verbose)
        except Exception as e:
            print(f"[ERROR] Error al procesar la entrada: {e}")
    
    
    