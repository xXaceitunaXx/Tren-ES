import os
import pandas as pd
import strawberry
from dotenv import load_dotenv
from sqlalchemy import create_engine
from typing import List

def conectar_bd():
    load_dotenv()
    user = os.getenv("DB_USER", "test")
    password = os.getenv("DB_PASSWD", "test")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB", "testdb")
    
    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(url)


@strawberry.type
class MunicipioBD:
    id: str
    nombre: str
    n_habitantes: int
    
@strawberry.type
class DatosConsulta1:
    id: int
    nombre_estacion: str
    nombre_municipio: str

@strawberry.type
class Query:
    @strawberry.field
    def probar_municipios(self, limite: int = 5) -> List[MunicipioBD]:

        motor = conectar_bd()        
        consulta = f"SELECT id, nombre, n_habitantes FROM Municipio LIMIT {limite};"
        
        df = pd.read_sql(consulta, motor)
        
        # Hacer la lista de municipios a partir del objeto pandas
        lista_municipios = []
        for _, fila in df.iterrows():
            lista_municipios.append(MunicipioBD(
                id=str(fila["id"]),
                nombre=str(fila["nombre"]),
                # Usamos un pequeño seguro por si hay nulos en la BD
                n_habitantes=int(fila["n_habitantes"]) if pd.notna(fila["n_habitantes"]) else 0 
            ))
            
        return lista_municipios
    
    @strawberry.field
    def total_municipios(self) -> int:
        motor = conectar_bd()
        consulta = "SELECT COUNT(*) as total FROM Municipio;"
        df = pd.read_sql(consulta, motor)
        
        return int(df.iloc[0]["total"])
    
    @strawberry.field
    def consulta1(self, limite: int = 20) -> List[DatosConsulta1]:
        motor = conectar_bd()
        consulta = f"""
        SELECT E.id, E.nombre AS estacion, M.nombre AS municipio
        FROM Estacion AS E
        INNER JOIN Municipio AS M
            ON E.municipio = M.id
        WHERE M.n_habitantes > 10000
        LIMIT {limite};"""
        
        df = pd.read_sql(consulta, motor)
        
        lista_estaciones = []
        for _, fila in df.iterrows():
            lista_estaciones.append(DatosConsulta1(
                id=str(fila["id"]),
                nombre_estacion=str(fila["estacion"]),
                nombre_municipio=str(fila["municipio"]) 
            ))
            
        return lista_estaciones

schema = strawberry.Schema(query=Query)