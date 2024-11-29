from flask import Flask, request, render_template, redirect, url_for, current_app, send_file, Blueprint
import pandas as pd
from dotenv import load_dotenv
from databases.db_config import get_connection
from werkzeug.utils import secure_filename
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

@proveedor_bp.route('/importarProveedores')
def importar_proveedores():
    return render_template('./proveedores/importarProveedor.html')

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
# ver tema de alguna alerta cuando estan relacionados con un

    cursor.execute('DELETE FROM Proveedor WHERE idProveedor = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('proveedores.prov'))

@proveedor_bp.route('/importarProveedores', methods=['POST'])
def importarProveedores():
    if 'file' not in request.files:
        return 'No se ingreso ningun archivo', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'El archivo no tiene nombre', 400

    # Obtener la ruta de uploads desde la configuración de Flask
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # Procesar archivo con pandas
    if file.filename.endswith('.csv'):
        proveedores_df = pd.read_csv(file_path)
    elif file.filename.endswith('.xlsx'):
        proveedores_df = pd.read_excel(file_path)
    else:
        return 'Formato de archivo no soportado', 400
    
    # Conectar a la base de datos y guardar los datos
    conn = get_connection()
    cursor = conn.cursor()
    for _, row in proveedores_df.iterrows():
        cursor.execute('''
            INSERT INTO Proveedor (nombreProveedor, telefonoProveedor, direccionProveedor)
            VALUES (?, ?, ?)
        ''', (row['nombreProveedor'], row['telefonoProveedor'], row['direccionProveedor']))
    conn.commit()
    conn.close()

    return redirect(url_for('proveedores.prov'))

@proveedor_bp.route('/exportarProveedores', methods=['GET'])
def exportarProveedores():
    formato = request.args.get('formato', 'csv') 

    conn = get_connection()
    query = 'SELECT idProveedor, nombreProveedor, telefonoProveedor, direccionProveedor FROM Proveedor'
    proveedores_df = pd.read_sql(query, conn)
    conn.close()

    # Generar el archivo exportado
    if formato == 'csv':
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'proveedores_exportados.csv')
        proveedores_df.to_csv(file_path, index=False)
    elif formato == 'excel':
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'proveedores_exportados.xlsx')
        proveedores_df.to_excel(file_path, index=False)
    else:
        return 'Formato no soportado', 400

    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        return 'Error al generar el archivo', 500

    # Enviar el archivo al cliente
    return send_file(file_path, as_attachment=True)

@proveedor_bp.route('/eliminarTodosProveedores', methods=['POST'])
def eliminarTodosProveedores():
    conn = get_connection()
    cursor = conn.cursor()

    try:

         # se debe de realizar un delete casacade que se debe de hacer en sql server 
        cursor.execute('DELETE FROM ProductoIngresado WHERE idProveedor IS NOT NULL')
        print(cursor.fetchall())

        # Eliminar todos los registros de Producto despuésf
        cursor.execute('DELETE FROM Proveedor')
        print(cursor.fetchall())
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar los prov: {e}")
        return "Error al eliminar los prov", 500
    finally:
        conn.close()

    return redirect(url_for('proveedores.prov'))

#
# if __name__ == '__main__':
#     app.run(debug=True)
