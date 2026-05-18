# WikiData

Los datos de los municipios de España los vamos a obtener de **WikiData**, mediante un script de Python que utiliza el servicio de consultas SPARQL proporcionado por la propia plataforma.

Esta fuente se ha escogido porque WikiData ofrece información estructurada, accesible y fácilmente consultable sobre los municipios de España.

En concreto, necesitamos recuperar el nombre del municipio, su código oficial, la población y sus coordenadas geográficas.

---

## Estructura de los datos obtenidos

La información que queremos obtener desde WikiData tiene la siguiente estructura:

| Columna | Tipo |
|---|---|
| CODIGO | text |
| LABEL | text |
| POBLACION | numeric |
| COORDENADAS | Point |

El campo `CODIGO` representa el código oficial del municipio. El campo `LABEL` contiene el nombre del municipio en español. El campo `POBLACION` almacena el número de habitantes y el campo `COORDENADAS` contiene la localización geográfica del municipio en formato `Point`.

---

## Consulta SPARQL utilizada

Para realizar la extracción de datos se ha utilizado la siguiente consulta SPARQL:

```sparql
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
```

La consulta selecciona aquellas entidades que son municipios de España o pertenecen a alguna subclase relacionada. Para cada municipio se recuperan cuatro atributos principales: el código oficial, el nombre, la población y las coordenadas.

La expresión:

```sparql
?municipio (wdt:P31/(wdt:P279*)) wd:Q2074737;
```

permite seleccionar municipios teniendo en cuenta tanto las instancias directas como aquellas entidades clasificadas mediante subclases. Esto es necesario porque en *WikiData* no están clasificados los municipios de forma uniforme. 

A continuación, se extraen las propiedades necesarias:

```sparql
wdt:P772 ?codigo;
wdt:P1082 ?poblacion;
wdt:P625 ?coordenadas.
```

Estas propiedades corresponden al código oficial del municipio, la población y las coordenadas geográficas.

Además, se utiliza el servicio de etiquetas de WikiData:

```sparql
SERVICE wikibase:label {
  bd:serviceParam wikibase:language "es".
  ?municipio rdfs:label ?label.
}
```

Gracias a esto, se obtiene el nombre del municipio en español, evitando trabajar directamente con identificadores internos de WikiData.

---

## Script de extracción en Python

Para automatizar el proceso se ha desarrollado el siguiente script en Python:

```python
import requests
import csv
import json

WIKIDATA_URL = "https://query.wikidata.org/sparql"

# Consulta para WikiData
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

# Importante: sin el User-Agent, Wikidata puede bloquear la consulta
headers = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "Tren-ES/0.1"
}

# Realiza la consulta
response = requests.get(
    WIKIDATA_URL,
    params={"query": query, "format": "json"},
    headers=headers,
    timeout=60
)

data = response.json()

rows = []

# Procesar los resultados
for item in data["results"]["bindings"]:
    rows.append({
        "codigo": item["codigo"]["value"],
        "label": item["label"]["value"],
        "poblacion": int(float(item["poblacion"]["value"])),
        "coordenadas": item["coordenadas"]["value"],
    })

# Guardar como JSON
with open("municipios_wikidata.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

# Guardar como CSV para SQL
with open("municipios_wikidata.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["codigo", "label", "poblacion", "coordenadas"]
    )
    writer.writeheader()
    writer.writerows(rows)
```

---

## Explicación del script

En primer lugar, se importan las librerías necesarias y se define `WIKIDATA_URL` para poder hacer la conexión.
## Cabeceras de la petición

Una parte importante del script es la definición del `User-Agent`, puesto que, sin ella, *WikiData* bloquea la consulta.
La parte del `Accept` determina el formato que se quiere recibir, en este caso, JSON.


```python
headers = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "Tren-ES/0.1"
}
```

---

## Ejecución de la consulta

La consulta se ejecuta mediante una petición `GET`, con un `timeout` de 60 segundos. 

```python
response = requests.get(
    WIKIDATA_URL,
    params={"query": query, "format": "json"},
    headers=headers,
    timeout=60
)
```

Después, la respuesta se convierte a JSON:

```python
data = response.json()
```

De esta forma, los datos devueltos por *WikiData* pueden procesarse como estructuras propias de Python.

---

## Procesamiento de los resultados

Los resultados de WikiData se encuentran dentro de la estructura `results.bindings`. Cada elemento representa un municipio y contiene los valores solicitados en la consulta.

Para transformar esta estructura en una lista más sencilla, se recorre cada resultado y se crea un diccionario con los campos necesarios:

```python
rows = []

for item in data["results"]["bindings"]:
    rows.append({
        "codigo": item["codigo"]["value"],
        "label": item["label"]["value"],
        "poblacion": int(float(item["poblacion"]["value"])),
        "coordenadas": item["coordenadas"]["value"],
    })
```

En este paso se extraen únicamente los valores reales de cada campo, accediendo a la clave `value`.

La población se convierte a número entero mediante:

```python
int(float(item["poblacion"]["value"]))
```

Es importante transformar los datos a `int` para asegurarse de que son números y no textos.

---

## Exportación a JSON

Una vez procesados los resultados, se guardan en un archivo JSON. Con `ensure_ascii=False` mantenemos las ñ. Con `indent=2` se facilita el debug al meter indentaciones:

```python
with open("municipios_wikidata.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
```

---

## Exportación a CSV

Además del archivo JSON, el script genera un archivo CSV, que es el que se utilizará en una base de datos relacional. Con `fieldnames` se definen los nombres de las columnas, con `writeheader()` se escribe la cabecera y con `writerows(rows)` las filas:

```python
with open("municipios_wikidata.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["codigo", "label", "poblacion", "coordenadas"]
    )
    writer.writeheader()
    writer.writerows(rows)
```

---

## Resultado del proceso

Tras ejecutar el script, se obtienen dos archivos:

```text
municipios_wikidata.json
municipios_wikidata.csv
```

Ambos archivos contienen la misma información, pero están pensados para usos diferentes. El archivo JSON resulta útil para conservar los datos en un formato más legible y se ha utilizado para hacer comprobaciones básicas a mano. El archivo CSV, en cambio, está orientado a la carga de datos en SQL y a su integración con el resto de fuentes del sistema.