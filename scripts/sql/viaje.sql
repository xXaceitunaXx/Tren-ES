CREATE TABLE Viaje (
    id INT PRIMARY KEY,
    ruta INT NOT NULL,
    fecha DATE NOT NULL,
    horario TIME NOT NULL,
    FOREIGN KEY (ruta) REFERENCES Ruta(id)
);

