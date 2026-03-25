A partir del mediador y los esquemas de las fuentes de datos podemos acabar con los siguientes esquemas GAV:

### Municipio

Es necesario cruzar los datos de los datos de *wikidata* y los del *INE* para poder obtener de forma correcta los códigos de provincia y comunidad autónoma.

`Municipio(id, nombre, n_habitantes, latitud_m, longitud_m, provincia, CCAA)` $\subseteq$

```
wikidata_MUNICIPIO(id, nombre ,n_habitantes, coordenadas), latitud_m=latitud(coordenadas), longitud_m=longitud(coordenadas), INE_MUNICIPIO(cmun, cpro, v1, v2), id==cmun+cpro, INE_PROVINCIA(cpro, provincia, v3, CCAA)
```

### Estacion

Hay que tener en cuenta que solo debemos obtener estaciones de España.

`Estacion(id, municipio, nombre, latitud_e, longitud_e)` $\subseteq$

```
data_renfe_ESTACION(v1, id, nombre, latitud_e, longitud_e, v2, v3, nombre_mun, v4, v5), wikidata_MUNICIPIO(municipio, nombre_mun ,v6, pais), pais==España
```

### Distancia

En este caso solo guardamos las distancias entre las estaciones de forma unidireccional, ya que la distancia entre una estación y otra es la misma que entre la segunda y la primera, y así evitamos información repetida.

`Distancia(estacion1, estacion2, distancia)` $\subseteq$

```
data_renfe_ESTACION(v1, estacion1, v2, latitud_1, longitud_1, v3, v4, v5, v6, pais), data_renfe_ESTACION(v8, estacion2, v9, latitud_2, longitud_2, v10, v11, v12, v13, pais), distancia=dist(latitud_1, latitud_2, longitud_1, longitud_2), estacion1 < estacion2, pais==España
```

### Ruta y Parada

En las fuentes de datos obtenemos desde *horarios_renfe_RUTA* una lista de paradas. Para poder extraer cada parada por separado debemos normalizar esta lista, por lo que nos ayudamos de una vista auxiliar. Esta vista no se encuentra en los archivos SQL en este hito.

#### Vista auxiliar: Parada_aux

Esta vista auxiliar no se encuentra en el esquema mediador, utilizaremos una función para normalizar la lista y poder extraer las paradas:

`Parada_aux(codigo_ruta, num_secuencia, nombre_parada)`$\subseteq$

```
horarios_renfe_RUTA(lista_paradas, codigo_ruta), (num_secuencia, nombre_parada) =unlist(lista_paradas)
```

A partir de esta vista auxiliar podemos definir correctamente parada:

`Parada(ruta, estacion, num_secuencia, km_origen)` $\subseteq$

```
Parada_aux(ruta, num_secuencia, nombre_parada), data_renfe_ESTACION(v1, estacion, nombre_parada, v3, v4, v5, v6, v7, v8, pais), pais==España
```

Para definir la ruta volvemos a necesitar funciones externas. Una ruta se define por un identificador propio y una tupla origen y destino de estaciones de la ruta. Para esto debemos obtener los números de secuencia mínimo y máximo de cada entrada de *Parada_aux*.

`Ruta(id, origen, destino, tipo)` $\subseteq$

```
Parada_aux(id, num_secuencia, nombre_parada), nombre_origen=getMinSecuencia(num_secuencia), nombre_destino=getMaxSecuencia(num_secuencia), data_renfe_ESTACION(v1, origen, nombre_origen, v3, v4, v5, v6, v7, v8, pais), data_renfe_ESTACION(v10, destino, nombre_destino, v11, v12, v13, v14, v15, v16, pais), pais==España
```

### Viaje

El horario se refiere a la hora de llegada en la estación destino del viaje específico, recogido de la web de *ADIF*.

`Viaje(id, ruta, fecha, horario)` $\subseteq$

```
Parada_aux(ruta, num_secuencia, nombre_parada), nombre_origen=getMinSecuencia(num_secuencia), data_renfe_ESTACION(v1, estacion, nombre_origen, v3, v4, v5, v6, v7, v8, pais), adif_SALIDAS(fecha, horario, v10, v11, estacion), id=secuencia(), pais==España
```

No se han considerado simplificaciones para ninguna tabla. Para la tabla Municipio no se puede simplificar ya que es necesario hacer el cruce de tablas con el INE para obtener correctamente el código de provincia y Comunidad Autónoma. Para el resto de tablas no vemos simplificación posible.
