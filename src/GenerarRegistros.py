import random
from datetime import date, timedelta
from decimal import Decimal
import sys
import pyodbc

# Importa las funciones del módulo db_manager
from db_manager import get_db_connection, get_dimension_values, record_transaction

# --- Obtener los valores de las dimensiones de la base de datos ---
cnxn = get_db_connection()
if not cnxn:
    print("No se pudo conectar a la base de datos para obtener los valores dimensionales.")
    sys.exit()

try:
    tipos_gasto_list = get_dimension_values(cnxn, "DimTipoGasto", "TipoGasto")
    categorias_list = get_dimension_values(cnxn, "DimTipoGasto", "CategoriaPrincipal")
    personas_list = get_dimension_values(cnxn, "DimPersona", "NombrePersona")
    relaciones_list = get_dimension_values(cnxn, "DimPersona", "Relacion")
    ciudades_list = get_dimension_values(cnxn, "DimUbicacion", "Ciudad")
    paises_list = get_dimension_values(cnxn, "DimUbicacion", "Pais")
    cuentas_list = get_dimension_values(cnxn, "DimCuenta", "NombreCuenta")
    tipos_cuenta_list = get_dimension_values(cnxn, "DimCuenta", "TipoCuenta")
    cnxn.close()
except Exception as e:
    print(f"Error al obtener los valores dimensionales: {e}")
    sys.exit()

# Diccionario para la lógica de los datos
logica_tipo_gasto = {
    'Sueldo': 'Ingresos',
    'Ventas': 'Ingresos',
    'Arriendo': 'Gastos Fijos',
    'Seguros': 'Gastos Fijos',
    'Comida': 'Gastos Variables',
    'Entretenimiento': 'Gastos Variables'
}

logica_cuenta = {
    'Cuenta Banco BCI': 'Banco',
    'Tarjeta Credito Banco de Chile': 'Tarjeta de Credito',
    'Billetera (Efectivo)': 'Efectivo'
}

logica_ubicacion = {
    'Puerto Montt': 'Chile',
    'Santiago': 'Chile',
    'Madrid': 'España'
}

# Definición de los objetivos de saldo
saldo_objetivo = {
    'Cuenta Banco BCI': random.uniform(9000000, 10000000),
    'Tarjeta Credito Banco de Chile': random.uniform(1000000, 2000000),
    'Billetera (Efectivo)': random.uniform(100000, 500000)
}

saldo_actual = {
    'Cuenta Banco BCI': Decimal(0),
    'Tarjeta Credito Banco de Chile': Decimal(0),
    'Billetera (Efectivo)': Decimal(0)
}

num_registros_por_cuenta = 1000 // len(cuentas_list)

def generar_datos_logicos(cuenta_actual, fecha_base):
    """Genera una transacción con datos lógicos y aleatorios."""
    
    # Seleccionar tipo de gasto (Ingreso o Gasto)
    es_ingreso = False
    if saldo_actual[cuenta_actual] < Decimal(saldo_objetivo[cuenta_actual]):
        es_ingreso = True
    elif saldo_actual[cuenta_actual] > Decimal(saldo_objetivo[cuenta_actual]):
        es_ingreso = False
    else:
        es_ingreso = random.choice([True, False])

    if es_ingreso:
        tipo_gasto = random.choice(['Sueldo', 'Ventas'])
        monto = Decimal(random.uniform(50000, 500000)).quantize(Decimal('0.01'))
        descripcion = f"Ingreso por {tipo_gasto}"
    else:
        tipo_gasto = random.choice(['Arriendo', 'Seguros', 'Comida', 'Entretenimiento'])
        monto = Decimal(random.uniform(10000, 200000)).quantize(Decimal('0.01'))
        descripcion = f"Gasto en {tipo_gasto}"

    categoria = logica_tipo_gasto[tipo_gasto]
    tipo_cuenta = logica_cuenta[cuenta_actual]
    
    persona = random.choice(personas_list)
    relacion = relaciones_list[personas_list.index(persona)]
    ubicacion = random.choice(ciudades_list)
    pais = logica_ubicacion[ubicacion]

    return {
        'fecha': fecha_base,
        'monto': monto,
        'descripcion': descripcion,
        'tipo_gasto': tipo_gasto,
        'categoria': categoria,
        'persona': persona,
        'relacion': relacion,
        'ubicacion': ubicacion,
        'pais': pais,
        'cuenta': cuenta_actual,
        'tipo_cuenta': tipo_cuenta
    }


print(f"Iniciando la generación e inserción de {1000} registros...")
fecha_actual = date(2025, 1, 1)

for i in range(1000):
    
    cuenta_aleatoria = random.choice(cuentas_list)
    
    data = generar_datos_logicos(cuenta_aleatoria, fecha_actual)
    
    success, message = record_transaction(data)
    
    if success:
        if data['categoria'] == 'Ingresos':
            saldo_actual[cuenta_aleatoria] += data['monto']
        else:
            saldo_actual[cuenta_aleatoria] -= data['monto']
        print(f"Registro {i+1} de {1000} insertado.")
    else:
        print(f"Error al insertar registro {i+1}: {message}")
    
    fecha_actual += timedelta(days=1)
        
print("\n¡Generación de datos finalizada!")
