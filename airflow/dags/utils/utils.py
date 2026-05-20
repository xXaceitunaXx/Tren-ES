from airflow.sdk.bases.hook import BaseHook
from sqlalchemy import create_engine

import unicodedata
import csv

def to_csv(path, data):
    keys = data[0].keys()
    with open(path, "w", encoding="utf-8") as fichero:
        writer = csv.DictWriter(fichero, keys)
        writer.writeheader()
        writer.writerows(data)


def connect_database():
    conn = BaseHook.get_connection("warehouse_mariadb")
    engine = create_engine(f"mysql+pymysql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}")
    return engine


def normalize_unicode(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize('NFKD', text.upper()) 
        if unicodedata.category(c) == 'Lu'
    )


SUBSET_ESTACIONES = {
    # Valladolid
    "10602",
    "32002",
    "10604",
    "32003",
    "10502",
    "8240",
    "10500",
    "31002",
    "10501",
    "10503",
    "10600",
    "10610",
    "10504",

    # Palencia
    "14113",
    "14114",
    "14112",
    "14102",
    "11000",
    "15003",
    "15006",
    "10605",
    "14108",
    "14104",
    "15001",
    "14111",
    "11004",
    "14101",
    "14117",
    "14100",
    "15004",
    "14103",
    "14115",
    "11006",
    "15007",
    "14107"
}