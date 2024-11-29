from flask import Flask, request, render_template, redirect, url_for, Blueprint
import pandas as pd
import pyodbc
from dotenv import load_dotenv
from databases.db_config import get_connection
# from werkzeug.utils import secure_filename
import os
app = Flask(__name__)


load_dotenv()

productoIngresado_bp = Blueprint('productoIngresado', __name__)


@productoIngresado_bp.route('/editarIngreso')
def editar_ingreso():
    return render_template('./ProductosIngresados/editarIngreso.html')
 

@productoIngresado_bp.route('/ingresarProducto', methods=['GET', 'POST'])
def ingresarProducto():

    conn = get_connection()
    cursor = conn.cursor()

    # Si es un POST, procesar el formulario
    if request.method == 'POST':
        id_producto = int(request.form.get('idProducto'))
        id_proveedor = int(request.form.get('idProveedor'))
        cantidad_ingresada = int(request.form.get('cantidad'))
        precio_producto = float(request.form.get('precioUnitarioIng'))
        fecha_ingreso = request.form.get('fechaIngreso')

        if not cantidad_ingresada or not precio_producto or not id_producto or not id_proveedor or not fecha_ingreso:
            return "Faltan datos", 400

        # Insertar los datos en ProductoIngresado
        cursor.execute('''
            INSERT INTO ProductoIngresado (cantidad, precioUnitarioIng, idProducto, idProveedor, fechaIngreso)
            VALUES (?, ?, ?, ?, ?)
        ''', (cantidad_ingresada, precio_producto, id_producto, id_proveedor, fecha_ingreso))

        # Actualizar la cantidad disponible en Producto
        cursor.execute('''
            UPDATE Producto SET cantidadDisponible = cantidadDisponible + ? WHERE idProducto = ?
        ''', (cantidad_ingresada, id_producto))

        conn.commit()
        conn.close()

        return redirect(url_for('productoIngresado.ingresos'))

    # Si es un GET, recuperar proveedores y productos
    query_proveedores = 'SELECT idProveedor, nombreProveedor FROM Proveedor'
    query_productos = 'SELECT idProducto, nombreProducto FROM Producto'
    # Obtener proveedores
    cursor.execute(query_proveedores)
    proveedores = cursor.fetchall()
    # Obtener productos
    cursor.execute(query_productos)
    productos = cursor.fetchall()
    conn.close()
    # Convertir los datos obtenidos a listas de diccionarios
    proveedores = [{"idProveedor": proveedor[0],
        "nombreProveedor": proveedor[1]} for proveedor in proveedores]
    productos = [{"idProducto": producto[0], "nombreProducto": producto[1]}
        for producto in productos]

    # Renderizar el formulario con proveedores y productos
    return render_template('./ProductosIngresados/ingresarProductos.html', proveedores=proveedores, productos=productos)


@productoIngresado_bp.route('/', methods=['GET'])
def ingresos():
    # Conexión a la base de datos
    conn = get_connection()

    # Consulta para obtener los productos ingresados
    query = '''
        SELECT pi.idProducto, p.nombreProducto, pi.cantidad, pi.precioUnitarioIng, pi.fechaIngreso, pr.nombreProveedor, pi.idProdIngresado
        FROM ProductoIngresado pi
        JOIN Producto p ON pi.idProducto = p.idProducto
        JOIN Proveedor pr ON pi.idProveedor = pr.idProveedor
    '''
    # Ejecutar la consulta y obtener los resultados
    ingresos_df = pd.read_sql(query, conn)
    ingresos = ingresos_df.to_dict(orient='records')

    conn.close()

    # Pasar los datos al template
    return render_template('./ProductosIngresados/ingresos.html', ingresos=ingresos)


# @productoIngresado_bp.route('/productos/graficoIngresos', methods=['GET'])
# def grafico_ingresos():
#     conn = get_connection()

#     # Se seleccionan los datos de productoIngresado
#     query = '''
#     SELECT pi.fechaIngreso, SUM(pi.cantidad) AS totalIngresos
#     FROM ProductoIngresado pi
#     GROUP BY pi.fechaIngreso
#     ORDER BY pi.fechaIngreso
# '''
#     data = pd.read_sql(query, conn)
#     conn.close()

#     # Convertir datos a listas para el gráfico
#     fechas = data['fechaIngreso'].tolist()
#     ingresos = data['totalIngresos'].tolist()

#     return render_template('./Graficos/graficProdIngresos.html', fechas=fechas, ingresos=ingresos)


@productoIngresado_bp.route('/editarIngreso/<int:id>', methods=['GET', 'POST'])
def editarIngreso(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        id_producto = int(request.form.get('idProducto'))
        id_proveedor = int(request.form.get('idProveedor'))
        cantidad_ingresada = int(request.form.get('cantidad'))
        fecha_ingreso = request.form.get('fechaIngreso')
        precio_unitario = float(request.form.get('precioUnitarioIng'))

        # Actualizar el producto ingresado
        cursor.execute('''
            UPDATE ProductoIngresado
            SET idProveedor = ?, idProducto = ?, cantidad = ?, fechaIngreso = ?, precioUnitarioIng = ?
            WHERE idProdIngresado = ?
        ''', (id_proveedor, id_producto, cantidad_ingresada, fecha_ingreso, precio_unitario, id))

        conn.commit()
        conn.close()
        return redirect(url_for('productoIngresado.ingresos'))
    
    # Obtener el producto ingresado específico
    cursor.execute('''
        SELECT idProdIngresado, idProveedor, idProducto, fechaIngreso, cantidad, precioUnitarioIng
        FROM ProductoIngresado
        WHERE idProdIngresado = ?
    ''', (id,))
    productoIngresado = cursor.fetchone()

    # Convertir el resultado a un diccionario si existe
    if productoIngresado:
        productoIngresado = dict(zip([column[0] for column in cursor.description], productoIngresado))

    # Obtener todos los productos disponibles para el select
    cursor.execute('SELECT idProducto, nombreProducto FROM Producto')
    productos = cursor.fetchall()

    # Obtener todos los proveedores disponibles para el select
    cursor.execute('SELECT idProveedor, nombreProveedor FROM Proveedor')
    proveedores = cursor.fetchall()

    # Cerrar la conexión después de obtener todos los datos
    conn.close()

    # Renderizar la plantilla con los datos obtenidos
    return render_template(
        './ProductosIngresados/editarIngreso.html',
        productoIngresado=productoIngresado,
        productos=productos,
        proveedores=proveedores
    )

@productoIngresado_bp.route('/eliminarIngreso/<int:id>', methods=['POST'])
def eliminarIngreso(id):
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener el producto saliente para obtener la cantidad y el id del producto
    cursor.execute('SELECT idProducto, cantidad FROM ProductoIngresado WHERE idProdIngresado = ?', (id,))

    resultado = cursor.fetchone()

    id_producto, cantidad_total = resultado

    #cant disponible del producto
    cursor.execute('SELECT cantidadDisponible FROM Producto WHERE idProducto = ?', (id_producto,))
    cantidad_disponible = cursor.fetchone()[0]

    # Actualizar la cantidad disponible sumando la cantidad eliminada
    nueva_cantidad_disponible = cantidad_disponible - cantidad_total

    # Eliminar el producto saliente
    cursor.execute('DELETE FROM ProductoIngresado WHERE idProdingresado = ?', (id,))

    # Actualizar la cantidad disponible del producto
    cursor.execute('UPDATE Producto SET cantidadDisponible = ? WHERE idProducto = ?', (nueva_cantidad_disponible, id_producto))

    conn.commit()
    conn.close()

    return redirect(url_for('productoIngresado.ingresos'))

if __name__ == '__main__':
    app.run(debug=True)
