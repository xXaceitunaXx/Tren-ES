CREATE TABLE Ruta (
    id INT PRIMARY KEY,
    origen INT NOT NULL,
    destino INT NOT NULL,
    tipo VARCHAR(50),
    FOREIGN KEY (origen) REFERENCES Estacion(id),
    FOREIGN KEY (destino) REFERENCES Estacion(id)
);

