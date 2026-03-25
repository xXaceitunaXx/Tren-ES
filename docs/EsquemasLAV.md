A partir del esquema mediador y los esquemas de las fuentes de datos, podemos obtener los siguientes esquemas LAV:

### wikidata_MUNICIPIO

Necesitamos concatenar las coordenadas de latitud y longitud extraidas en los esquemas GAV

`wikidata_MUNICIPIO(codigo, label, poblacion, coordenadas)`$\subseteq$

```
Municipio(codigo, label, poblacion, latitud, longitud, v1, v2), 
coordenadas = coords(latitud, longitud)
```

### INE_MUNICIPIO

Como no extraemos el dígito de control dc, no podemos obtenerlo de los esquemas del mediador.

`INE_MUNICIPIO(cmun, cpro, dc, nombre)`$\subseteq$

```
Municipio(id, nombre, v1, v2, v3, v4, v5), id == cmun + cpro
```

### INE_PROVINCIA

Como no extraemos el , no podemos obtenerlo de los esquemas del mediador.

`INE_PROVINCIA(cpro, nombre, codauto, ccaa)`$\subseteq$

```
Municipio(id, nombre, v1, v2, v3, v4, v5), id == cmun + cpro
```

### data_renfe_ESTACION

Como estación venía de un formulario con varios campos que no extraemos, no podemos reconstruir exactamente la fuente completa a partir de nuestros esquemas.

`data_renfe_ESTACION(v1, id, descripcion, latitud, longitud, v2, c_p, poblacion, provincia, pais)`$\subseteq$

```
Estacion(id, id_mun, descripcion, latitud, longitud), 
Municipio(id_mun, poblacion, v3, v4, v5, provincia, v6)
```

### horarios_renfe_RUTA

Al contrario que en los esquemas GAV, debemos crear una lista a partir de nuestros esquemas.

`horarios_renfe_RUTA(codigo, paradas)`$\subseteq$

```
Parada(codigo, estacion, n_secuencia, v4), paradas = list(estacion, n_secuencia)
```

### adif_SALIDAS

No podemos conseguir los campos tren y via desde nuestros esquemas, por lo que la tabla no se puede construir por completo.

`adif_SALIDAS(hora, destino, tren, via, estacion)`$\subseteq$

```
Viaje(id_viaje, ruta, fecha, hora), Ruta(ruta, origen, id_estacion_destino, tipo), 
Estacion(id_estacion_destino, estacion, destino, v2, v3)
```

Al igual que en los esquemas GAV, no se ha considerado ninguna simplificación.
