from flask import Flask, render_template
import pandas as pd
import mysql.connector
from clases.producto import registrarProducto, products

app = Flask(__name__)

# Datos del inventario actual
inventario_data = {
    'producto_id': [1, 2, 3, 4],
    'producto': ['Producto A', 'Producto B', 'Producto C', 'Producto D'],
    'categoria': ['Electrónica', 'Hogar', 'Electrónica', 'Juguetes'],
    'stock': [50, 20, 0, 15],
    'precio': [500, 300, 150, 200]
}

# Datos de órdenes de compra
ordenes_data = {
    'orden_id': [101, 102, 103, 104],
    'producto_id': [1, 2, 3, 4],
    'cantidad': [5, 10, 2, 1],
    'estado': ['Pendiente', 'Completado', 'Pendiente', 'Pendiente']
}

# Convertimos los datos en DataFrames de pandas
df_inventario = pd.DataFrame(inventario_data)
df_ordenes = pd.DataFrame(ordenes_data)

# Limpieza de datos: eliminar productos con stock negativo
df_inventario = df_inventario[df_inventario['stock'] >= 0]

# Análisis de productos que necesitan reabastecimiento (stock <= 5)
productos_bajos_stock = df_inventario[df_inventario['stock'] <= 5]

# Unimos las órdenes con el inventario para ver el detalle de productos pendientes
ordenes_pendientes = df_ordenes[df_ordenes['estado'] == 'Pendiente']
ordenes_con_inventario = pd.merge(ordenes_pendientes, df_inventario, on='producto_id')

# Ruta principal
@app.route('/')
def index():
    # Convertir los DataFrames en formato HTML para mostrarlos en la página
    inventario_html = df_inventario.to_html(classes='table table-striped', index=False)
    ordenes_html = df_ordenes.to_html(classes='table table-striped', index=False)
    bajos_stock_html = productos_bajos_stock.to_html(classes='table table-striped', index=False)
    pendientes_html = ordenes_con_inventario.to_html(classes='table table-striped', index=False)
    
    # Renderizar el template y pasar los datos
    return render_template('index.html', 
                           inventario=inventario_html, 
                           ordenes=ordenes_html, 
                           bajos_stock=bajos_stock_html, 
                           pendientes=pendientes_html)


app.add_url_rule('/productos', view_func=products, methods=['GET'])
app.add_url_rule('/registrarProducto', view_func=registrarProducto, methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run(debug=True)
