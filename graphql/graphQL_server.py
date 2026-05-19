import uuid
import os
import pandas as pd
import strawberry
from dotenv import load_dotenv
from sqlalchemy import create_engine
from typing import List
from obtener_salidas import obtener_salidas_adif

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
class DatosConsulta1:
    id: int
    nombre_estacion: str
    nombre_municipio: str
    
@strawberry.type
class DatosConsulta2:
    id: str
    ruta_id: str
    tren: str
    destino: str

@strawberry.type
class Query:
    @strawberry.field
    def consulta1(self, n_habit: int = 10000, limite: int = 20) -> List[DatosConsulta1]:
        motor = conectar_bd()
        consulta1 = f"""
        SELECT E.id, E.nombre AS estacion, M.nombre AS municipio
        FROM Estacion AS E
        INNER JOIN Municipio AS M
            ON E.municipio = M.id
        WHERE M.n_habitantes < {n_habit}
        LIMIT {limite};"""
        
        df = pd.read_sql(consulta1, motor)
        
        lista_estaciones = []
        for _, fila in df.iterrows():
            lista_estaciones.append(DatosConsulta1(
                id=str(fila["id"]),
                nombre_estacion=str(fila["estacion"]),
                nombre_municipio=str(fila["municipio"]) 
            ))
            
        return lista_estaciones

    @strawberry.field
    async def consulta2(self, max_distancia: float = 30, limite: int = 20) -> List[DatosConsulta2]:
        motor = conectar_bd()
        consulta2 = f"""
        SELECT R.id AS ruta_id, R.origen AS estacion_origen, M.nombre AS municipio
        FROM Ruta AS R
        INNER JOIN Distancia AS D
            ON (R.origen = D.estacion1 AND R.destino = D.estacion2) OR
               (R.origen = D.estacion2 AND R.destino = D.estacion1)
        INNER JOIN Estacion AS E
            ON R.origen = E.id
        INNER JOIN Municipio AS M
            ON E.municipio = M.id
        WHERE D.distancia < {max_distancia}
        LIMIT {limite};"""
        
        df = pd.read_sql(consulta2, motor)
        lista_viajes = []
        
        for _, fila in df.iterrows():
            estacion_origen = str(fila["estacion_origen"])
            nombre_municipio = str(fila["municipio"])
            ruta_id = str(fila["ruta_id"])
            
            try:
                # Llamamos a Adif usando el origen de esa ruta
                #viajes_adif = obtener_salidas_adif(estacion_origen, nombre_municipio)
                viajes= await obtener_salidas_adif(17000, "MADRID")
                
            except Exception as error:
                print("A")
                
            # Por cada tren que encontremos en la web, "creamos" una entidad Viaje
            for tren in viajes:
                lista_viajes.append(DatosConsulta2(
                    id=str(uuid.uuid4()), # Generamos un ID virtual único
                    ruta_id=ruta_id,
                    tren=tren.get("tren", "Desconocido"),
                    destino=tren.get("destino", "Desconocido")
                ))
                
        return lista_viajes

schema = strawberry.Schema(query=Query)