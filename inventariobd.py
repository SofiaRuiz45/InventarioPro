import sqlite3

#conexion a base de datos
conn = sqlite3.connect('inventario.db')
cursor = conn.cursor()

# Crear tabla Producto
cursor.execute('''
CREATE TABLE IF NOT EXISTS Producto (
    idProducto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombreProducto TEXT NOT NULL,
    cantidadDisponible INTEGER NOT NULL,
    categoriaProducto TEXT NOT NULL
)''')

# Crear tabla Proveedor
cursor.execute('''
CREATE TABLE IF NOT EXISTS Proveedor (
    idProveedor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombreProveedor TEXT NOT NULL,
    telefonoProveedor INTEGER NOT NULL,
    direccionProveedor TEXT NOT NULL
)''')
#Si necesitas listar productos asociados a una orden,  hacer una consulta JOIN entre OrdenCompra y ProductoIngresado.
# Crear tabla OrdenCompra
cursor.execute('''CREATE TABLE IF NOT EXISTS OrdenCompra (
                     idOrdenCompra INTEGER PRIMARY KEY AUTOINCREMENT,
                     fechaOrden DATE NOT NULL,
                     cantidadTotal INTEGER NOT NULL,
                     precioTotal REAL NOT NULL,
                     estado TEXT NOT NULL,
                     idInventario INTEGER,
                     FOREIGN KEY (idInventario) REFERENCES Inventario(idInventario)
                  )''')

# Crear tabla ProductoIngresado
cursor.execute('''
CREATE TABLE IF NOT EXISTS ProductoIngresado (
    idProdIngresado INTEGER PRIMARY KEY AUTOINCREMENT,
    cantidad INTEGER NOT NULL,
    precio REAL NOT NULL,
    fechaIngreso DATE NOT NULL,
    idProducto INTEGER,
    idProveedor INTEGER,
    idOrdenCompra INTEGER,
    FOREIGN KEY (idProducto) REFERENCES Producto(idProducto),
    FOREIGN KEY (idProveedor) REFERENCES Proveedor(idProveedor),
    FOREIGN KEY (idOrdenCompra) REFERENCES OrdenCompra(idOrdenCompra)
)''')

conn.commit()
conn.close()
