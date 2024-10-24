from flask import Flask, request, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',     
        user='root',   
        password='',
        database='inventario' 
    )

@app.route('/registrarProveedor', methods=['GET', 'POST'])
def registrarProveedor():
    if request.method == 'POST':
        # Obtener los valores del formulario
        nombreProv = request.form.get('nombreProveedor')
        telefonoProv = request.form.get('telefonoProveedor')
        direccionProv = request.form.get('direccionProveedor')

        # Verificar que los valores no estén vacíos
        if not nombreProv or not telefonoProv or not direccionProv:
            return "Faltan datos", 400

        # Conectar a la base de datos y almacenar los datos
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Proveedor (nombreProveedor, telefonoProveedor, direccionProveedor)
            VALUES (%s, %s, %s)
        ''', (nombreProv, telefonoProv, direccionProv))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('prov'))

    # Si el método es GET, mostrar el formulario de registro
    return render_template('./proveedores/registrarProveedor.html')

@app.route('/proveedores', methods=['GET'])
def prov():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT idProveedor, nombreProveedor, telefonoProveedor, direccionProveedor FROM Proveedor')
    provedores = cursor.fetchall()
    conn.close()

    return render_template('./proveedores/proveedores.html', provedores=provedores)

if __name__ == '__main__':
    app.run(debug=True)
