import os
import argparse
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

GITHUB = "https://github.com/xXaceitunaXx/Tren-ES"
PROTOCOL = "mysql+mysqlconnector"
TEST_SQL = "SELECT nombre FROM Municipio LIMIT 1"

consultas = [
    '''
    SELECT E.id, E.nombre AS estacion, M.nombre AS municipio
	FROM Estacion AS E
	INNER JOIN Municipio AS M
		ON E.municipio_id = M.id
	WHERE M.n_habitantes < 10000;
    ''',
    '''
    SELECT V.id
	FROM Viaje AS V
	INNER JOIN Ruta AS R
		ON V.ruta = R.id
	INNER JOIN Distancia AS D
		ON (R.origen = D.estacion1 AND R.destino = D.estacion2) OR
		(R.origen = D.estacion2 AND R.destino = D.estacion1)
	WHERE D.distancia < 30;
    ''',
    '''
    SELECT M.id, M.nombre, COUNT(DISTINCT V.id) AS num_viajes_hoy
	FROM Municipio AS M
	LEFT JOIN Estacion AS E 
		ON E.municipio_id = M.id
	LEFT JOIN Parada AS P
		ON P.estacion = E.id
	LEFT JOIN Viaje AS V
		ON V.ruta = P.ruta
	AND V.fecha = CURRENT_DATE
	WHERE M.n_habitantes BETWEEN 20000 AND 100000
	GROUP BY M.id, M.nombre
	HAVING COUNT(DISTINCT V.id) < 5;
    '''
]


def get_engine(env_file):
    load_dotenv(env_file)

    user = os.getenv("DB_USER", "test")
    password = os.getenv("DB_PASSWD", "test")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB", "testdb")

    url = f"{PROTOCOL}://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(url)


def launch_query(query, engine):
    print(f"Consulta sql: (texto)")
    print(query)
    print(pd.read_sql(query, engine))
    print("\n---------------------------------\n")


def main():
    parser = argparse.ArgumentParser(
        description="Ejecuta consultas contra la BD del Tren-ES"
    )
    parser.add_argument(
        "--env",
        type=str,
        default=".env",
        help="Ruta del archivo .env (default: .env)",
    )
    args = parser.parse_args()

    env_file = Path(args.env)
    if not env_file.exists():
        print(f"Error: archivo .env no encontrado en {env_file.absolute()}")
        return 1

    print("Test Esquema Intermedio Tren-ES")
    print(f"Repo: {GITHUB}")
    print(f"Usando .env: {env_file.absolute()}\n")

    engine = get_engine(str(env_file))

    if engine:
        print(f"Creada conexión con {engine.url}")

    # Consulta de prueba
    print("Ejecutando consulta de prueba:")
    launch_query(TEST_SQL, engine)

    # Consultas propuestas
    for i, consulta in enumerate(consultas):
        print(f"Ejecutando consulta {i + 1}:")
        launch_query(consulta, engine)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())