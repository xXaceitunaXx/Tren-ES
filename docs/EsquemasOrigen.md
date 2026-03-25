# Esquemas Origen

En este documento se muestran los esquemas de las fuentes de datos origen de nuestro sistema integrador Tren-ES. Las fuentes de datos son las siguientes:

- Wikidata. Para obtener información de los municipios, como su nombre, código del INE, coordenadas geográficas o la población)
- INE. Para conectar los códigos de los municipios con las provincias y comunidades autónomas.
- Renfe. Dos distintas:
    - Renfe Data. Obtenemos información a partir de la API de Renfe de todas las estaciones que existen en España.
    - Renfe horarios. Un pequeño formulario desde el que se puede obtener la información de todos los horarios de tramos (Estación Origen, Estación Destino) disponibles en la web de renfe y las rutas correspondientes.
- ADIF. Información en tiempo real de las salidas y llegadas en cada estación. Nos permite contrastar los horarios planificados con los reales.

## Forma conjuntiva de las tablas origen

* wikidata_MUNICIPIO(codigo, label, poblacion, coordenadas)
Tabla de datos extraidos de Wikidata. La tabla está formada por un campo `codigo` que contiene el identificador INE del municipio, un campo `label` con el nombre del municipio en texto legible, la columna `poblacion` que almacena el número de habitantes de ese municipio y las `coordenadas`, una tupla de tipo Point que almacena las coordenadas geográficas de dicho municipio.
* INE_MUNICIPIO(cmun, cpro, dc, nombre)
Datos oficiales sobre municipios ofrecidos por el INE. Formados por un código de municipio `cmun`, que identifica a un municipio *dentro* de una provincia, el código de la provincia a la que pertenece, `cpro`, un dígito de control (que no nos genera interés) `dc` y el nombre en texto legible, `nombre`.
* INE_PROVINCIA(cpro, nombre, codauto, ccaa)
Datos oficiales sobre provincias ofrecidos por el INE. Es una tabla que cruza provincias con su respectiva comunidad autónoma. Formada por la información de provincia, `cpro` y `nombre`, código de la provincia y nombre en texto legible respectivamente, e información sobre la Comunidad Autónoma a la que pertenece, `codauto` y `ccaa`, código de la Comunidad Autónoma y nombre en texto legible respectivamente.
* data_renfe_ESTACION(id, codigo, descripcion, latitud, longitud, direccion, c_p, poblacion, provincia, pais)
Este esquema, se ofrece en la sección de datos abiertos de Renfe. Contiene información sobre todas las estaciones de trenes que hay en España. Se compone por, un `id` de asignación secuencial, un código de estación `codigo`, el nombre en texto legible guardado en `descripción`, las coordenadas geográficas por separado en `latitud` y `longitud`, una dirección guardada en la columna `direccion` y el código postal asociado `c_p` y finalmente datos territoriales de la ubicación, `población`, `provincia` y `pais`.
* horarios_renfe_HORARIO(recorrido, salida, llegada, duracion)
Datos extraídos de un formulario de la página de Renfe. El horario son viajes que van desde una estación de origen hasta una de destino. `recorrido` es la ruta que realiza ese viaje, `salida` y `llegada` son las estaciones que une dicho viaje (y que son paradas de la ruta). Duración es el tiempo en horas y minutos que tarda en completarse el viaje.
* horarios_renfe_RUTA(codigo, tipo, paradas)
Se extraen del mismo formulario, contiene información sobre una ruta en específico. Las rutas son conjuntos de estaciones que se recorren en un orden específico. Una ruta tiene un `codigo` que la identifica frente al resto, y un `tipo` de tren que la recorre (MD, AV, AVLO, ...) y `paradas` representa la lista de paradas. Sabemos que no es una representación normalizada, pero nos parecía que añadía mucha complejidad a representar los orígenes, y por motivos de simpleza lo hemos hecho así. En el esquema mediador se trata y soluciona este problema.
* adif_SALIDAS(hora, destino, tren, via, estacion)
Información accesible desde las páginas de datos en tiempo real sobre las estaciones españolas. Contiene información sobre las salidas en tiempo real. `hora` es el cuándo sale el tren de la estación, el campo `destino` contiene la estación destino de dicha salida, `tren` almacena tanto la ruta de dicho viaje que sale como el tipo de tren que la atiende, una columna `via` desde dónde es dicha salida y `estacion` la estación de la que provienen los datos.  
* adif_LLEGADAS(hora, origen, tren, via, estacion)
La entidad de llegadas contiene la misma información que salidas, pero intercambiando cualquier dato por los correspondientes a las llegadas.

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
```
```mermaid
erDiagram
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
```
```mermaid
erDiagram

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
