import pyodbc
from datetime import date, timedelta
server = 'Javier-Asus\\SQLEXPRESS'
database = 'FinanzasPersonales'
cnxn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
)

start_date = date(2024, 1, 1)  # Comienza en el año 2024
end_date = date(2028, 12, 31)  # Termina en el año 2028
delta = timedelta(days=1)
current_date = start_date

# --- Lógica principal del script ---
print("Iniciando la inserción de fechas en la tabla DimFecha...")

try:
    cnxn = pyodbc.connect(cnxn_str)
    cursor = cnxn.cursor()

    # Prepara el comando INSERT una sola vez para mejorar el rendimiento
    sql_insert_date = """
        INSERT INTO DimFecha (
            FechaID, Fecha, Dia, Mes, Anio, NombreMes, Trimestre, DiaSemana
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    # Diccionario para convertir el número del mes a su nombre en español
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    # Recorre cada día en el rango de fechas
    while current_date <= end_date:
        # Genera un ID numérico único (ej: 20250915)
        fecha_id = int(current_date.strftime('%Y%m%d'))

        # Prepara los datos para la inserción
        data = (
            fecha_id,
            current_date,
            current_date.day,
            current_date.month,
            current_date.year,
            meses[current_date.month],
            (current_date.month - 1) // 3 + 1, # Cálculo del trimestre
            current_date.strftime('%A') # Nombre del día de la semana
        )

        # Inserta los datos en la tabla
        cursor.execute(sql_insert_date, data)

        current_date += delta

    cnxn.commit()  # Confirma todas las inserciones
    print("¡La tabla DimFecha ha sido poblada con éxito!")

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"Error al conectar o insertar datos. Código de estado SQL: {sqlstate}")
    print(f"Detalles del error: {ex}")

finally:
    if 'cnxn' in locals() and cnxn:
        cnxn.close()
        print("Conexión a la base de datos cerrada.")
