START TRANSACTION;

-- Crear tabla Producto
CREATE TABLE Producto (
    idProducto INT PRIMARY KEY AUTO_INCREMENT,
    nombreProducto VARCHAR(255) NOT NULL,
    cantidadDisponible INT NOT NULL,
    categoriaProducto VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- Insertar datos
INSERT INTO Producto (idProducto, nombreProducto, cantidadDisponible, categoriaProducto)
VALUES
(1, 'Pepas', 25, 'galletas'),
(2, 'Spaghetti', 50, 'fideos'),
(3, 'Spaghetti', 50, 'fideos'),
(4, 'Tallarines', 25, 'fideos'),
(5, 'Tallarines', 25, 'fideos'),
(6, 'Tallarines', 25, 'fideos'),
(7, 'Tallarines', 25, 'fideos'),
(8, 'Tallarines', 25, 'fideos'),
(9, 'Tallarines', 25, 'fideos'),
(10, 'Tallarines', 25, 'fideos'),
(11, 'Pepas', 45, 'galletas'),
(12, 'Arroz', 35, 'otros');

-- Crear tabla Proveedor
CREATE TABLE Proveedor (
    idProveedor INT PRIMARY KEY AUTO_INCREMENT,
    nombreProveedor VARCHAR(255) NOT NULL,
    telefonoProveedor VARCHAR(20) NOT NULL, 
    direccionProveedor VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- Crear tabla OrdenCompra
CREATE TABLE OrdenCompra (
    idOrdenCompra INT PRIMARY KEY AUTO_INCREMENT,
    fechaOrden DATE NOT NULL,
    cantidadTotal INT NOT NULL,
    precioTotal DECIMAL(10, 2) NOT NULL, -- Cambiar REAL por DECIMAL(10,2) para mayor precisión
    estado VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- Crear tabla ProductoIngresado
CREATE TABLE ProductoIngresado (
    idProdIngresado INT PRIMARY KEY AUTO_INCREMENT,
    cantidad INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    fechaIngreso DATE NOT NULL,
    idProducto INT,
    idProveedor INT,
    idOrdenCompra INT,
    FOREIGN KEY (idProducto) REFERENCES Producto(idProducto),
    FOREIGN KEY (idProveedor) REFERENCES Proveedor(idProveedor),
    FOREIGN KEY (idOrdenCompra) REFERENCES OrdenCompra(idOrdenCompra)
) ENGINE=InnoDB;

COMMIT;
