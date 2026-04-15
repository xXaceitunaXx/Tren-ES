from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import sys

def buscar_horarios_trenes(entrada, verbose = False):
    with sync_playwright() as p:
        
        # Separamos laa entrada
        origen = entrada[0]
        destino = entrada[1]
        dia = entrada[2]
        mes = entrada[3]
        anio = entrada[4]

        browser = p.chromium.launch(headless=True) 
        page = browser.new_page()
        page.goto("https://www.renfe.com/es/es/viajar/informacion-util/horarios")
        
        try: # Botón de cookies, en renfe no parece obligatorio, pero por si acaso
            page.wait_for_selector('#onetrust-accept-btn-handler', timeout=5000)
            page.click('#onetrust-accept-btn-handler')
            if(verbose):   
                print("[LOG] Cookies aceptadas.")
        except:
            if(verbose): 
                print("[LOG] No apareció el banner de cookies.")

        #  FORMULARIO
        
        # Los contenidos están en un iframe
        # Debemos acceder al iframe para poder ver los selectores del formulario
        buscador_frame = page.frame_locator('#ContenidoPrincipal')
        
        
        if(verbose): 
            print("[LOG] Iframe encontrado: Rellenando datos de búsqueda...")

        buscador_frame.locator('select#O').select_option(value=origen) # Codigo de estacion
        buscador_frame.locator('select#D').select_option(value=destino) # Codigo de estacion
        buscador_frame.locator('select#DF').select_option(value=dia)
        buscador_frame.locator('select#MF').select_option(value=mes)
        buscador_frame.locator('select#AF').select_option(value=anio)
        # Palencia: 14100
        # Valladolid: 10600 
        
        
        # BUSCAR
        buscador_frame.locator('button[title="BUSCAR"]').click()
        
        # Esperamos a que cargue la página web para poder acceder
        if(verbose): 
            print("[LOG] Buscando trenes...")
        buscador_frame.locator('tr.odd.irf-travellers-table__tr').first.wait_for(timeout=10000)
        
        # Escogemos el contenedor dentro del iframe
        html_resultados = buscador_frame.locator('body').inner_html()
        soup = BeautifulSoup(html_resultados, 'html.parser')
        
        trenes = soup.find_all('tr', class_='odd irf-travellers-table__tr')
        
        for tren in trenes:
            tds = tren.find_all('td', class_='txt_borde1')
            
            info_tren = tds[0].get_text(strip = True).split()
            enlace_js = tds[0].find('a').get('href', '')
                
            if "abrirNuevaVentana" in enlace_js: # Abrimos el enlace (funcion javaScript)
                ruta_sucia = enlace_js.split('"')[1]
                
                lineas = ruta_sucia.split('\n')
                ruta_limpia = "".join([linea.strip() for linea in lineas]) # La ruta sale con varios saltos de linea
                
                ruta_limpia = ruta_limpia.replace(' ', '%20') # Espacios reemplazados por %20
                
                url_completa = f"https://horarios.renfe.com/HIRRenfeWeb/{ruta_limpia}"
                
                if(verbose): 
                    print(f"[LOG] URL busqueda: {url_completa}")
                    
                # Para cada ruta creamos una "entrada de tabla"
                pagina_linea = browser.new_page()
                pagina_linea.goto(url_completa)
                resultados_linea = pagina_linea.content()
                
                soup2 = BeautifulSoup(resultados_linea, 'html.parser')
                filas_paradas = soup2.find_all('tr', class_='irf-renfe-travel__tr')
                lista_paradas = []
                
                for fila in filas_paradas:
                    # Iteramos sobre las filas de la tabla
                    celdas = fila.find_all('td', class_='txt_gral')
                    
                    if len(celdas) >= 3:
                        estacion = celdas[0].get_text(strip=True)
                        horaSalida = celdas[1].get_text(strip=True)
                        horaLlegada = celdas[2].get_text(strip=True)
                        
                        # Guardamos si la estación está vacía (puede pasar)
                        if estacion:
                            lista_paradas.append(f"{estacion} [{horaSalida}//{horaLlegada}]")
                
                print(f"\n {info_tren} -> Paradas: {lista_paradas}\n")
                
                pagina_linea.close()

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
    
    
    