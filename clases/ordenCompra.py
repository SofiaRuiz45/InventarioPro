from flask import Flask, request, render_template, redirect, url_for
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import os
app = Flask(__name__)
load_dotenv()


def get_db_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={os.getenv("DB_SERVER")};'
        f'DATABASE={os.getenv("DB_NAME")};'
        f'UID={os.getenv("DB_USER")};'
        f'PWD={os.getenv("DB_PASSWORD")}'
    )


@app.route('/registrarOrdenCompra', methods=['GET', 'POST'])
def registrarOrdenCompra():
    if request.method == 'POST':
        fechaOrden = request.form.get('fechaOrden')
        cantidadTotal = request.form.get('cantidadTotal')
        precioTotal = request.form.get('precioTotal')
        estado = request.form.get('estado')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO OrdenCompra (fechaOrden, cantidadTotal, precioTotal, estado)
            VALUES (?, ?, ?, ?)
        ''', (fechaOrden, cantidadTotal, precioTotal, estado))

        conn.commit()
        conn.close()

        return redirect(url_for('orders'))

    return render_template('./OrdenCompra/registrarOrdenCompra.html')


@app.route('/ordenes', methods=['GET'])
def orders():
    conn = get_db_connection()

    query = 'SELECT idOrdenCompra, fechaOrden, cantidadTotal, precioTotal, estado FROM OrdenCompra'
    orders_df = pd.read_sql(query, conn)

    conn.close()

    ordenes = orders_df.to_dict(orient='records')

    return render_template('./OrdenCompra/ordenCompra.html', ordenes=ordenes)


@app.route('/editarOrdenCompra/<int:id>', methods=['GET', 'POST'])
def editarOrdenCompra(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # datos del formulario
        fechaOrden = request.form.get('fechaOrden')
        cantidadTotal = request.form.get('cantidadTotal')
        precioTotal = request.form.get('precioTotal')
        estado = request.form.get('estado')

        cursor.execute('''
            UPDATE OrdenCompra 
            SET fechaOrden = ?, cantidadTotal = ?, precioTotal = ?, categoriaProducto = ?
            WHERE idOrdencompra = ?
        ''', (fechaOrden, cantidadTotal, precioTotal, estado, id))

        conn.commit()
        conn.close()
        return redirect(url_for('products'))

    cursor.execute(
        'SELECT idOrdenCompra, fechaOrden, cantidadTotal, precioTotal, estado FROM OrdenCompra WHERE idOrdenCompra = ?', (id,))
    ordenes = cursor.fetchone()
    conn.close()

    if ordenes:
        ordenes = dict(zip([column[0]
                        for column in cursor.description], ordenes))

    return render_template('./OrdenCompra/editarOrdenCompra.html', ordenes=ordenes)

@app.route('/eliminarOrdenCompra/<int:id>', methods=['POST'])
def eliminarOrdenCompra(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM OrdenCompra WHERE idOrdenCompra = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('orders'))


if __name__ == '__main__':
    app.run(debug=True)
