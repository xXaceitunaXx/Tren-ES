import requests
import sys
import csv

url_sql = 'https://data.renfe.com/api/3/action/datastore_search_sql'

# Se puede hacer una consulta SQL directamente sobre la api para obtener la tabla
mi_sql = """
    SELECT "_id" as "ID", "CODIGO", "DESCRIPCION", "LATITUD", "LONGITUD", "DIRECION" as "DIRECCION", "CP", "POBLACION", "PROVINCIA", "PAIS"
    FROM "783e0626-6fa8-4ac7-a880-fa53144654ff" 
    WHERE "FEVE" = 'NO'
"""

# Es necesario que esté en un diccionario o salta error
parametros = {
    'sql': mi_sql
}

respuesta = requests.get(url_sql, params=parametros)

if respuesta.status_code == 200:
    datos = respuesta.json()
    registros = datos.get('result', {}).get('records', [])

    if registros:
        nombre_archivo = "data_renfe_ESTACION.csv"

        with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo:
            # Nombres de columna
            orden_columnas = [
            "ID", "CODIGO", "DESCRIPCION", "LATITUD", "LONGITUD", 
            "DIRECCION", "CP", "POBLACION", "PROVINCIA", "PAIS"
        ]
            
            escritor = csv.DictWriter(archivo, fieldnames=orden_columnas)

            # Escribimos la cabecera 
            escritor.writeheader()
            
            # Escribimos el resto de datos
            escritor.writerows(registros)
            
        print(f"Se han guardado {len(registros)} registros en {nombre_archivo}.")
    else:
        print("Ha habido un fallo al cargar los datos", file=sys.stderr)
else:
    print(f"Error en la API: {respuesta.status_code}", file=sys.stderr)
    print(respuesta.text, file=sys.stderr)