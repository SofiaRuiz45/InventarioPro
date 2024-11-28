from flask import Flask, request, render_template, redirect, url_for, current_app, send_file, Blueprint
import pandas as pd
import pyodbc
from dotenv import load_dotenv
from databases.db_config import get_connection
# from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
 
load_dotenv()

proveedor_bp = Blueprint('proveedores', __name__)
# vistas
@proveedor_bp.route('/registrarProveedor')
def registrar_proveedor():
    return render_template('./proveedores/registrarProveedor.html')

@proveedor_bp.route('/editarProveedor')
def editar_proveedor():
    return render_template('./proveedores/editarProveedor.html')

# acciones
@proveedor_bp.route('/registrarProveedor', methods=['GET', 'POST'])
def registrarProveedor():
    if request.method == 'POST':
        # Obtener los valores del formulario
        nombreProv = request.form.get('nombreProveedor')
        telefonoProv = request.form.get('telefonoProveedor')
        direccionProv = request.form.get('direccionProveedor')
           
        # Verificar que los valores no estén vacíos
        if not nombreProv or not telefonoProv or not direccionProv:
            return "Faltan datos", 400
  
        # Conexión y ejecución de la inserción en SQL Server
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Proveedor (nombreProveedor, telefonoProveedor, direccionProveedor)
            VALUES (?, ?, ?)
        ''', (nombreProv, telefonoProv, direccionProv))

        conn.commit()
        conn.close()
        return redirect(url_for('proveedores.prov'))

    # Si el método es GET, mostrar el formulario de registro
    return render_template('./proveedores/registrarProveedor.html')


@proveedor_bp.route('/', methods=['GET'])
def prov():
    conn = get_connection()

    query = (
        'SELECT idProveedor, nombreProveedor, telefonoProveedor, direccionProveedor FROM Proveedor')
    proveedores_df = pd.read_sql(query, conn)
    conn.close() 

    proveedores = proveedores_df.to_dict(orient='records')

    return render_template('./proveedores/proveedores.html', proveedores=proveedores) 
#


@proveedor_bp.route('/editarProveedor/<int:id>', methods=['GET', 'POST'])
def editarProveedor(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre_proveedor = request.form.get('nombreProveedor')
        telefono_proveedor = request.form.get('telefonoProveedor')
        direccion_proveedor = request.form.get('direccionProveedor')

        # Actualiza el producto en la base de datos
        cursor.execute('''
            UPDATE Proveedor 
            SET nombreProveedor = ?, telefonoProveedor = ?, direccionProveedor = ?
            WHERE idProveedor = ?
        ''', (nombre_proveedor, telefono_proveedor, direccion_proveedor, id))

        conn.commit()
        conn.close()
        return redirect(url_for('proveedores.prov'))

    cursor.execute(
        'SELECT idProveedor, nombreProveedor, telefonoProveedor,direccionProveedor FROM Proveedor WHERE idProveedor = ?', (id,))
    proveedor = cursor.fetchone()
    conn.close()

    # Convierte el resultado en un diccionario si existe
    if proveedor:
        proveedor = dict(zip([column[0]
                              for column in cursor.description], proveedor))

    return render_template('./proveedores/editarProveedor.html', proveedor=proveedor) 


@proveedor_bp.route('/eliminarProveedor/<int:id>', methods=['POST'])
def eliminarProveedor(id):
    conn = get_connection()
    cursor = conn.cursor() 
    cursor.execute('DELETE FROM Proveedor WHERE idProveedor = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('proveedores.prov'))


#
if __name__ == '__main__':
    app.run(debug=True)
