## Reformulación GAV y LAV de las Consultas

En esta sección vamos a hacer la reformulación GAV y LAV de las consultas. Para la reformulación GAV emplearemos la descomposición de consultas y para la reformulación LAV utilizaremos el algoritmo de los *Buckets*.

### Consulta 1

* Estaciones de tren en poblaciones de menos de 10000 habitantes.

La consulta se puede escribir sobre el esquema mediador como:

```
Q1(id, nombre_estacion, nombre_municipio):- Estacion(id, id_mun, nombre_estacion, lat_e, lon_e), Municipio(nombre_municipio, habitantes, id_mun, lat_m, lon_m, prov, ccaa), hab<10000
```

#### Reformulación GAV

Para hacer la reformulación GAV basta con sustituir los átomos en la consulta global por sus respectivas definiciones en función de las fuentes, a partir de la formulación GAV de las fuentes vistas en apartados anteriores.

Para el átomo *Estacion*, sustituimos por su correspondiente formulación GAV:
`Estacion(id, municipio, nombre, latitud_e, longitud_e)` $\subseteq$

```
data_renfe_ESTACION(v1, id, nombre, latitud_e, longitud_e, v2, v3, nombre_mun, v4, v5), wikidata_MUNICIPIO(municipio, nombre_mun ,v6, pais), pais==España
```

E igualmente con *Municipio*, que queda:
`Municipio(id, nombre, n_habitantes, latitud_m, longitud_m, provincia, CCAA)` $\subseteq$

```
wikidata_MUNICIPIO(id, nombre ,n_habitantes, coordenadas), latitud_m=latitud(coordenadas), longitud_m=longitud(coordenadas), INE_MUNICIPIO(cmun, cpro, v1, v2), id==cmun+cpro, INE_PROVINCIA(cpro, provincia, v3, CCAA)
```

Incluimos dichas formulaciones en la consulta global, añadiendo la restriccion de habitantes, que da como resultado:

```
Q1'(id, nombre_estacion, nombre_municipio):- data_renfe_ESTACION(v1​, id, nombre_estacion, lat_e, lon_e, v2​, v3​, nom_mun, v4​, v5​), wikidata_MUNICIPIO(id_mun, nombre_municipio, v6​, v7​), wikidata_MUNICIPIO(id_mun, nombre_municipio, hab, coord), lat_m=latitud(coord), lon_m=longitud(coord), INE_MUNICIPIO(cmun, cpro, v8​, v9​), INE_PROVINCIA(cpro, prov, v10​, ccaa), id_mun=cmun+cpro, hab<10000
```

Por último, podemos ver que el átomo *wikidata_MUNICIPIO* se encuentra repetido, por lo que podríamos pensar en simplificar para eliminar redundancias. Podríamos hacer mappings de contención para ver equivalencias, pero es evidente que, dado que v6 y v7 no se utilizan, podemos eliminar el primer átomo, quedando la consulta final como:

```
Q1'(id, nombre_estacion, nombre_municipio):- data_renfe_ESTACION(v1​, id, nombre_estacion, lat_e, lon_e, v2​, v3​, nom_mun, v4​, v5​), wikidata_MUNICIPIO(id_mun, nombre_municipio, hab, coord), lat_m=latitud(coord), lon_m=longitud(coord), INE_MUNICIPIO(cmun, cpro, v8​, v9​), INE_PROVINCIA(cpro, prov, v10​, ccaa), id_mun=cmun+cpro, hab<10000
```

#### Reformulación LAV

Para hacer la reformulación LAV debemos utilizar el algoritmo basado en buckets. 

1. Creamos y llenamos los buckets: como hay dos átomos en la consulta, creamos dos buckets. Para que una vista forme parte de un bucket es necesario que cumpla tres condiciones:
    a. Un átomo de la vista y el átomo g para el cual construimos el bucket afectan a la misma relación.
    b. Los predicados (condiciones) de la vista y los de la consulta Q son mutuamente satisfacibles.
    c. Si en g aparece alguna variable cabecera de la consulta Q, entonces también debe aparecer en la cabecera de la vista.

Siguiendo las normas de construcción de buckets, para el primer átomo, su bucket estará compuesto únimamente por *wikidata_ESTACION*, que se añade al bucket. El segundo bucket estará compuesto únicamente por la fuente *wikidata_MUNICIPIO*, que se añade al segundo bucket.

2. Reformulación como producto cartesiano: hacemos el producto cartesiano entre los buckets. Como solo hay una posibilidad por bucket solo podremos hacer una reformulación. Si nos fijamos, esta reformulación será la misma que la reformulación GAV:

```
Q1''(id, nombre_estacion, nombre_municipio):- data_renfe_ESTACION(v1​, id, nombre_estacion, lat_e, lon_e, v2​, v3​, nom_mun, v4​, v5​), wikidata_MUNICIPIO(id_mun, nombre_municipio, v6​, v7​), wikidata_MUNICIPIO(id_mun, nombre_municipio, hab, coord), lat_m=latitud(coord), lon_m=longitud(coord), INE_MUNICIPIO(cmun, cpro, v8​, v9​), INE_PROVINCIA(cpro, prov, v10​, ccaa), id_mun=cmun+cpro, hab<10000
```

3. Posible simplificación: como ya vimos anteriormente, es posible simplificar la consulta, por lo que el resultado final es:

```
Q1'(id, nombre_estacion, nombre_municipio):- data_renfe_ESTACION(v1​, id, nombre_estacion, lat_e, lon_e, v2​, v3​, nom_mun, v4​, v5​), wikidata_MUNICIPIO(id_mun, nombre_municipio, hab, coord), lat_m=latitud(coord), lon_m=longitud(coord), INE_MUNICIPIO(cmun, cpro, v8​, v9​), INE_PROVINCIA(cpro, prov, v10​, ccaa), id_mun=cmun+cpro, hab<10000
```

Como ya hemos visto, la reformulación LAV y GAV coinciden aunque hayamos utilizado diferentes algoritmos para su construcción. Es por esto que para las siguientes dos consultas únicamente se dejará indicada la reformulación final.

### Consulta 2

Esta consulta tiene un `OR` para poder trabajar con la tabla distancia. Es por ello que la consulta se define como:
$$
Q2=Q2_a\cup Q2_b
$$

Estas subconsultas se pueden escribir sobre el esquema mediador como:

```
Q2a(id):- Viaje(id, ruta, v1, v2), Ruta(ruta, origen, destino, v3), Distancia(origen, destino, dist), dist<30
```
```
Q2a(id):- Viaje(id, ruta, v1, v2), Ruta(ruta, origen, destino, v3), Distancia(destino, origen, dist), dist<30
```

#### Reformulación GAV/LAV

La consulta queda extremadamente larga, puesto que para calcular distancias hay que cruzar datos con la vista auxiliar

```
Q2a'​(id):− Parada_aux(ruta, num_secuencia, nombre_parada), nombre_origen=getMinSecuencia(num_secuencia), data_renfe_ESTACION(v1, estacion, nombre_origen, v3, v4, v5, v6, v7, v8, pais), adif_SALIDAS(fecha, horario, v10, v11, estacion), id=secuencia(), pais==España, 
```


### Consulta 3
