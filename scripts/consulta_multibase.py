import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

PROTOCOL = "mysql+mysqlconnector"

SQL_DB1 = """
SELECT
    CODIGO AS codigo_wikidata,
    LABEL AS nombre_wikidata,
    POBLACION AS poblacion_wikidata
FROM wikidata_MUNICIPIO;
"""

SQL_DB2 = """
SELECT
    CPRO AS cpro,
    CMUN AS cmun,
    NOMBRE AS nombre_ine
FROM INE_MUNICIPIO;
"""


def build_engine(host: str, port: str, db_name: str, user: str, password: str):
    url = f"{PROTOCOL}://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(url)


def run_multibase_query(env_file: Path):
    load_dotenv(env_file)

    user = os.getenv("DB_USER", "test")
    password = os.getenv("DB_PASSWD", "test")
    host = os.getenv("DB_HOST", "localhost")
    db_name1 = os.getenv("DB1", "testdb")
    db_name2 = os.getenv("DB2", "testdb")

    port1 = os.getenv("DB_PORT1") or "3306"
    port2 = os.getenv("DB_PORT2") or "3306"

    engine1 = build_engine(host, port1, db_name1, user, password)
    engine2 = build_engine(host, port2, db_name2, user, password)

    print(f"Conectando DB1 en puerto {port1}")
    print(f"Conectando DB2 en puerto {port2}")

    df_wikidata = pd.read_sql(SQL_DB1, engine1)
    df_ine = pd.read_sql(SQL_DB2, engine2)

    # Clave de cruce INE: CPRO + CMUN (ej. 28 + 079 -> 28079).
    df_ine["codigo_ine"] = (df_ine["cpro"] * 1000 + df_ine["cmun"]).astype(int)
    df_wikidata["codigo_wikidata"] = df_wikidata["codigo_wikidata"].astype(int)

    # Consulta multibase: municipios presentes en ambas fuentes.
    result = pd.merge(
        df_wikidata,
        df_ine,
        left_on="codigo_wikidata",
        right_on="codigo_ine",
        how="inner",
    )
    result = result[[
        "codigo_wikidata",
        "nombre_wikidata",
        "nombre_ine",
        "poblacion_wikidata",
        "cpro",
        "cmun",
    ]].drop_duplicates()

    result = result.sort_values(by=["codigo_wikidata", "nombre_wikidata"]).reset_index(drop=True)
    return result


def main():
    # Para poder utilizar un archivo .env
    parser = argparse.ArgumentParser(
        description="Ejecuta una consulta multibase entre INE_MUNICIPIO y wikidata_MUNICIPIO"
    )
    parser.add_argument(
        "--env",
        type=str,
        default=".env",
        help="Ruta del archivo .env (default: .env)",
    )
    args = parser.parse_args()

    env_path = Path(args.env)
    if not env_path.exists():
        print(f"Error: archivo .env no encontrado en {env_path.absolute()}")
        return 1

    result = run_multibase_query(env_path)

    if result.empty:
        print("No hay coincidencias entre INE_MUNICIPIO y wikidata_MUNICIPIO.")
        return 0

    print("Resultado consulta multibase:")
    print(result.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
