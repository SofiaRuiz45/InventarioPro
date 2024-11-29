from flask import Blueprint, render_template
from databases.db_config import get_connection
import pandas as pd

# Crear un Blueprint para las rutas relacionadas con el índice
index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    conn = get_connection()

    # Consulta para obtener los productos
    query = 'SELECT idProducto, nombreProducto, cantidadDisponible, precioUnitario, precioVenta, categoriaProducto FROM Producto'
    productos_df = pd.read_sql(query, conn)

    # graficos
    query_grafico = '''
    SELECT pi.fechaIngreso, SUM(pi.cantidad) AS totalIngresos
    FROM ProductoIngresado pi
    GROUP BY pi.fechaIngreso
    ORDER BY pi.fechaIngreso
    '''  
    # Ejecutamos la consulta para el gráfico y obtenemos los datos en un DataFrame
    data = pd.read_sql(query_grafico, conn)

    query_grafico_salida='''
    SELECT fechaSalida, SUM(cantidad) AS totalSalida
        FROM ProductoSaliente
        GROUP BY fechaSalida
        ORDER BY fechaSalida
'''
    salida = pd.read_sql(query_grafico_salida, conn)


    # Ahora podemos cerrar la conexión
    conn.close()
    
    data['fechaIngreso'] = pd.to_datetime(data['fechaIngreso'])
    salida['fechaSalida'] = pd.to_datetime(salida['fechaSalida'])
 
    fechas = data['fechaIngreso'].dt.strftime('%Y-%m-%d').tolist()
    fechas_salida = salida['fechaSalida'].dt.strftime('%Y-%m-%d').tolist()  

    ingresos_totales = data['totalIngresos'].tolist()
    salidas_totales =salida['totalSalida'].tolist()
    fechas_salida =salida['fechaSalida'].tolist()

    # Renderizar el template de index.html con los productos
    return render_template('index.html', productos=productos_df.to_dict(orient='records'), ingresos_totales=ingresos_totales, fechas=fechas, salidas_totales=salidas_totales, fechas_salida=fechas_salida )
 
 
if __name__ == '__main__':
    app.run(debug=True)