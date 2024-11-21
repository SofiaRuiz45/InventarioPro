from databases.db_init import create_database, create_tables

# Llamar a las funciones para crear la base de datos y las tablas
if __name__ == "__main__":
    print("Iniciando la creación de la base de datos y las tablas...")
    create_database()  # Crear la base de datos si no existe
    create_tables()    # Crear las tablas en la base de datos
    print("Proceso completado.")
