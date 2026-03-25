/*
    Script de despliegue de la base de datos con esquema 
    mediador.

    Tren-ES

    authors:
        Sergio Velasco de Pedro
        Víctor Elvira Fernández
        Juan Horrillo Crespo
*/

-- 1. Eliminación de tablas existentes
DROP TABLE IF EXISTS Viaje;
DROP TABLE IF EXISTS Parada;
DROP TABLE IF EXISTS Distancia;
DROP TABLE IF EXISTS Ruta;
DROP TABLE IF EXISTS Estacion;
DROP TABLE IF EXISTS Municipio;

-- 2. Creación de tablas

-- Tabla Municipio
CREATE TABLE Municipio (
    id INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    n_habitantes INT,
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6),
    provincia VARCHAR(100),
    ccaa VARCHAR(100)
);

-- Tabla Estacion
CREATE TABLE Estacion (
    id INT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    municipio_id INT NOT NULL,
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6),
    FOREIGN KEY (municipio_id) REFERENCES Municipio(id)
);

-- Tabla Ruta
CREATE TABLE Ruta (
    id INT PRIMARY KEY,
    origen INT NOT NULL,
    destino INT NOT NULL,
    tipo VARCHAR(50),
    FOREIGN KEY (origen) REFERENCES Estacion(id),
    FOREIGN KEY (destino) REFERENCES Estacion(id)
);

-- Tabla Distancia
CREATE TABLE Distancia (
    estacion1 INT NOT NULL,
    estacion2 INT NOT NULL,
    distancia DECIMAL(8,2) NOT NULL,
    PRIMARY KEY (estacion1, estacion2),
    FOREIGN KEY (estacion1) REFERENCES Estacion(id),
    FOREIGN KEY (estacion2) REFERENCES Estacion(id)
);

-- Tabla Parada
CREATE TABLE Parada (
    ruta INT NOT NULL,
    estacion INT NOT NULL,
    n_secuencia INT NOT NULL,
    km_origen DECIMAL(8,2),
    PRIMARY KEY (ruta, n_secuencia),
    FOREIGN KEY (ruta) REFERENCES Ruta(id),
    FOREIGN KEY (estacion) REFERENCES Estacion(id)
);

-- Tabla Viaje
CREATE TABLE Viaje (
    id INT PRIMARY KEY,
    ruta INT NOT NULL,
    fecha DATE NOT NULL,
    horario TIME NOT NULL,
    FOREIGN KEY (ruta) REFERENCES Ruta(id)
);

-- 3. Inserción de tuplas de ejemplo

INSERT INTO Municipio (id, nombre, n_habitantes, latitud, longitud, provincia, ccaa) VALUES
(1, 'Valladolid', 295639, 41.652300, -4.724500, 'Valladolid', 'Castilla y León'),
(2, 'Segovia', 51378, 40.942900, -4.108800, 'Segovia', 'Castilla y León'),
(3, 'Palencia', 76438, 42.009500, -4.528000, 'Palencia', 'Castilla y León'),
(4, 'Burgos', 175821, 42.343900, -3.696900, 'Burgos', 'Castilla y León'),
(5, 'León', 121281, 42.598700, -5.567100, 'León', 'Castilla y León'),
(6, 'Salamanca', 144436, 40.970100, -5.663500, 'Salamanca', 'Castilla y León'),
(7, 'Zamora', 59475, 41.503300, -5.744600, 'Zamora', 'Castilla y León'),
(8, 'Ávila', 58085, 40.656600, -4.681900, 'Ávila', 'Castilla y León'),
(9, 'Soria', 39821, 41.763300, -2.468800, 'Soria', 'Castilla y León'),
(10, 'Madrid', 3556, 40.416800, -3.703800, 'Madrid', 'Comunidad de Madrid');

INSERT INTO Estacion (id, nombre, municipio_id, latitud, longitud) VALUES
(1, 'Valladolid Campo Grande', 1, 41.642000, -4.727000),
(2, 'Segovia Guiomar', 2, 40.910000, -4.094000),
(3, 'Palencia', 3, 42.015000, -4.534000),
(4, 'Burgos Rosa Manzano', 4, 42.367000, -3.666000),
(5, 'León', 5, 42.594000, -5.582000),
(6, 'Salamanca', 6, 40.958000, -5.671000),
(7, 'Zamora', 7, 41.515000, -5.751000),
(8, 'Ávila', 8, 40.656000, -4.700000),
(9, 'Soria', 9, 41.768000, -2.468000),
(10, 'Madrid Chamartín-Clara Campoamor', 10, 40.472200, -3.682600);

INSERT INTO Ruta (id, origen, destino, tipo) VALUES
(1, 1, 10, 'AVE'),
(2, 10, 1, 'AVE'),
(3, 1, 2, 'AVANT'),
(4, 2, 10, 'AVE'),
(5, 1, 3, 'Media Distancia'),
(6, 3, 5, 'Media Distancia'),
(7, 6, 7, 'Regional'),
(8, 8, 10, 'Media Distancia'),
(9, 4, 1, 'Media Distancia'),
(10, 9, 10, 'Alvia'),
(11, 5, 3, 'Media Distancia'),
(12, 7, 6, 'Regional'),
(13, 10, 8, 'Media Distancia'),
(14, 1, 4, 'Media Distancia'),
(15, 10, 9, 'Alvia');

INSERT INTO Parada (ruta, estacion, n_secuencia, km_origen) VALUES
(1, 1, 1, 0.00),
(1, 10, 2, 13.00),
(2, 10, 1, 0.00),
(2, 1, 2, 13.00),
(3, 1, 1, 0.00),
(3, 2, 2, 108.00),
(4, 2, 1, 0.00),
(4, 10, 2, 92.00),
(5, 1, 1, 0.00),
(5, 3, 2, 50.00),
(6, 3, 1, 0.00),
(6, 5, 2, 127.00),
(7, 6, 1, 0.00),
(7, 7, 2, 66.00),
(8, 8, 1, 0.00),
(8, 10, 2, 115.00),
(9, 4, 1, 0.00),
(9, 3, 2, 90.00),
(9, 1, 3, 140.00),
(10, 9, 1, 0.00),
(10, 10, 2, 231.00),
(11, 5, 1, 0.00),
(11, 3, 2, 127.00),
(12, 7, 1, 0.00),
(12, 6, 2, 66.00),
(13, 10, 1, 0.00),
(13, 8, 2, 115.00),
(14, 1, 1, 0.00),
(14, 3, 2, 50.00),
(14, 4, 3, 140.00),
(15, 10, 1, 0.00),
(15, 9, 2, 231.00);

INSERT INTO Viaje (id, ruta, fecha, horario) VALUES
(1, 1, '2026-03-24', '08:30:00'),
(2, 1, '2026-03-24', '14:00:00'),
(3, 1, '2026-03-25', '18:30:00'),
(4, 2, '2026-03-24', '10:00:00'),
(5, 2, '2026-03-25', '19:00:00'),
(6, 3, '2026-03-24', '09:15:00'),
(7, 3, '2026-03-26', '17:10:00'),
(8, 4, '2026-03-24', '11:20:00'),
(9, 4, '2026-03-25', '16:40:00'),
(10, 4, '2026-03-26', '20:10:00'),
(11, 5, '2026-03-24', '07:45:00'),
(12, 5, '2026-03-25', '15:30:00'),
(13, 5, '2026-03-26', '19:20:00'),
(14, 6, '2026-03-24', '13:10:00'),
(15, 7, '2026-03-24', '18:00:00'),
(16, 7, '2026-03-26', '12:00:00'),
(17, 8, '2026-03-24', '06:50:00'),
(18, 8, '2026-03-25', '16:10:00'),
(19, 8, '2026-03-26', '21:00:00'),
(20, 9, '2026-03-25', '16:30:00'),
(21, 9, '2026-03-26', '09:40:00'),
(22, 10, '2026-03-25', '17:45:00'),
(23, 10, '2026-03-26', '07:30:00'),
(24, 11, '2026-03-24', '12:15:00'),
(25, 12, '2026-03-26', '07:55:00'),
(26, 13, '2026-03-25', '09:05:00'),
(27, 13, '2026-03-26', '13:25:00'),
(28, 14, '2026-03-25', '11:50:00'),
(29, 14, '2026-03-26', '18:05:00'),
(30, 15, '2026-03-25', '15:15:00');


INSERT INTO Distancia (estacion1, estacion2, distancia) VALUES
(1, 1, 0.00),
(1, 2, 97.07),
(1, 3, 44.45),
(1, 4, 119.10),
(1, 5, 127.20),
(1, 6, 109.56),
(1, 7, 86.34),
(1, 8, 109.66),
(1, 9, 188.05),
(1, 10, 156.80),
(2, 1, 97.07),
(2, 2, 0.00),
(2, 3, 128.22),
(2, 4, 165.87),
(2, 5, 224.27),
(2, 6, 132.58),
(2, 7, 154.07),
(2, 8, 58.32),
(2, 9, 165.92),
(2, 10, 59.77),
(3, 1, 44.45),
(3, 2, 128.22),
(3, 3, 0.00),
(3, 4, 81.52),
(3, 5, 107.58),
(3, 6, 150.94),
(3, 7, 115.23),
(3, 8, 151.75),
(3, 9, 173.20),
(3, 10, 185.73),
(4, 1, 119.10),
(4, 2, 165.87),
(4, 3, 81.52),
(4, 4, 0.00),
(4, 5, 159.14),
(4, 6, 228.65),
(4, 7, 196.75),
(4, 8, 208.82),
(4, 9, 119.23),
(4, 10, 210.70),
(5, 1, 127.20),
(5, 2, 224.27),
(5, 3, 107.58),
(5, 4, 159.14),
(5, 5, 0.00),
(5, 6, 182.06),
(5, 7, 120.79),
(5, 8, 227.62),
(5, 9, 272.51),
(5, 10, 283.99),
(6, 1, 109.56),
(6, 2, 132.58),
(6, 3, 150.94),
(6, 4, 228.65),
(6, 5, 182.06),
(6, 6, 0.00),
(6, 7, 62.30),
(6, 8, 88.35),
(6, 9, 282.05),
(6, 10, 176.07),
(7, 1, 86.34),
(7, 2, 154.07),
(7, 3, 115.23),
(7, 4, 196.75),
(7, 5, 120.79),
(7, 6, 62.30),
(7, 7, 0.00),
(7, 8, 129.93),
(7, 9, 274.24),
(7, 10, 208.75),
(8, 1, 109.66),
(8, 2, 58.32),
(8, 3, 151.75),
(8, 4, 208.82),
(8, 5, 227.62),
(8, 6, 88.35),
(8, 7, 129.93),
(8, 8, 0.00),
(8, 9, 223.92),
(8, 10, 88.34),
(9, 1, 188.05),
(9, 2, 165.92),
(9, 3, 173.20),
(9, 4, 119.23),
(9, 5, 272.51),
(9, 6, 282.05),
(9, 7, 274.24),
(9, 8, 223.92),
(9, 9, 0.00),
(9, 10, 176.38),
(10, 1, 156.80),
(10, 2, 59.77),
(10, 3, 185.73),
(10, 4, 210.70),
(10, 5, 283.99),
(10, 6, 176.07),
(10, 7, 208.75),
(10, 8, 88.34),
(10, 9, 176.38),
(10, 10, 0.00);

-- 4. Consultas

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