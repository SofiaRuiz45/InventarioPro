from flask import Blueprint, render_template
from databases.db_config import get_connection
import pandas as pd

# Crear un Blueprint para las rutas relacionadas con el índice
index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    conn = get_connection()

    # Consulta
    query = 'SELECT idProducto, nombreProducto, cantidadDisponible, categoriaProducto FROM Producto'
    productos_df = pd.read_sql(query, conn)
    conn.close()

    productos = productos_df.to_dict(orient='records')

    # Renderizar el template de index.html con los productos
    return render_template('index.html', productos=productos)
