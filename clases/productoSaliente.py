from flask import Blueprint, request, render_template, redirect, url_for, current_app
from databases.db_config import get_connection

producto_saliente_bp = Blueprint('productoSaliente', __name__)

# Ruta para registrar un producto saliente
@producto_saliente_bp.route('/registrarProductoSaliente', methods=['GET', 'POST'])
def registrarProductoSaliente():
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        id_producto = request.form.get('idProducto')
        fecha_salida = request.form.get('fechaSalida')
        cantidad_total = int(request.form.get('cantidadTotal'))
        descripcion = request.form.get('descripcion')

        # Conexión a la base de datos
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener datos del producto (precioVenta y cantidadDisponible)
        cursor.execute('SELECT precioVenta, cantidadDisponible FROM Producto WHERE idProducto = ?', (id_producto,))
        resultado = cursor.fetchone()

        if not resultado:
            return "Error: Producto no encontrado", 404

        precio_venta, cantidad_disponible = resultado

        # Verificar cantidad disponible
        if cantidad_disponible < cantidad_total:
            return "Error: Cantidad insuficiente en el inventario", 400

        # Calcular ganancia
        ganancia = round(precio_venta * cantidad_total, 2)

        # Insertar en ProductoSaliente
        cursor.execute('''
    INSERT INTO ProductoSaliente (idProducto, fechaSalida, cantidad, descripcion, ganancia)
    VALUES (?, ?, ?, ?, ?)
''', (id_producto, fecha_salida, cantidad_total, descripcion, ganancia))


        # Actualizar cantidad disponible en Producto
        nueva_cantidad = cantidad_disponible - cantidad_total
        cursor.execute('UPDATE Producto SET cantidadDisponible = ? WHERE idProducto = ?', (nueva_cantidad, id_producto))

        conn.commit()
        conn.close()

        return redirect(url_for('productoSaliente.productosSalientes'))

    # Obtener todos los productos para el formulario
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT idProducto, nombreProducto FROM Producto')
    productos = cursor.fetchall()
    conn.close()

    return render_template('./productoSaliente/registrarProductoSaliente.html', productos=productos)

# Ruta para mostrar productos salientes
@producto_saliente_bp.route('/', methods=['GET'])
def productosSalientes():
    conn = get_connection()
    cursor = conn.cursor()

    # Consulta para obtener los productos salientes con el nombre del producto
    cursor.execute('''
        SELECT ps.idProdSaliente, ps.fechaSalida, ps.cantidad, ps.descripcion, ps.ganancia, p.nombreProducto, p.cantidadDisponible
        FROM ProductoSaliente ps
        JOIN Producto p ON ps.idProducto = p.idProducto
    ''')

    productos_salientes = cursor.fetchall()
    conn.close()

    # Convertimos los resultados en un diccionario para usarlos en la plantilla
    productos_salientes = [
        {
            'idProdSaliente': producto[0],
            'fechaSalida': producto[1],
            'cantidadTotal': producto[2],
            'descripcion': producto[3],
            'ganancia': producto[4],
            'nombreProducto': producto[5],
            'cantidadDisponible': producto[6]
        }
        for producto in productos_salientes
    ]

    return render_template('./productoSaliente/productoSaliente.html', productos_salientes=productos_salientes)


# Ruta para editar un producto saliente
@producto_saliente_bp.route('/editarProductoSaliente/<int:id>', methods=['GET', 'POST'])
def editarProductoSaliente(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nueva_cantidad_total = int(request.form.get('cantidadTotal'))
        nueva_descripcion = request.form.get('descripcion')

        # Obtener datos actuales del producto saliente
        cursor.execute('SELECT idProducto, cantidadTotal FROM ProductoSaliente WHERE idProdSaliente = ?', (id,))
        resultado = cursor.fetchone()
        if not resultado:
            return "Error: Producto saliente no encontrado", 404

        id_producto, cantidad_anterior = resultado

        # Verificar cantidad disponible
        cursor.execute('SELECT precioVenta, cantidadDisponible FROM Producto WHERE idProducto = ?', (id_producto,))
        precio_venta, cantidad_disponible = cursor.fetchone()

        # Calcular el impacto en la cantidad disponible
        diferencia = nueva_cantidad_total - cantidad_anterior
        if cantidad_disponible < diferencia:
            return "Error: Cantidad insuficiente en el inventario", 400

        nueva_cantidad_disponible = cantidad_disponible - diferencia

        # Calcular ganancia
        nueva_ganancia = round(precio_venta * nueva_cantidad_total, 2)

        # Actualizar ProductoSaliente y Producto
        cursor.execute('''
            UPDATE ProductoSaliente
            SET cantidadTotal = ?, descripcion = ?, ganancia = ?
            WHERE idProdSaliente = ?
        ''', (nueva_cantidad_total, nueva_descripcion, nueva_ganancia, id))
        cursor.execute('UPDATE Producto SET cantidadDisponible = ? WHERE idProducto = ?', (nueva_cantidad_disponible, id_producto))

        conn.commit() 
        conn.close()
        return redirect(url_for('productoSaliente.productosSalientes'))

    # Obtener datos actuales para mostrar en el formulario
    cursor.execute('SELECT * FROM ProductoSaliente WHERE idProdSaliente = ?', (id,))
    column_names = [desc[0] for desc in cursor.description]
    producto_saliente = dict(zip(column_names, cursor.fetchone()))

    # Obtener todos los productos para el dropdown
    cursor.execute('SELECT idProducto, nombreProducto FROM Producto')
    productos = cursor.fetchall()

    conn.close()

    return render_template('./productoSaliente/editarProductoSaliente.html', producto_saliente=producto_saliente, productos=productos)



# Ruta para eliminar un producto saliente
@producto_saliente_bp.route('/eliminarProductoSaliente/<int:id>', methods=['POST'])
def eliminarProductoSaliente(id):
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener el producto saliente para obtener la cantidad y el id del producto
    cursor.execute('SELECT idProducto, cantidad FROM ProductoSaliente WHERE idProdSaliente = ?', (id,))
    resultado = cursor.fetchone()
    
    if not resultado:
        return "Error: Producto saliente no encontrado", 404

    id_producto, cantidad_total = resultado

    # Obtener la cantidad disponible del producto
    cursor.execute('SELECT cantidadDisponible FROM Producto WHERE idProducto = ?', (id_producto,))
    cantidad_disponible = cursor.fetchone()[0]

    # Actualizar la cantidad disponible sumando la cantidad eliminada
    nueva_cantidad_disponible = cantidad_disponible + cantidad_total

    # Eliminar el producto saliente
    cursor.execute('DELETE FROM ProductoSaliente WHERE idProdSaliente = ?', (id,))

    # Actualizar la cantidad disponible del producto
    cursor.execute('UPDATE Producto SET cantidadDisponible = ? WHERE idProducto = ?', (nueva_cantidad_disponible, id_producto))

    conn.commit()
    conn.close()

    return redirect(url_for('productoSaliente.productosSalientes'))

# 
@producto_saliente_bp.route('/eliminarProductosSalientes', methods=['POST'])
def eliminarProductosSalientes():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Eliminar todos los registros de ProductoSaliente primero
        cursor.execute('DELETE FROM ProductoSaliente')
        
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar los productos: {e}")
        return "Error al eliminar los productos", 500
    finally:
        conn.close()

    return redirect(url_for('productoSaliente.productosSalientes'))
