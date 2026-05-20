# Integración final

Hemos optado por un sistema integrador híbrido, combinando el Warhousing con técnicas de Integración Virtual. La motivación principal de esta hibridación es principalmente la diferencia entre las frecuencias de actualización de los datos. Por un lado tenemos fuentes como los datos de municipios y provincias proporcionados por el INE, que se actualizan cada mucho tiempo, frente a otras como las tablas de salidas de trenes en tiempo real en la página web de Adif, que se actualizan en periodos de segundos.

El _tech stack_ está formado por:
- Apache Airflow. Para extractores y pipelines.
- MariaDB. Base de datos relacional que almacena el Warehouse.
- GraphQL. Resolución de consultas sobre el esquema mediador.

A continuación se muestra una representación gráfica del sistema

![Diagrama sistema integrador](img/DiagramaTren-ES.png)

## Pipelines ETL

Los pipelines de extracción, transformación y carga de los datos se han implementado como DAGs de Airflow. El flujo es el siguiente:

```
EXTRACTOR S1 ----> TABLA STAGE (csv) -----+
                                          |
                                          |
                                          |
                                          |
EXTRACTOR S2 ----> TABLA STAGE (csv) ---- + ----> TRANSFORM ----> ESQUEMA WAREHOUSE
                                          |
                                          |
                                         ···
                                          |
                                          |
EXTRACTOR Sk ----> TABLA STAGE (csv) -----+

```
