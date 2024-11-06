-- Crear base de datos
CREATE DATABASE inventario;
GO

-- Usar la base de datos inventario
USE inventario;
GO

BEGIN TRANSACTION;

-- Crear tabla Producto
CREATE TABLE Producto (
    idProducto INT PRIMARY KEY IDENTITY(1,1),
    nombreProducto VARCHAR(255) NOT NULL,
    cantidadDisponible INT NOT NULL,
    categoriaProducto VARCHAR(255) NOT NULL
);

-- Insertar datos en la tabla Producto
INSERT INTO Producto (nombreProducto, cantidadDisponible, categoriaProducto)
VALUES
('Pepas', 25, 'galletas'),
('Spaghetti', 50, 'fideos'),
('Spaghetti', 50, 'fideos'),
('Tallarines', 25, 'fideos'),
('Tallarines', 25, 'fideos'),
('Tallarines', 25, 'fideos'),
('Tallarines', 25, 'fideos'),
('Tallarines', 25, 'fideos'),
('Tallarines', 25, 'fideos'),
('Tallarines', 25, 'fideos'),
('Pepas', 45, 'galletas'),
('Arroz', 35, 'otros');

-- Crear tabla Proveedor
CREATE TABLE Proveedor (
    idProveedor INT PRIMARY KEY IDENTITY(1,1),
    nombreProveedor VARCHAR(255) NOT NULL,
    telefonoProveedor VARCHAR(20) NOT NULL, 
    direccionProveedor VARCHAR(255) NOT NULL
);

-- Crear tabla OrdenCompra
CREATE TABLE OrdenCompra (
    idOrdenCompra INT PRIMARY KEY IDENTITY(1,1),
    fechaOrden DATE NOT NULL,
    cantidadTotal INT NOT NULL,
    precioTotal DECIMAL(10, 2) NOT NULL, -- DECIMAL(10,2) para mayor precisión
    estado VARCHAR(255) NOT NULL
);

-- Crear tabla ProductoIngresado
CREATE TABLE ProductoIngresado (
    idProdIngresado INT PRIMARY KEY IDENTITY(1,1),
    cantidad INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    fechaIngreso DATE NOT NULL,
    idProducto INT,
    idProveedor INT,
    idOrdenCompra INT,
    FOREIGN KEY (idProducto) REFERENCES Producto(idProducto),
    FOREIGN KEY (idProveedor) REFERENCES Proveedor(idProveedor),
    FOREIGN KEY (idOrdenCompra) REFERENCES OrdenCompra(idOrdenCompra)
);

COMMIT;
GO
