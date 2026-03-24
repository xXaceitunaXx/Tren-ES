CREATE TABLE Municipio (
    id INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    n_habitantes INT,
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6),
    provincia VARCHAR(100),
    ccaa VARCHAR(100)
);

