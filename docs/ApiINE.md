## INE

El Instituto Nacional de Estadística (INE) proporciona datos de todo tipo. La información sobre economía, geografía o demografía se encuentra entre lo más importante. Recientemente el INE comenzó a ofrecer una alternativa a su portal de datos para descargar información, la API [Tempus](https://ine.es/dyngs/DAB/index.htm?cid=1099). Desde esta API, entre otras cosas, se puede acceder al catálogo de Variables, Tablas, Series o Publicaciones, y al contenido de estos. 

Nuestro objetivo es acceder a las variables del INE que cruzan los nombres de municipio con su código y el de la provincia en el que se encuentran, así mismo también nos interesa guardar la Comunidad Autónoma (CCAA) a la que pertenece dicha provincia, por lo que buscamos las variables Municipio y Provincia.

Para acceder a los valores de una variable es necesario conocer su código. Este catálogo de variables se encuentra en el endpoint `VARIABLES`. Las variables Municipio y Provincia corresponden a los códigos 19 y 115 respectivamente.

> Como curiosidad, el contenido de `VARIABLES` no son datos en si, sino los nombres que se usan para dividir y cruzar datos de las series o tablas; por ejemplo, mostrar la evolución del PIB por provincias, o el número de personas paradas en cada año, por sexo, por nivel de formación digital...

Los valores se obtienen con una simple request http sobre el endpoint `VALORES_VARIABLE/{CODIGO}`. Para obtener la información sobre la CCAA de cada provincia es necesario soliciar información más completa. Para ello, se ha de añadir el parámetro `det` (detalle) con valor 2 (el máximo).

Al realizar el script nos encontramos con que la API no se comportaba como se esperaba. Según la documentación, existe un parámetro de página para que los datos se manden de 500 en 500. Sin embargo, por mucho provar nunca funcionó. La API es muy lenta, parece muy mal optimizada, y al descargar los aproximadamente 8000 municipios de España se demoraba varios minutos. Al final, no pudimos resolverlo, esto hizo que tomasemos la decisión de almacenar estos datos como un Warehouse, ya que no tendría sentido trabajar con semejante latencia para cada consulta que involucrase a los municipios.
