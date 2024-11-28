from databases.db_config import get_connection
import os

# obtiene la variable DB_NAME desde la configuración
DB_NAME = os.getenv("DB_NAME")

# crea la base de datos si no existe
def create_database():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # verifica si la base de datos ya existe
            cursor.execute(
                f"SELECT database_id FROM sys.databases WHERE name = '{DB_NAME}';")
            result = cursor.fetchone()
            if not result:
                # Si la base de datos no existe, crearla
                cursor.execute(f"CREATE DATABASE {DB_NAME};")
                conn.commit()
                print(f"Base de datos '{DB_NAME}' creada exitosamente.")
            else:
                print(f"La base de datos '{DB_NAME}' ya existe.")
        except Exception as e:
            print(f"Error al crear la base de datos: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("No se pudo establecer la conexión para crear la base de datos.")

# Crear las tablas en la base de datos
def create_tables():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Asegurarse de usar la base de datos correcta
            cursor.execute(f"USE {DB_NAME};")

            # Crear tablas
            cursor.execute("""IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Producto' AND xtype='U')
        CREATE TABLE Producto (
            idProducto INT PRIMARY KEY IDENTITY(1,1),
            nombreProducto VARCHAR(100),
            cantidadDisponible INT,
            precioUnitario DECIMAL(18,2),
            precioVenta DECIMAL(18,2),
            categoriaProducto VARCHAR(100)
        );
        
        
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Proveedor' AND xtype='U')
        CREATE TABLE Proveedor (
            idProveedor INT PRIMARY KEY IDENTITY(1,1),
            nombreProveedor VARCHAR(100),
            telefonoProveedor VARCHAR(15),
            direccionProveedor VARCHAR(100)
        );
        
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ProductoIngresado' AND xtype='U')
        CREATE TABLE ProductoIngresado (
            idProdIngresado INT PRIMARY KEY IDENTITY(1,1),
            cantidad INT,
            precioUnitarioIng DECIMAL(18,2),
            fechaIngreso DATE,
            idProducto INT,
            idProveedor INT,
            FOREIGN KEY (idProducto) REFERENCES Producto(idProducto),
            FOREIGN KEY (idProveedor) REFERENCES Proveedor(idProveedor)
        );

        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ProductoSaliente' AND xtype='U')
        CREATE TABLE ProductoSaliente (
            idProdSaliente INT PRIMARY KEY IDENTITY(1,1),
            cantidad INT,
            ganancia DECIMAL(18,2),
            fechaSalida DATE,
            descripcion VARCHAR(100),
            idProducto INT,
            FOREIGN KEY (idProducto) REFERENCES Producto(idProducto)
        );
    """)
            conn.commit()
            print("Tablas creadas correctamente.")
        except Exception as e:
            print(f"Error al crear las tablas: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("No se pudo establecer la conexión para crear las tablas.")
