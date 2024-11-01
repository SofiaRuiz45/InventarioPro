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

if __name__ == '__main__':
    app.run(debug=True)
