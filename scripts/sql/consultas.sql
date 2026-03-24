-- Consulta 1: Estaciones en municipios con menos de 10000 habitantes
SELECT
	E.id,
	E.nombre AS estacion,
	M.nombre AS municipio
FROM
	Estacion AS E
	INNER JOIN Municipio AS M ON E.municipio_id = M.id
WHERE
	M.n_habitantes < 10000;

-- Consulta 2: Viajes programados que unen dos estaciones a menos de 30 km de distancia
SELECT
	V.id
FROM
	Viaje AS V
	INNER JOIN Ruta AS R ON V.ruta = R.id
	INNER JOIN Distancia AS D ON (
		R.origen = D.estacion1
		AND R.destino = D.estacion2
	)
	OR (
		R.origen = D.estacion2
		AND R.destino = D.estacion1
	)
WHERE
	D.distancia < 30;

-- Consulta 3: Municipios con menos de 5 viajes programados en su estación
SELECT
	M.id,
	M.nombre,
	COUNT(DISTINCT V.id) AS num_viajes_hoy
FROM
	Municipio AS M
	LEFT JOIN Estacion AS E ON E.municipio_id = M.id
	LEFT JOIN Parada AS P ON P.estacion = E.id
	LEFT JOIN Viaje AS V ON V.ruta = P.ruta
	AND V.fecha = CURRENT_DATE
WHERE
	M.n_habitantes BETWEEN 20000 AND 100000
GROUP BY
	M.id,
	M.nombre
HAVING
	COUNT(DISTINCT V.id) < 5;