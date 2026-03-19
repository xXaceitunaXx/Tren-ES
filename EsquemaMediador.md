* Estacion(**id**, nombre, _municipio_, latitud, longitud)
* Municipio(nombre, n_habitantes, **id**, latitud, longitud, provincia, CCAA)
* Viaje(**id**, _ruta_, fecha, horario)
* Parada(***ruta***, ***estacion***, n_secuencia, km_origen)
* Ruta(**id**, _origen_, _destino_, tipo)

```mermaid
erDiagram
    MUNICIPIO {
        string id PK
        string nombre
        int n_habitantes
        float latitud
        float longitud
        string provincia
        string CCAA
    }

    ESTACION {
        string id PK
        string municipio FK
        string nombre
        float latitud
        float longitud
    }

    RUTA {
        string id PK
        string origen FK
        string destino FK
        string tipo
    }

    VIAJE {
        string id PK
        string ruta FK
        date fecha
        string horario
    }

    PARADA {
        string ruta PK,FK
        string estacion PK,FK
        int n_secuencia
        float km_origen
    }

    %% Relaciones
    MUNICIPIO ||--o{ ESTACION : "tiene"
    ESTACION ||--o{ RUTA : "es origen de"
    ESTACION ||--o{ RUTA : "es destino de"
    RUTA ||--o{ VIAJE : "planifica"
    RUTA ||--|{ PARADA : "se compone de"
    ESTACION ||--o{ PARADA : "pertenece a"
```
