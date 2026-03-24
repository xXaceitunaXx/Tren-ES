CREATE TABLE Distancia (
    estacion1 INT NOT NULL,
    estacion2 INT NOT NULL,
    distancia DECIMAL(8,2) NOT NULL,
    PRIMARY KEY (estacion1, estacion2),
    FOREIGN KEY (estacion1) REFERENCES Estacion(id),
    FOREIGN KEY (estacion2) REFERENCES Estacion(id)
);