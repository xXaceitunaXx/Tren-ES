# API

## RENFE

Para obtener la información de las estaciones necesitamos hacer uso de la API oficial de [data RENFE](https://data.renfe.com/), más concretamente la asociada al dataset con el [listado completo de estaciones](https://data.renfe.com/dataset/estaciones-listado-completo). Para hacer esta búsqueda en primer lugar decidimos no incluir todas aquellas estaciones que fuesen de cercanías o feve, pero nos encontramos con un problema: al no incluir estaciones de cercanías estábamos excluyendo todas aquellas estaciones que tuvieran el servicio, incluyendo las dos grandes estaciones de Madrid: Chamartín y Puerta de Atocha, por lo que finalmente decidimos excluir únicamente aquellas estaciones que tuvieran servicio feve. 

El archivo en su origen tenía los siguientes campos:

| Columna | Tipo |
| --- | --- |
| CODIGO | numeric |
| DESCRIPCION | text |
| LATITUD | numeric |
| LONGITUD | numeric |
| DIRECION | text |
| CP | numeric |
| POBLACION | text |
| PROVINCIA | text |
| PAIS | text |
| CERCANIAS | text |
| FEVE | text |
| COMUN | text |

Para hacer la consulta a la api decidimos utilizar la consulta via sentencia sql para mayor control, ya que la documentación de la api era bastante poco clara (los ejemplos estaban hechos en Python2). La consulta que acabamos realizando es la siguiente:

```sql
SELECT "_id" as "ID", "CODIGO", "DESCRIPCION", "LATITUD", "LONGITUD", "DIRECION" as "DIRECCION", "CP", "POBLACION", "PROVINCIA", "PAIS"
    FROM "783e0626-6fa8-4ac7-a880-fa53144654ff" 
    WHERE "FEVE" = 'NO'
```

Con lo que acabamos con los campos vistos en los esquemas de origen, listo para su utilización por el esquema mediador. Los campos que no hemos escogido no los hemos visto necesarios para el desarrollo de la práctica.

Hay que tener en cuenta que ciertas estaciones por algún motivo carecen de algunos campos como el código postal o la dirección. Tendremos que realizar una limpieza de estas estaciones al realizar la integración. Al final, obtenemos un listado con 870 estaciones.

### La problemática: muchas estaciones

Tras cargar el listado de estaciones nos encontramos con un problema: encontrar las rutas necesarias entre dos estaciones via scraping. El acto de realizar este scraping entre dos estaciones tarda entre 3 y 20 segundos dependiendo del número de rutas. Puede parecer poco tiempo pero haciendo cálculos, necesitamos combinar las 870 estaciones de dos en dos:

$$
\binom{870}{2}=\frac{870!}{2!868!}=\frac{870*869}{2}=378015\ combinaciones
$$

Con lo que obtenemos un rango de entre 13 y 85 días aproximadamente solo obteniendo los datos de las rutas para un día concreto. Esto es inviable, y es un problema que deberemos solucionar a la hora de integrar la información y realizar las consultas propuestas.


