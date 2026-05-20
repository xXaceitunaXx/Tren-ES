# Límites y retos del sistema

En esta sección se describen las principales limitaciones y retos encontrados durante el desarrollo del sistema integrador **Tren-ES**.

## Limitaciones del sistema

Aunque el esquema mediador se ha diseñado para representar estaciones, municipios, rutas, paradas, viajes y distancias a nivel nacional, la demo final se ha limitado a un subconjunto de estaciones de Valladolid y Palencia.

Esta decisión se debe a que trabajar con todas las estaciones disponibles en RENFE resultaba inasumible tanto en tiempo como en espacio. El scraping de rutas entre pares de estaciones tardaba demasiado al crecer el número de combinaciones, y los cruces necesarios para generar datos como distancias, rutas y viajes producían un volumen de información demasiado grande para las máquinas virtuales utilizadas.

Por ello, los resultados obtenidos deben interpretarse como una demostración funcional del modelo de integración, no como una explotación completa de toda la red ferroviaria española.

Otra limitación aparece en la tercera consulta. La formulación original buscaba poblaciones con menos de cinco viajes programados, incluyendo aquellas con cero viajes. Para representar estos casos era necesario utilizar operaciones como `LEFT JOIN`, que no se ajustaban bien a la reformulación en forma conjuntiva. Por este motivo, la consulta se reformuló para considerar poblaciones con entre uno y cinco viajes programados.

## Retos temporales

Uno de los principales retos ha sido la gestión del tiempo entre los distintos hitos de la práctica. El proyecto requería definir fuentes, construir el esquema mediador, plantear los mappings GAV y LAV, extraer datos reales, cargarlos y formular consultas sobre ellos.

El scraping aumentó esta dificultad, ya que no bastaba con definir las fuentes de forma teórica: era necesario obtener datos reales y transformarlos a un formato compatible con el sistema. Además, al tener que repetir el scraping para distintos pares de estaciones, el tiempo total de ejecución crecía rápidamente.

## Retos en la extracción de datos

La extracción de datos desde ADIF y RENFE ha sido uno de los puntos más complejos del proyecto.

En ADIF, una petición HTTP básica no era suficiente, ya que la web bloqueaba el acceso automatizado. Fue necesario utilizar `playwright` para simular la navegación de un usuario real y poder acceder a las tablas de salidas y llegadas.

En RENFE, la información de horarios tampoco estaba disponible como una tabla descargable o una API sencilla. Fue necesario interactuar con un formulario, introducir origen, destino y fecha, y acceder después a páginas intermedias para obtener las paradas de cada recorrido.

Este proceso era especialmente costoso porque debía repetirse para cada par origen-destino. Al aumentar el número de estaciones, el número de combinaciones crecía muy rápido, haciendo inviable realizar el scraping completo.

## Retos espaciales y de cruce de datos

Además del tiempo de ejecución, también hubo problemas relacionados con el espacio necesario para almacenar y cruzar los datos.

Relaciones como `Distancia` requieren considerar pares de estaciones. Esto implica que, al aumentar el número de estaciones, el número de tuplas posibles crece de forma muy rápida. Algo similar ocurre al cruzar estaciones, rutas, paradas y viajes procedentes de distintas fuentes.

Este motivo también llevó a la decisión de limitar la instancia de la demo. Así se evita que el tamaño de los datos derivados impida completar la carga y consulta del sistema.

## Retos tecnológicos

Durante el desarrollo se han utilizado tecnologías nuevas para el grupo, como `playwright`, Airflow y GraphQL. Estas herramientas han requerido un proceso previo de aprendizaje para entender cómo aplicarlas dentro de un sistema integrador con fuentes heterogéneas.

También se han usado consultas SPARQL sobre WikiData para obtener información de municipios. Aunque esta fuente ofrece datos estructurados, fue necesario tener en cuenta detalles técnicos como el uso de cabeceras para evitar bloqueos.

## Retos de integración

Las fuentes utilizadas no compartían el mismo modelo de datos ni los mismos identificadores. Por ello, fue necesario definir correspondencias entre los esquemas origen y el esquema mediador.

Por ejemplo, la tabla `Municipio` requiere combinar datos de WikiData y del INE. WikiData aporta población y coordenadas, mientras que el INE permite relacionar municipios con provincias y comunidades autónomas.

En el caso de RENFE, las paradas de una ruta aparecían como una lista no normalizada. Para adaptarlas al esquema mediador fue necesario introducir una vista auxiliar que permitiera descomponer esa lista y construir la relación `Parada`.

## Otras limitaciones

Inicialmente se planteó añadir una interfaz gráfica para facilitar la consulta del integrador. Sin embargo, por falta de tiempo, la demo final no incluye una interfaz de usuario y se centra en mostrar el funcionamiento del sistema mediante los datos cargados y las consultas definidas.