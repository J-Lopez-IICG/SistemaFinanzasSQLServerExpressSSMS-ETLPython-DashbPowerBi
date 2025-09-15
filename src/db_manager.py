import pyodbc
from datetime import date
from decimal import Decimal

# --- Configuración de la conexión ---
SERVER = 'Javier-Asus\\SQLEXPRESS'
DATABASE = 'FinanzasPersonales'
CNXN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos."""
    try:
        cnxn = pyodbc.connect(CNXN_STR)
        return cnxn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Error al conectar a la base de datos. Código de estado SQL: {sqlstate}")
        print(f"Detalles del error: {ex}")
        return None

def get_dimension_values(cnxn, table, column):
    """Obtiene todos los valores únicos de una columna en una tabla de dimensión."""
    cursor = cnxn.cursor()
    cursor.execute(f"SELECT DISTINCT {column} FROM {table}")
    values = [row[0] for row in cursor.fetchall()]
    return values

def get_or_create_dimension(cnxn, table, id_column, column, value, additional_data=None):
    """
    Busca o inserta un valor en una tabla de dimensión y devuelve su ID.
    """
    cursor = cnxn.cursor()
    cursor.execute(f"SELECT {id_column} FROM {table} WHERE {column} = ?", value)
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        if additional_data:
            cols = [column] + list(additional_data.keys())
            vals = [value] + list(additional_data.values())
            placeholders = ', '.join(['?' for _ in cols])
            sql_insert = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
            cursor.execute(sql_insert, tuple(vals))
        else:
            sql_insert = f"INSERT INTO {table} ({column}) VALUES (?)"
            cursor.execute(sql_insert, value)
        
        cnxn.commit()
        cursor.execute(f"SELECT {id_column} FROM {table} WHERE {column} = ?", value)
        return cursor.fetchone()[0]

def update_saldo(cnxn, cuenta_id, fecha_id, monto, tipo_gasto):
    """Calcula y actualiza el saldo de una cuenta."""
    cursor = cnxn.cursor()
    cursor.execute("""
        SELECT TOP 1 Saldo
        FROM FactSaldo
        WHERE CuentaID = ?
        ORDER BY SaldoID DESC;
    """, cuenta_id)
    last_saldo = cursor.fetchone()
    current_saldo = last_saldo[0] if last_saldo else Decimal(0)

    if tipo_gasto in ['Sueldo', 'Ventas', 'Ingresos']:
        new_saldo = current_saldo + monto
    else:
        new_saldo = current_saldo - monto

    sql_insert_saldo = """
        INSERT INTO FactSaldo (CuentaID, FechaID, Saldo)
        VALUES (?, ?, ?);
    """
    cursor.execute(sql_insert_saldo, cuenta_id, fecha_id, new_saldo)
    cnxn.commit()

def record_transaction(data):
    """
    Función principal para registrar una transacción completa.
    """
    cnxn = get_db_connection()
    if not cnxn:
        return False, "No se pudo conectar a la base de datos."

    try:
        cursor = cnxn.cursor()
        
        fecha_id = int(data['fecha'].strftime('%Y%m%d'))
        tipo_gasto_id = get_or_create_dimension(cnxn, 'DimTipoGasto', 'TipoGastoID', 'TipoGasto', data['tipo_gasto'], 
                                                {'CategoriaPrincipal': data['categoria']})
        persona_id = get_or_create_dimension(cnxn, 'DimPersona', 'PersonaID', 'NombrePersona', data['persona'], 
                                             {'Relacion': data['relacion']})
        ubicacion_id = get_or_create_dimension(cnxn, 'DimUbicacion', 'UbicacionID', 'Ciudad', data['ubicacion'], 
                                               {'Pais': data['pais']})
        cuenta_id = get_or_create_dimension(cnxn, 'DimCuenta', 'CuentaID', 'NombreCuenta', data['cuenta'], 
                                            {'TipoCuenta': data['tipo_cuenta']})
        
        sql_insert_transaccion = """
            INSERT INTO FactTransacciones (FechaID, TipoGastoID, PersonaID, UbicacionID, CuentaID, Monto, Descripcion)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        cursor.execute(sql_insert_transaccion, 
                       fecha_id, tipo_gasto_id, persona_id, ubicacion_id, cuenta_id, 
                       data['monto'], data['descripcion'])
        cnxn.commit()

        update_saldo(cnxn, cuenta_id, fecha_id, data['monto'], data['tipo_gasto'])
        
        return True, "Transacción registrada y saldo actualizado con éxito."
    
    except Exception as e:
        cnxn.rollback()
        return False, f"Error al registrar la transacción: {e}"
        
    finally:
        if cnxn:
            cnxn.close()

def get_current_saldo_by_account(cnxn, account_name):
    """Obtiene el último saldo de una cuenta específica."""
    cursor = cnxn.cursor()
    cursor.execute("""
        SELECT TOP 1 T1.Saldo
        FROM FactSaldo AS T1
        JOIN DimCuenta AS T2 ON T1.CuentaID = T2.CuentaID
        WHERE T2.NombreCuenta = ?
        ORDER BY T1.SaldoID DESC;
    """, account_name)
    row = cursor.fetchone()
    return row.Saldo if row else Decimal(0)
