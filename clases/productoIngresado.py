from flask import Flask, request, render_template, redirect, url_for, send_file, Blueprint
import pandas as pd
import pyodbc
from dotenv import load_dotenv
from databases.db_config import get_connection
# from werkzeug.utils import secure_filename
import os
app = Flask(__name__)

load_dotenv()

productoIngresado_bp = Blueprint('productoIngresado', __name__)

# vistas 
@productoIngresado_bp.route('/ingresarProducto')
def ingresar_producto():
    return render_template('./ProductosIngresados/ingresarProductos.html')

# @productoIngresado_bp.route('/')

@productoIngresado_bp.route('/ingresarProducto', methods=['GET', 'POST'])
def ingresarProducto():
    if request.method == 'POST':
        id_producto = int(request.form.get('idProducto'))
        id_proveedor = int(request.form.get('idProveedor'))
        cantidad_ingresada = int(request.form.get('cantidad'))
        precio_producto = float(request.form.get('precioUnitarioIng'))
        fecha_ingreso = request.form.get('fechaIngreso')

        if not cantidad_ingresada or not precio_producto or not id_producto or not id_proveedor or not fecha_ingreso:
            return "Faltan datos", 400

        conn = get_connection()
        cursor = conn.cursor()

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

        return redirect(url_for('productosIngresados.ingresos'))

    conn = get_connection()
    cursor = conn.cursor()

    # Obtener los proveedores
    cursor.execute('SELECT idProveedor, nombreProveedor FROM Proveedor')
    proveedores = [{'idProveedor': row[0], 'nombreProveedor': row[1]} for row in cursor.fetchall()]
    print("Proveedores obtenidos:", proveedores)  # Depuración

    # Obtener los productos
    cursor.execute('SELECT idProducto, nombreProducto FROM Producto')
    productos = [{'idProducto': row[0], 'nombreProducto': row[1]} for row in cursor.fetchall()]
    print("Productos obtenidos:", productos)  # Depuración

    print(proveedores)  # Para depuración
    print(productos)    # Para depuración

    conn.close()

    return render_template('./ProductosIngresados/ingresarProductos.html', proveedor=proveedores, productos=productos)

  
@productoIngresado_bp.route('/', methods=['GET']) 
def ingresos():
    # Conexión a la base de datos
    conn = get_connection()

    # Consulta para obtener los productos ingresados
    query = '''
        SELECT pi.idProducto, p.nombreProducto, pi.cantidad, pi.precioUnitarioIng, pi.fechaIngreso, pr.nombreProveedor
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

@productoIngresado_bp.route('/productos/graficoIngresos', methods=['GET'])
def grafico_ingresos():
    conn = get_connection()

    # Se seleccionan los datos de productoIngresado
    query = '''
    SELECT pi.fechaIngreso, SUM(pi.cantidad) AS totalIngresos
    FROM ProductoIngresado pi
    GROUP BY pi.fechaIngreso
    ORDER BY pi.fechaIngreso
'''
    data = pd.read_sql(query, conn)
    conn.close()

    # Convertir datos a listas para el gráfico
    fechas = data['fechaIngreso'].tolist()
    ingresos = data['totalIngresos'].tolist()

    return render_template('./Graficos/graficProdIngresos.html', fechas=fechas, ingresos=ingresos)

# @app.route('/ingreso/editar/<int: id>', methods=['GET', 'POST'])
# def editarIngreso(id):
#     conn = get_connection()
#     cursor = conn.cursor()

if __name__ == '__main__':
    app.run(debug=True)
