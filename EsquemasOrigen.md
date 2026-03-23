---
title: Esquemas Origen
author: Víctor Elvira Fernández, Juan Horrillo Crespo, Sergio Velasco de Pedro
---

# Esquemas Origen

En este documento se muestran los esquemas de las fuentes de datos origen de nuestro sistema integrador Tren-ES. Las fuentes de datos son las siguientes

- WikiData. Para obtener información de los municipios, como su nombre, código del INE, coordenadas geográficas o la población)
- INE. Para conectar los códigos de los municipios con las provincias y comunidades autónomas.
- Renfe. Dos distintas:
    - Renfe Data. Obtenemos información a partir de la api de renfe de todas las estaciones que existen en españa.
    - Renfe horarios. Un pequeño formulario desde el que se puede obtener la información de todos los horarios de tramos (Estación Origen, Estación Destino) disponibles en la web de renfe y las rutas correspondientes.
- ADIF. Información en tiempo real de las salidas y llegadas en cada estación. Nos permite contrastar los horarios planificados con los reales.

```mermaid
erDiagram
    wikidata_MUNICIPIO {
        int CODIGO "CÓDIGO"
        text LABEL
        int POBLACION "POBLACIÓN"
        point COORDENADAS
    }

    INE_MUNICIPIO {
        int CMUN "CÓDIGO DE MUNICIPIO"
        int CPRO "CÓDIGO DE PROVINCIA"
        int DC "DÍGITO DE CONTROL"
        text NOMBRE
    }

    INE_PROVINCIA {
        int CPRO "CÓDIGO DE PROVINCIA"
        text NOMBRE "NOMBRE DE PROVINCIA"
        int CODAUTO "CÓDIGO DE CCAA"
        text CCAA "NOMBRE COMUNIDAD AUTÓNOMA"
    }

    data_renfe_ESTACION {
        int ID
        numeric CODIGO "CÓDIGO"
        text DESCRIPCION "NOMBRE ESTACIÓN"
        text LATITUD
        text LONGITUD
        text DIRECCION "DIRECCIÓN"
        numeric C_P "C.P."
        text POBLACION
        text PROVINCIA
        text PAIS
    }
```
```mermaid
erDiagram
    horarios_renfe_HORARIO {
        text RECORRIDO "TREN/RECORRIDO"
        time SALIDA
        time LLEGADA
        text DURACION "HORAS/MINUTOS"
    }

    horarios_renfe_RUTA {
        list PARADAS "NOMBRE ESTACIONES"
        int CODIGO "CÓDIGO DE RUTA"
    }

    adif_SALIDAS {
        time HORA
        text DESTINO
        text TREN
        int VIA
    }

    adif_LLEGADAS {
        time HORA
        text ORIGEN
        text TREN
        int VIA
    }
```
