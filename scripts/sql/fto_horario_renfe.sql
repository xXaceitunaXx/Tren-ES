DROP TABLE IF EXISTS horarios_renfe_HORARIO;
DROP TABLE IF EXISTS horarios_renfe_RUTA;

CREATE TABLE horarios_renfe_RUTA (
    PARADAS TEXT,         -- NOMBRE ESTACIONES (Lista)
    CODIGO INT PRIMARY KEY -- CÓDIGO DE RUTA
);

CREATE TABLE horarios_renfe_HORARIO (
    RECORRIDO INT,          -- TREN/RECORRIDO (FK to RUTA.CODIGO)
    SALIDA TIME,
    LLEGADA TIME,
    DURACION VARCHAR(50),    -- HORAS/MINUTOS
    PRIMARY KEY (RECORRIDO, SALIDA),
    FOREIGN KEY (RECORRIDO) REFERENCES horarios_renfe_RUTA(CODIGO)
);

INSERT INTO horarios_renfe_RUTA (CODIGO, PARADAS) VALUES 
(101, 'Madrid-Segovia-Valladolid'),
(102, 'Madrid-Ciudad Real-Cordoba-Sevilla'),
(103, 'Valladolid-Palencia-Leon');

INSERT INTO horarios_renfe_HORARIO (RECORRIDO, SALIDA, LLEGADA, DURACION) VALUES 
(101, '08:00:00', '09:05:00', '1h 05m'),
(101, '15:00:00', '16:05:00', '1h 05m'),
(102, '09:00:00', '11:30:00', '2h 30m'),
(103, '10:00:00', '11:15:00', '1h 15m');