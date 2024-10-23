from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

# Ruta 
@app.route('/registrarProducto', methods=['GET', 'POST'])
def registrarProducto():
    if request.method == 'POST':
        # llamamos los datos del formulario
        nombre_producto = request.form['nombreProducto']
        cantidad_disponible = request.form['cantidadDisponible']
        categoria_producto = request.form['categoriaProducto']

        conn = sqlite3.connect('inventario.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Producto (nombreProducto, cantidadDisponible, categoriaProducto)
            VALUES (?, ?, ?)
        ''', (nombre_producto, cantidad_disponible, categoria_producto))

        conn.commit()
        conn.close()

        return redirect(url_for('products')) 

    return render_template('./productos/registrarProducto.html')

@app.route('/productos', methods=['GET'])
def products():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()

    cursor.execute('SELECT idProducto, nombreProducto, cantidadDisponible, categoriaProducto FROM Producto')
    productos = cursor.fetchall()  # Llama a todos los registros
    conn.close()

    return render_template('./productos/productos.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)
