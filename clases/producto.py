from flask import Flask, request, render_template, redirect, url_for
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

# Conexión a la BD SQL Server
def get_db_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={os.getenv("DB_SERVER")};'
        f'DATABASE={os.getenv("DB_NAME")};'
        f'UID={os.getenv("DB_USER")};'
        f'PWD={os.getenv("DB_PASSWORD")}'
    )


# Ruta para registrar un producto
@app.route('/registrarProducto', methods=['GET', 'POST'])
def registrarProducto():
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        nombre_producto = request.form.get('nombreProducto')
        cantidad_disponible = request.form.get('cantidadDisponible')
        categoria_producto = request.form.get('categoriaProducto')

        # Conexión y ejecución de la inserción en SQL Server
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Producto (nombreProducto, cantidadDisponible, categoriaProducto)
            VALUES (?, ?, ?)
        ''', (nombre_producto, cantidad_disponible, categoria_producto))

        conn.commit()
        conn.close()

        return redirect(url_for('products')) 

    return render_template('./productos/registrarProducto.html')

# Ruta para mostrar productos
@app.route('/productos', methods=['GET'])
def products():
    conn = get_db_connection()

    # Consulta
    query = 'SELECT idProducto, nombreProducto, cantidadDisponible, categoriaProducto FROM Producto'
    productos_df = pd.read_sql(query, conn)  

    conn.close()

    productos = productos_df.to_dict(orient='records')

    return render_template('./productos/productos.html', productos=productos)


@app.route('/editarProducto/<int:id>', methods=['GET', 'POST'])
def editarProducto(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Obtiene los datos del formulario
        nombre_producto = request.form.get('nombreProducto')
        cantidad_disponible = request.form.get('cantidadDisponible')
        categoria_producto = request.form.get('categoriaProducto')

        # Actualiza el producto en la base de datos
        cursor.execute('''
            UPDATE Producto 
            SET nombreProducto = ?, cantidadDisponible = ?, categoriaProducto = ?
            WHERE idProducto = ?
        ''', (nombre_producto, cantidad_disponible, categoria_producto, id))

        conn.commit()
        conn.close()
        return redirect(url_for('products'))

    # Obtiene los datos actuales del producto para la edición
    cursor.execute('SELECT idProducto, nombreProducto, cantidadDisponible, categoriaProducto FROM Producto WHERE idProducto = ?', (id,))
    producto = cursor.fetchone()
    conn.close()

    # Convierte el resultado en un diccionario si el producto existe
    if producto:
        producto = dict(zip([column[0] for column in cursor.description], producto))

    return render_template('./productos/editarProducto.html', producto=producto)

# Ruta para eliminar un producto
@app.route('/eliminarProducto/<int:id>', methods=['POST'])
def eliminarProducto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Producto WHERE idProducto = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products'))

if __name__ == '__main__':
    app.run(debug=True)
