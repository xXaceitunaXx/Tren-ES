import requests
import json
import csv

INE_REQUEST_URL = r"https://servicios.ine.es/wstempus/js/ES/VALORES_VARIABLE"
INE_PROVINCIAS = "115"
INE_MUNICIPIOS = "19"


def to_csv(nombre, contenido):
    keys = contenido[0].keys()
    with open(nombre, "w") as fichero:
        dict_writer = csv.DictWriter(fichero, keys)
        dict_writer.writeheader()
        dict_writer.writerows(contenido)


def extraer_provincias():
    provincias_response = requests.get(f"{INE_REQUEST_URL}/{INE_PROVINCIAS}?det=2")
    provincias_json = provincias_response.json()
    provincias = [
            {
                "CPRO": p["Codigo"], 
                "NOMBRE": p["Nombre"], 
                "CODAUTO": p["JerarquiaPadres"][0]["Codigo"],
                "CCAA": p["JerarquiaPadres"][0]["Nombre"].split(",")[0]
            }
            for p in provincias_json
            if p["Codigo"] and int(p["Codigo"]) in range(1, 50)
        ]

    to_csv("provincias.csv", provincias) 

def extraer_municipios():
    municipios_response = requests.get(f"{INE_REQUEST_URL}/{INE_MUNICIPIOS}")
    municipios_json = municipios_response.json()
#    with open("./municipios.json") as m_file:
#    municipios_json = json.load(m_file)

    municipios = [
            {
                "CMUN": m["Codigo"][2:5],
                "CPRO": m["Codigo"][0:2],
                "NOMBRE": m["Nombre"]
            }
            for m in municipios_json
        ]

    to_csv("municipios.csv", municipios)
     

def main():
   # extraer_provincias() 
   extraer_municipios()

if __name__ == "__main__":
    main()
