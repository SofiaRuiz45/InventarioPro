import os
from flask import Flask, render_template
from databases.db_init import create_database, create_tables
import pandas as pd
# from index import index_bp
from databases.db_config import get_connection
import pyodbc
from clases.producto import productos_bp 
from clases.proveedor import proveedor_bp
from clases.productoSaliente import producto_saliente_bp
from clases.productoIngresado import productoIngresado_bp

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# app.register_blueprint(index_bp)
app.register_blueprint(productos_bp, url_prefix='/productos')
app.register_blueprint(producto_saliente_bp, url_prefix='/productoSaliente')
# proveedor
app.register_blueprint(proveedor_bp, url_prefix='/proveedores')
app.register_blueprint(productoIngresado_bp, url_prefix='/productoIngresado') 



if __name__ == '__main__':
    create_database()  # Crear la base de datos si no existe
    create_tables()    # Crear las tablas en la base de datos
    app.run(debug=True)
