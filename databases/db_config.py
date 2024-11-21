# db_config.py
import os
import pyodbc
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

# Imprimir los valores para depuración
print(f"DB_SERVER: {DB_SERVER}")
print(f"DB_NAME: {DB_NAME}")


# Función para obtener la conexión a la base de datos (usando autenticación de Windows)
def get_connection():
    try:
        # Cambiar la conexión a autenticación de Windows
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                     f'SERVER={DB_SERVER};'
                     f'DATABASE={DB_NAME};'
                     f'Trusted_Connection=yes;')
        print("Conexión exitosa a la base de datos.")
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
