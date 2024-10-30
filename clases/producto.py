from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
import pandas as pd

app = Flask(__name__)

# Conexión a la base de datos MySQL
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',       # Cambia esto si MySQL está en otro servidor o contenedor
        user='root',      # Reemplaza con tu usuario MySQL
        password='',# Reemplaza con tu contraseña MySQL
        database='inventario'    # Nombre de tu base de datos
    )

# Ruta para registrar un producto
@app.route('/registrarProducto', methods=['GET', 'POST'])
def registrarProducto():
    if request.method == 'POST':
        # Obtenemos los datos del formulario
        nombre_producto = request.form.get('nombreProducto')
        cantidad_disponible = request.form.get('cantidadDisponible')
        categoria_producto = request.form.get('categoriaProducto')

        # Conexión y ejecución de la inserción en MySQL
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Producto (nombreProducto, cantidadDisponible, categoriaProducto)
            VALUES (%s, %s, %s)
        ''', (nombre_producto, cantidad_disponible, categoria_producto))

        conn.commit()
        conn.close()
        conn.close()

        return redirect(url_for('products')) 

    return render_template('./productos/registrarProducto.html')

# Ruta para mostrar productos
@app.route('/productos', methods=['GET'])
def products():
    # Conexión a MySQL
    conn = get_db_connection()

    # Consulta de los productos
    query = 'SELECT idProducto, nombreProducto, cantidadDisponible, categoriaProducto FROM Producto'
    productos_df = pd.read_sql(query, conn)  # Utilizamos pandas para obtener los datos como DataFrame

    conn.close()

    # Convertimos el DataFrame a lista de diccionarios para pasar a la plantilla
    productos = productos_df.to_dict(orient='records')

    return render_template('./productos/productos.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)
