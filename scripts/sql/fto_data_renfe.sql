DROP TABLE IF EXISTS data_renfe_ESTACION;

CREATE TABLE data_renfe_ESTACION (
    ID INT PRIMARY KEY,
    CODIGO NUMERIC,        -- CÓDIGO
    DESCRIPCION VARCHAR(255), -- NOMBRE ESTACIÓN
    LATITUD VARCHAR(50),
    LONGITUD VARCHAR(50),
    DIRECCION VARCHAR(255),   -- DIRECCIÓN
    C_P NUMERIC,           -- C.P.
    POBLACION VARCHAR(255),
    PROVINCIA VARCHAR(255),
    PAIS VARCHAR(100)
);

INSERT INTO data_renfe_ESTACION (ID, CODIGO, DESCRIPCION, LATITUD, LONGITUD, DIRECCION, C_P, POBLACION, PROVINCIA, PAIS) VALUES 
(1, 28001, 'MADRID-PUERTA DE ATOCHA', '40.4063', '-3.6918', 'Plaza del Emperador Carlos V', 28045, 'Madrid', 'Madrid', 'España'),
(2, 47002, 'VALLADOLID-CAMPO GRANDE', '41.6420', '-4.7270', 'Calle de Recondo', 47007, 'Valladolid', 'Valladolid', 'España'),
(3, 41003, 'SEVILLA-SANTA JUSTA', '37.3920', '-5.9750', 'Avenida de Kansas City', 41007, 'Sevilla', 'Sevilla', 'España'),
(4, 39004, 'SANTANDER', '43.4589', '-3.8090', 'Plaza de las Estaciones', 39002, 'Santander', 'Cantabria', 'España');