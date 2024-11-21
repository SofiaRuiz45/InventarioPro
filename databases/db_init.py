from databases.db_config import get_connection
import os

# Obtener la variable DB_NAME desde la configuración
DB_NAME = os.getenv("DB_NAME")

# Crear la base de datos si no existe


def create_database():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Verificar si la base de datos ya existe
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

            # Crear una tabla de ejemplo
            cursor.execute("""IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Producto' AND xtype='U')
        CREATE TABLE Producto (
            idProducto INT PRIMARY KEY IDENTITY(1,1),
            nombreProducto VARCHAR(100),
            cantidadDisponible INT,
            categoriaProducto VARCHAR(100)
        );
        
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='OrdenCompra' AND xtype='U')
        CREATE TABLE OrdenCompra (
            idOrdenCompra INT PRIMARY KEY IDENTITY(1,1),
            fechaOrden DATE,
            cantidadTotal INT,
            precioTotal DECIMAL(18,2),
            estado VARCHAR(100)
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
            precio DECIMAL(18,2),
            fechaIngreso DATE,
            idProducto INT,
            idProveedor INT,
            idOrdenCompra INT,
            FOREIGN KEY (idProducto) REFERENCES Producto(idProducto),
            FOREIGN KEY (idProveedor) REFERENCES Proveedor(idProveedor),
            FOREIGN KEY (idOrdenCompra) REFERENCES OrdenCompra(idOrdenCompra)
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
