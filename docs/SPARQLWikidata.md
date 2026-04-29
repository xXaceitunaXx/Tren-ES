# SPARQL 

## WikiData

Los datos de los municipios de España los vamos a coger de [WikiData](https://www.wikidata.org/?uselang=es), mediante un script de *Python* que utilice el servicio de consultas del propio WikiData.

En este caso, la consulta ha sido directa y sencilla, necesitando únicamente el nombre del municipio, la población que tiene y sus coordenadas, en formato POINT. Únicamente hay que tener en cuenta que WikiData puede cancelar la consulta si no se especifica un User-Agent (debido a su política de Robots).

| Columna | Tipo |
| --- | --- |
| CODIGO | text |
| LABEL | text |
| POOBLACION | numeric |
| COORDENADAS | Point |

Para lograrlo, hemos hecho la siguiente consulta:

```sql
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
