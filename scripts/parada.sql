CREATE TABLE Parada (
    ruta INT NOT NULL,
    estacion INT NOT NULL,
    n_secuencia INT NOT NULL,
    km_origen DECIMAL(8,2),
    PRIMARY KEY (ruta, n_secuencia),
    FOREIGN KEY (ruta) REFERENCES Ruta(id),
    FOREIGN KEY (estacion) REFERENCES Estacion(id)
);