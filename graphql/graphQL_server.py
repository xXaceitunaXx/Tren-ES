import uuid
import os
import pandas as pd
import strawberry
from dotenv import load_dotenv
from sqlalchemy import create_engine
from typing import List
from obtener_salidas import obtener_salidas_adif
from strawberry.scalars import JSON

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
    origen: str
    destinos: JSON
    

@strawberry.type
class DatosConsulta3:
    nombre: str
    numero_habitantes: int
    numero_paradas: int
    
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
        SELECT R.id AS ruta_id, R.origen AS estacion_origen, M.nombre AS municipio, R.destino AS estacion_destino
        FROM Ruta AS R
        INNER JOIN Distancia AS D
            ON (R.origen = D.estacion1 AND R.destino = D.estacion2) OR
               (R.origen = D.estacion2 AND R.destino = D.estacion1)
        INNER JOIN Estacion AS E
            ON R.origen = E.id
        INNER JOIN Municipio AS M
            ON E.Municipio = M.id
        WHERE D.distancia < {max_distancia}
        LIMIT {limite};"""
        
        df = pd.read_sql(consulta2, motor)
        lista_viajes = []
        estaciones_viajes = {} # Cunjunto de estaciones, no se hace más scraping del necesario
        
        for _, fila in df.iterrows():
            estacion_origen = str(fila["estacion_origen"])
            estacion_destino = str(fila["estacion_destino"])
            nombre_municipio = str(fila["municipio"])
           
            
            if estacion_origen not in estaciones_viajes:
            
                try:
                    viajes = await obtener_salidas_adif(estacion_origen, nombre_municipio)
                    estaciones_viajes[estacion_origen] =viajes
                    
                except Exception as error:
                    print(f"Error en: {estacion_origen}, {print(error)}")
                    estaciones_viajes[estacion_origen] = []
            
            trayecto = estaciones_viajes[estacion_origen]
            
            if trayecto: # Si funciona el scraping
                for tren in trayecto:
                    lista_viajes.append(DatosConsulta2(
                        id=str(uuid.uuid4()), # Hacemos un ID para poder guardarlo si lo necesitamos
                        origen=nombre_municipio,
                        destinos = tren
                    ))
            else:
                lista_viajes.append(DatosConsulta2(
                    id=str(uuid.uuid4()), 
                    origen=nombre_municipio,
                    destinos = f"Sin datos disponibles a tiempo real"    
                ))
                
        return lista_viajes
    
    @strawberry.field
    def consulta3(self, poblacion_min: int = 20000, poblacion_max: int = 100000, limite: int = 20,
                  rutas_min: int = 1, rutas_max: int = 5) -> List[DatosConsulta3]:
        motor = conectar_bd()
        consulta3 = f"""
        SELECT 
            M.nombre, 
            M.n_habitantes,
            COUNT(P.ruta) AS total_paradas
        FROM Municipio M
        INNER JOIN Estacion E 
            ON M.id = E.municipio
        INNER JOIN Parada P 
            ON E.id = P.estacion
        WHERE M.n_habitantes BETWEEN {poblacion_min} AND {poblacion_max}
        GROUP BY M.id, M.nombre, M.n_habitantes
        HAVING COUNT(DISTINCT P.ruta) BETWEEN {rutas_min} AND {rutas_max}
        LIMIT {limite};"""
        
        df = pd.read_sql(consulta3, motor)
        
        lista_estaciones = []
        for _, fila in df.iterrows():
            lista_estaciones.append(DatosConsulta3(
                nombre=str(fila["nombre"]),
                numero_habitantes=str(fila["n_habitantes"]),
                numero_paradas=str(fila["total_paradas"]) 
            ))
            
        return lista_estaciones

schema = strawberry.Schema(query=Query)