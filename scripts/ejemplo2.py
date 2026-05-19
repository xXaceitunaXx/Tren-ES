import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

def probar_conexion():
    print("⏳ Cargando credenciales del .env...")
    load_dotenv()
    
    user = os.getenv("DB_USER", "test")
    password = os.getenv("DB_PASSWD", "test")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB", "testdb")
    
    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
    
    # Ocultamos la contraseña para que no salga en la consola
    url_segura = f"mysql+mysqlconnector://{user}:***@{host}:{port}/{db_name}"
    print(f"🔌 Intentando conectar a: {url_segura}")

    try:
        motor = create_engine(url)
        
        # Intentamos una consulta súper básica
        consulta = "SELECT id, nombre, n_habitantes FROM Municipio LIMIT 5;"
        print(f"🔎 Ejecutando consulta: {consulta}")
        
        df = pd.read_sql(consulta, motor)
        
        print("\n✅ ¡ÉXITO! La conexión funciona perfectamente.")
        print("-" * 40)
        print(df.to_string(index=False))
        print("-" * 40)
        
    except OperationalError as e:
        print("\n❌ ERROR DE CONEXIÓN A LA BASE DE DATOS:")
        print("Esto significa que Python no puede llegar a la máquina virtual.")
        print(f"Detalle técnico: {e}")
    except Exception as e:
        print("\n❌ ERROR INESPERADO:")
        print(f"Detalle técnico: {e}")

if __name__ == "__main__":
    probar_conexion()