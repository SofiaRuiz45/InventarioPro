from flask import Blueprint, render_template, jsonify
from databases.db_config import get_connection
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64

# Crear un Blueprint para las rutas relacionadas con el índice
index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    conn = get_connection()

    # Consulta para obtener los productos
    query = 'SELECT idProducto, nombreProducto, cantidadDisponible, precioUnitario, precioVenta, categoriaProducto FROM Producto'
    productos_df = pd.read_sql(query, conn)

    # Consultas para los gráficos
    query_grafico = '''
    SELECT pi.fechaIngreso, SUM(pi.cantidad) AS totalIngresos
    FROM ProductoIngresado pi
    GROUP BY pi.fechaIngreso
    ORDER BY pi.fechaIngreso
    '''  
    data = pd.read_sql(query_grafico, conn)

    query_grafico_salida=''' 
    SELECT fechaSalida, SUM(cantidad) AS totalSalida
    FROM ProductoSaliente
    GROUP BY fechaSalida
    ORDER BY fechaSalida
    '''
    salida = pd.read_sql(query_grafico_salida, conn)

    conn.close()

    # Convertir fechas
    data['fechaIngreso'] = pd.to_datetime(data['fechaIngreso'])
    salida['fechaSalida'] = pd.to_datetime(salida['fechaSalida'])

    fechas = data['fechaIngreso'].dt.strftime('%b %d').tolist()
    fechas_salida = salida['fechaSalida'].dt.strftime('%b %d').tolist()  
    ingresos_totales = data['totalIngresos'].tolist()
    salidas_totales = salida['totalSalida'].tolist()

    # Crear los gráficos con Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))

    # Graficar ingresos
    ax.plot(data['fechaIngreso'], data['totalIngresos'], label='Ingresos', color='green', marker='o')
    # Graficar salidas
    ax.plot(salida['fechaSalida'], salida['totalSalida'], label='Salidas', color='red', marker='o')

    ax.set_xlabel('Fecha')
    ax.set_ylabel('Cantidad')
    ax.set_title('Movimientos de Productos: Ingresos y Salidas')

    # Rotar las fechas para mejorar la legibilidad
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45)

    # Agregar leyenda
    ax.legend()

    # Convertir el gráfico a imagen en base64 
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Renderizar la plantilla pasando la imagen como dato
    return render_template('index.html', 
                           productos=productos_df.to_dict(orient='records'),
                           img_base64=img_base64,
                           ingresos_totales=ingresos_totales, 
                           fechas=fechas, 
                           salidas_totales=salidas_totales, 
                           fechas_salida=fechas_salida)
