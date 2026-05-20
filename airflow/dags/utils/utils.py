from airflow.hooks.base import BaseHook
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