from flask import Blueprint, request, render_template, redirect, url_for, current_app, send_file
from databases.db_config import get_connection
import pandas as pd
from werkzeug.utils import secure_filename
import os

# Crear un Blueprint para las rutas de productos
productos_bp = Blueprint('productos', __name__)

#vistas
@productos_bp.route('/registrarProducto')
def registrar_producto():
    return render_template('./productos/registrarProducto.html')

@productos_bp.route('/editarProducto')
def editar_producto():
    return render_template('./productos/editarProducto.html')

@productos_bp.route('/importarProductos')
def importar_producto():
    return render_template('./productos/importarProducto.html')


# Ruta para registrar un producto
@productos_bp.route('/registrarProducto', methods=['GET', 'POST'])
def registrarProducto():
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        nombre_producto = request.form.get('nombreProducto')
        cantidad_disponible = request.form.get('cantidadDisponible')
        categoria_producto = request.form.get('categoriaProducto')
        precio_unitario = float(request.form.get('precioUnitario'))  # Convertir a float

        # Calcular precioVenta sumando un 10% al precioUnitario
        precio_venta = round(precio_unitario * 1.10, 2)

        # Conexión y ejecución de la inserción en SQL Server
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Producto (nombreProducto, cantidadDisponible, categoriaProducto, precioUnitario, precioVenta)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre_producto, cantidad_disponible, categoria_producto, precio_unitario, precio_venta))

        conn.commit()
        conn.close()

        return redirect(url_for('productos.products'))

    return render_template('./productos/registrarProducto.html')


# Ruta para mostrar productos
@productos_bp.route('/', methods=['GET'])
def products():
    conn = get_connection()

    # Consulta
    query = '''
        SELECT idProducto, nombreProducto, cantidadDisponible, categoriaProducto, precioUnitario, precioVenta
        FROM Producto
    '''
    productos_df = pd.read_sql(query, conn)
    conn.close()
    error = request.args.get('error', None)

    productos = productos_df.to_dict(orient='records')

    return render_template('./productos/productos.html', productos=productos, error=error)


# Ruta para editar un producto
@productos_bp.route('/editarProducto/<int:id>', methods=['GET', 'POST'])
def editarProducto(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Obtiene los datos del formulario
        nombre_producto = request.form.get('nombreProducto')
        cantidad_disponible = request.form.get('cantidadDisponible')
        categoria_producto = request.form.get('categoriaProducto')
        precio_unitario = float(request.form.get('precioUnitario'))  # Convertir a float

        # Recalcular precioVenta
        precio_venta = round(precio_unitario * 1.10, 2)

        # Actualiza el producto en la base de datos
        cursor.execute('''
            UPDATE Producto 
            SET nombreProducto = ?, cantidadDisponible = ?, categoriaProducto = ?, precioUnitario = ?, precioVenta = ?
            WHERE idProducto = ?
        ''', (nombre_producto, cantidad_disponible, categoria_producto, precio_unitario, precio_venta, id))

        conn.commit()
        conn.close()

        return redirect(url_for('productos.products'))

    # Obtiene los datos actuales del producto
    cursor.execute('''
        SELECT idProducto, nombreProducto, cantidadDisponible, categoriaProducto, precioUnitario, precioVenta
        FROM Producto
        WHERE idProducto = ?
    ''', (id,))
    producto = cursor.fetchone()
    conn.close()

    # Convierte el resultado en un diccionario si el producto existe
    if producto:
        producto = dict(zip([column[0] for column in cursor.description], producto))

    return render_template('./productos/editarProducto.html', producto=producto)

# Ruta para eliminar un producto
import pyodbc

@productos_bp.route('/eliminarProducto/<int:id>', methods=['POST'])
def eliminarProducto(id):
    conn = get_connection()  # Tu función para conectar a SQL Server
    cursor = conn.cursor()

    try:
        # Intenta eliminar el producto
        cursor.execute('DELETE FROM Producto WHERE idProducto = ?', (id,))
        conn.commit()
    except pyodbc.IntegrityError as e:
        # Captura el error de integridad referencial
        conn.rollback()
        print(f"Error de integridad: {e}")
        return redirect(url_for('productos.products', error="No se puede eliminar el producto porque tiene registros relacionados."))
    except Exception as e:
        # Manejo general de errores
        conn.rollback()
        print(f"Error inesperado: {e}")
        return redirect(url_for('productos.products', error="Ocurrió un error inesperado al intentar eliminar el producto."))
    finally:
        conn.close()

    # Si no hay errores, redirige normalmente
    return redirect(url_for('productos.products'))


# Ruta para exportar productos
@productos_bp.route('/exportarProductos', methods=['GET'])
def exportarProductos():
    formato = request.args.get('formato', 'csv')  # Por defecto se exportará en formato CSV

    conn = get_connection()
    query = 'SELECT idProducto, nombreProducto, cantidadDisponible, precioUnitario, precioVenta, categoriaProducto FROM Producto'
    productos_df = pd.read_sql(query, conn)
    conn.close()

    # Generar el archivo exportado
    if formato == 'csv':
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'productos_exportados.csv')
        productos_df.to_csv(file_path, index=False)
    elif formato == 'excel':
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'productos_exportados.xlsx')
        productos_df.to_excel(file_path, index=False)
    else:
        return 'Formato no soportado', 400

    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        return 'Error al generar el archivo', 500

    # Enviar el archivo al cliente
    return send_file(file_path, as_attachment=True)


# Ruta para importar productos
@productos_bp.route('/importarProductos', methods=['POST'])
def importarProductos():
    if 'file' not in request.files:
        return 'No se ha subido ningún archivo', 400

    file = request.files['file']
    if file.filename == '':
        return 'El archivo no tiene nombre', 400

    # Obtener la ruta de uploads desde la configuración de Flask
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # Procesar archivo con pandas
    if file.filename.endswith('.csv'):
        productos_df = pd.read_csv(file_path)
    elif file.filename.endswith('.xlsx'):
        productos_df = pd.read_excel(file_path)
    else:
        return 'Formato de archivo no soportado', 400

    # Conectar a la base de datos y guardar los datos
    conn = get_connection()
    cursor = conn.cursor()

    for _, row in productos_df.iterrows():
        # Validar y convertir precioUnitario y precioVenta
        try:
            precio_unitario = float(row['precioUnitario']) if pd.notnull(row['precioUnitario']) else None
            precio_venta = float(row['precioVenta']) if pd.notnull(row['precioVenta']) else None
        except ValueError:
            # Si no se puede convertir a float, asignamos None o manejamos el error
            precio_unitario = None
            precio_venta = None

        # Verificar que los precios sean valores válidos (no None o NaN)
        if precio_unitario is None or precio_venta is None:
            continue  # O manejar el error según tus necesidades

        # Asegurarse de que los demás campos sean válidos
        nombre_producto = row['nombreProducto']
        cantidad_disponible = row['cantidadDisponible']
        categoria_producto = row['categoriaProducto']

        # Asegurarse de que los valores numéricos sean válidos
        if not isinstance(cantidad_disponible, (int, float)):
            cantidad_disponible = 0  # O manejar de acuerdo a lo que quieras hacer con los valores no válidos

        # Insertar los datos en la base de datos
        cursor.execute('''
            INSERT INTO Producto (nombreProducto, cantidadDisponible, categoriaProducto, precioUnitario, precioVenta)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre_producto, cantidad_disponible, categoria_producto, precio_unitario, precio_venta))

    conn.commit()
    conn.close()

    return redirect(url_for('productos.products'))

# Eliminar todos los productos
@productos_bp.route('/eliminarTodosProductos', methods=['POST'])
def eliminarTodosProductos():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Eliminar todos los registros de ProductoSaliente primero
        cursor.execute('DELETE FROM ProductoSaliente')
        cursor.execute('DELETE FROM ProductoIngresado')
        # Eliminar todos los registros de Producto después
        cursor.execute('DELETE FROM Producto')
        
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar los productos: {e}")
        return "Error al eliminar los productos", 500
    finally:
        conn.close()

    return redirect(url_for('productos.products'))