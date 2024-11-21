from flask import Flask, render_template
from databases.db_init import create_database, create_tables
import pandas as pd
from databases.db_config import get_connection
import pyodbc
from clases.producto import registrarProducto, products, editarProducto, eliminarProducto
from clases.ordenCompra import registrarOrdenCompra, orders, editarOrdenCompra, eliminarOrdenCompra
# from clases.proveedor import registrarProveedor, prov

app = Flask(__name__)

# # Datos del inventario actual
# inventario_data = {
#     'producto_id': [1, 2, 3, 4],
#     'producto': ['Producto A', 'Producto B', 'Producto C', 'Producto D'],
#     'categoria': ['Electrónica', 'Hogar', 'Electrónica', 'Juguetes'],
#     'stock': [50, 20, 0, 15],
#     'precio': [500, 300, 150, 200]
# }

# # Datos de órdenes de compra
# ordenes_data = {
#     'orden_id': [101, 102, 103, 104],
#     'producto_id': [1, 2, 3, 4],
#     'cantidad': [5, 10, 2, 1],
#     'estado': ['Pendiente', 'Completado', 'Pendiente', 'Pendiente']
# }

# # Convertimos los datos en DataFrames de pandas
# df_inventario = pd.DataFrame(inventario_data)
# df_ordenes = pd.DataFrame(ordenes_data)

# # Limpieza de datos: eliminar productos con stock negativo
# df_inventario = df_inventario[df_inventario['stock'] >= 0]

# # Análisis de productos que necesitan reabastecimiento (stock <= 5)
# productos_bajos_stock = df_inventario[df_inventario['stock'] <= 5]

# # Unimos las órdenes con el inventario para ver el detalle de productos pendientes
# ordenes_pendientes = df_ordenes[df_ordenes['estado'] == 'Pendiente']
# ordenes_con_inventario = pd.merge(ordenes_pendientes, df_inventario, on='producto_id')

# Ruta principal
@app.route('/')
def index():
    # # Convertir los DataFrames en formato HTML para mostrarlos en la página
    # inventario_html = df_inventario.to_html(classes='table table-striped', index=False)
    # ordenes_html = df_ordenes.to_html(classes='table table-striped', index=False)
    # bajos_stock_html = productos_bajos_stock.to_html(classes='table table-striped', index=False)
    # pendientes_html = ordenes_con_inventario.to_html(classes='table table-striped', index=False)
    
    # Renderizar el template y pasar los datos
    return render_template('index.html')

# app.add_url_rule('/provedores', view_func=prov, methods=['GET'])
# app.add_url_rule('/registrarProveedor', view_func=registrarProveedor, methods=['GET', 'POST'])

app.add_url_rule('/productos', view_func=products, methods=['GET'])
app.add_url_rule('/registrarProducto', view_func=registrarProducto, methods=['GET', 'POST'])
app.add_url_rule('/ordenes', view_func=orders, methods=['GET'])
app.add_url_rule('/registrarOrdenCompra', view_func=registrarOrdenCompra, methods=['GET', 'POST'])
app.add_url_rule('/editarProducto/<int:id>', view_func=editarProducto, methods=['GET', 'POST'])
app.add_url_rule('/eliminarProducto/<int:id>', view_func=eliminarProducto, methods=['POST'])
app.add_url_rule('/editarOrdenCompra/<int:id>', view_func=editarOrdenCompra, methods=['GET', 'POST'])
app.add_url_rule('/eliminarOrdenCompra/<int:id>', view_func=eliminarOrdenCompra, methods=['POST'])


if __name__ == '__main__':
    create_database()  # Crear la base de datos si no existe
    create_tables()    # Crear las tablas en la base de datos
    app.run(debug=True)
