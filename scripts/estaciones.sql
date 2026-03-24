CREATE TABLE Estacion (
    id INT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    municipio_id INT NOT NULL,
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6),
    FOREIGN KEY (municipio_id) REFERENCES Municipio(id)
);

