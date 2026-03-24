SELECT E.id, E.nombre AS estacion, M.nombre AS municipio
	FROM Estacion AS E
	INNER JOIN Municipio AS M
		ON E.municipio = M.id
	WHERE M.n_habitantes < 10000;

SELECT V.id
	FROM Viaje AS V
	INNER JOIN Ruta AS R
		ON V.ruta = R.id
	INNER JOIN Distancia AS D
		ON (R.origen = D.estacion1 AND R.destino = D.estacion2) -- Asumimos que construimos la tabla Distancia de forma simétrica
	WHERE D.distancia < 30;


SELECT V.id, E1.nombre AS estacion_origen, E2.nombre AS estacion_destino, D.distancia
	FROM Poblaciones AS P
	INNER JOIN Viajes AS V
    		ON P.localidad = V.origen
	WHERE P.poblacion > 20000 AND P.poblacion < 100000
		AND V.fecha = CURRENT_DATE
	GROUP BY P.localidad
	HAVING COUNT(V.id) < 5;

SELECT M.id, M.nombre, COUNT(DISTINCT V.id) AS num_viajes_hoy
	FROM Municipio AS M
	LEFT JOIN Estacion AS E -- Utilizamos LEFT JOIN para incluir municipios sin estaciones, paradas o viajes
		ON E.municipio = M.id
	LEFT JOIN Parada AS P
		ON P.estacion = E.id
	LEFT JOIN Viaje AS V
		ON V.ruta = P.ruta
	AND V.fecha = CURRENT_DATE
	WHERE M.n_habitantes BETWEEN 20000 AND 100000
	GROUP BY M.id, M.nombre
	HAVING COUNT(DISTINCT V.id) < 5;