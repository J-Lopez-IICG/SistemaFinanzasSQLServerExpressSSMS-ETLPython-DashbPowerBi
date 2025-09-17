import pyodbc
from datetime import date
from decimal import Decimal
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Importa ttk para los comboboxes
import customtkinter  # La nueva importación

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

def update_saldo_display(event=None):
    """Actualiza la etiqueta del saldo en la interfaz gráfica."""
    selected_account = combo_cuenta.get()
    if not selected_account:
        label_saldo.configure(text="Seleccione una cuenta para ver el saldo.")
        return

    cnxn = get_db_connection()
    if not cnxn:
        label_saldo.configure(text="Error de conexión a la base de datos.")
        return

    saldo_valor = get_current_saldo_by_account(cnxn, selected_account)
    cnxn.close()

    monto_formateado = f"${saldo_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    label_saldo.configure(text=f"Saldo en '{selected_account}': {monto_formateado}")

# --- Lógica del formulario Tkinter ---
def add_new_dimension(dim_name, col_name, additional_data=None):
    """Abre una nueva ventana para agregar un nuevo valor a una dimensión."""
    new_window = customtkinter.CTkToplevel(root)
    new_window.title(f"Agregar {dim_name}")
    
    customtkinter.CTkLabel(new_window, text=f"Nuevo {col_name}:").grid(row=0, column=0, padx=5, pady=5)
    entry = customtkinter.CTkEntry(new_window)
    entry.grid(row=0, column=1, padx=5, pady=5)
    
    if additional_data:
        customtkinter.CTkLabel(new_window, text=f"Dato Adicional ({list(additional_data.keys())[0]}):").grid(row=1, column=0, padx=5, pady=5)
        entry_adicional = customtkinter.CTkEntry(new_window)
        entry_adicional.grid(row=1, column=1, padx=5, pady=5)
    
    def save_new_value():
        new_value = entry.get()
        if not new_value:
            messagebox.showerror("Error", "El campo no puede estar vacío.")
            return

        cnxn = get_db_connection()
        if not cnxn:
            return

        try:
            if additional_data:
                adicional = entry_adicional.get()
                adicional_dict = {list(additional_data.keys())[0]: adicional}
                get_or_create_dimension(cnxn, dim_name, f"{col_name}ID", col_name, new_value, adicional_dict)
            else:
                get_or_create_dimension(cnxn, dim_name, f"{col_name}ID", col_name, new_value)
            
            cnxn.close()
            messagebox.showinfo("Éxito", f"'{new_value}' agregado con éxito a {dim_name}.")
            
            if dim_name == 'DimTipoGasto':
                update_combobox_values(combo_tipo_gasto, "DimTipoGasto", "TipoGasto")
                update_combobox_values(combo_categoria, "DimTipoGasto", "CategoriaPrincipal")
            if dim_name == 'DimPersona':
                update_combobox_values(combo_persona, "DimPersona", "NombrePersona")
                update_combobox_values(combo_relacion, "DimPersona", "Relacion")
            if dim_name == 'DimUbicacion':
                update_combobox_values(combo_ubicacion, "DimUbicacion", "Ciudad")
                update_combobox_values(combo_pais, "DimUbicacion", "Pais")
            if dim_name == 'DimCuenta':
                update_combobox_values(combo_cuenta, "DimCuenta", "NombreCuenta")
                update_combobox_values(combo_tipo_cuenta, "DimCuenta", "TipoCuenta")

            new_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el valor: {e}")
            cnxn.close()

    btn_save = customtkinter.CTkButton(new_window, text="Guardar", command=save_new_value)
    btn_save.grid(row=2, column=0, columnspan=2, pady=10)

def update_combobox_values(combobox, table, column):
    """Función para actualizar los valores de un combobox desde la base de datos."""
    cnxn = get_db_connection()
    if cnxn:
        values = get_dimension_values(cnxn, table, column)
        combobox.configure(values=values)
        cnxn.close()


def submit_form():
    """Función que se llama cuando se presiona el botón 'Registrar'."""
    try:
        data = {
            'fecha': date.fromisoformat(entry_fecha.get()),
            'monto': Decimal(entry_monto.get()),
            'descripcion': entry_descripcion.get(),
            'tipo_gasto': combo_tipo_gasto.get(),
            'categoria': combo_categoria.get(),
            'persona': combo_persona.get(),
            'relacion': combo_relacion.get(),
            'ubicacion': combo_ubicacion.get(),
            'pais': combo_pais.get(),
            'cuenta': combo_cuenta.get(),
            'tipo_cuenta': combo_tipo_cuenta.get()
        }

        success, message = record_transaction(data)
        
        if success:
            messagebox.showinfo("Éxito", message)
            update_saldo_display()
        else:
            messagebox.showerror("Error", message)

    except Exception as e:
        messagebox.showerror("Error", f"Verifique los datos ingresados: {e}")

def main_gui():
    global root, combo_tipo_gasto, combo_categoria, combo_persona, combo_relacion, combo_ubicacion, combo_pais, combo_cuenta, combo_tipo_cuenta, entry_fecha, entry_monto, entry_descripcion, label_saldo

    customtkinter.set_appearance_mode("dark")  # Modos: "System" (estándar), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Temas: "blue" (estándar), "green", "dark-blue"
    
    # Crear la ventana principal y obtener datos de la BD
    root = customtkinter.CTk()
    root.title("Registrar Transacción de Finanzas")

    cnxn = get_db_connection()
    if cnxn:
        tipos_gasto_list = get_dimension_values(cnxn, "DimTipoGasto", "TipoGasto")
        categorias_list = get_dimension_values(cnxn, "DimTipoGasto", "CategoriaPrincipal")
        personas_list = get_dimension_values(cnxn, "DimPersona", "NombrePersona")
        relaciones_list = get_dimension_values(cnxn, "DimPersona", "Relacion")
        ciudades_list = get_dimension_values(cnxn, "DimUbicacion", "Ciudad")
        paises_list = get_dimension_values(cnxn, "DimUbicacion", "Pais")
        cuentas_list = get_dimension_values(cnxn, "DimCuenta", "NombreCuenta")
        tipos_cuenta_list = get_dimension_values(cnxn, "DimCuenta", "TipoCuenta")
        cnxn.close()

    # Crear los widgets del formulario
    customtkinter.CTkLabel(root, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_fecha = customtkinter.CTkEntry(root)
    entry_fecha.grid(row=0, column=1, padx=10, pady=5)
    entry_fecha.insert(0, str(date.today()))

    customtkinter.CTkLabel(root, text="Monto:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_monto = customtkinter.CTkEntry(root)
    entry_monto.grid(row=1, column=1, padx=10, pady=5)

    customtkinter.CTkLabel(root, text="Descripción:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    entry_descripcion = customtkinter.CTkEntry(root)
    entry_descripcion.grid(row=2, column=1, padx=10, pady=5)

    # Combobox para las dimensiones
    customtkinter.CTkLabel(root, text="Tipo de Gasto:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    combo_tipo_gasto = customtkinter.CTkComboBox(root, values=tipos_gasto_list)
    combo_tipo_gasto.grid(row=3, column=1, padx=10, pady=5)
    btn_add_tipo_gasto = customtkinter.CTkButton(root, text="+", width=30, command=lambda: add_new_dimension("DimTipoGasto", "TipoGasto", {"CategoriaPrincipal": ""}))
    btn_add_tipo_gasto.grid(row=3, column=2, padx=2, pady=5)

    customtkinter.CTkLabel(root, text="Categoría:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    combo_categoria = customtkinter.CTkComboBox(root, values=categorias_list)
    combo_categoria.grid(row=4, column=1, padx=10, pady=5)
    btn_add_categoria = customtkinter.CTkButton(root, text="+", width=30, command=lambda: add_new_dimension("DimTipoGasto", "CategoriaPrincipal"))
    btn_add_categoria.grid(row=4, column=2, padx=2, pady=5)
            
    customtkinter.CTkLabel(root, text="Persona:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    combo_persona = customtkinter.CTkComboBox(root, values=personas_list)
    combo_persona.grid(row=5, column=1, padx=10, pady=5)
    btn_add_persona = customtkinter.CTkButton(root, text="+", width=30, command=lambda: add_new_dimension("DimPersona", "NombrePersona", {"Relacion": ""}))
    btn_add_persona.grid(row=5, column=2, padx=2, pady=5)


    customtkinter.CTkLabel(root, text="Relación:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
    combo_relacion = customtkinter.CTkComboBox(root, values=relaciones_list)
    combo_relacion.grid(row=6, column=1, padx=10, pady=5)
    btn_add_relacion = customtkinter.CTkButton(root, text="+", width=30, command=lambda: add_new_dimension("DimPersona", "Relacion"))
    btn_add_relacion.grid(row=6, column=2, padx=2, pady=5)

    customtkinter.CTkLabel(root, text="Ciudad:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
    combo_ubicacion = customtkinter.CTkComboBox(root, values=ciudades_list)
    combo_ubicacion.grid(row=7, column=1, padx=10, pady=5)
    btn_add_ubicacion = customtkinter.CTkButton(root, text="+", width=30, command=lambda: add_new_dimension("DimUbicacion", "Ciudad", {"Pais": ""}))
    btn_add_ubicacion.grid(row=7, column=2, padx=2, pady=5)

    customtkinter.CTkLabel(root, text="País:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
    combo_pais = customtkinter.CTkComboBox(root, values=paises_list)
    combo_pais.grid(row=8, column=1, padx=10, pady=5)
    btn_add_pais = customtkinter.CTkButton(root, text="+", width=30, command=lambda: add_new_dimension("DimUbicacion", "Pais"))
    btn_add_pais.grid(row=8, column=2, padx=2, pady=5)

    customtkinter.CTkLabel(root, text="Cuenta:").grid(row=9, column=0, padx=10, pady=5, sticky="w")
    combo_cuenta = customtkinter.CTkComboBox(root, values=cuentas_list)
    combo_cuenta.grid(row=9, column=1, padx=10, pady=5)
    combo_cuenta.bind("<<ComboboxSelected>>", update_saldo_display)
    btn_add_cuenta = customtkinter.CTkButton(root, text="+", width=30, command=lambda: add_new_dimension("DimCuenta", "NombreCuenta", {"TipoCuenta": ""}))
    btn_add_cuenta.grid(row=9, column=2, padx=2, pady=5)

    customtkinter.CTkLabel(root, text="Tipo de Cuenta:").grid(row=10, column=0, padx=10, pady=5, sticky="w")
    combo_tipo_cuenta = customtkinter.CTkComboBox(root, values=tipos_cuenta_list)
    combo_tipo_cuenta.grid(row=10, column=1, padx=10, pady=5)
    btn_add_tipo_cuenta = customtkinter.CTkButton(root, text="+", width=30, command=lambda: add_new_dimension("DimCuenta", "TipoCuenta"))
    btn_add_tipo_cuenta.grid(row=10, column=2, padx=2, pady=5)

    # Botón para enviar
    button_submit = customtkinter.CTkButton(root, text="Registrar Transacción", command=submit_form)
    button_submit.grid(row=11, column=0, columnspan=3, pady=10)

    # Etiqueta para mostrar el saldo
    label_saldo = customtkinter.CTkLabel(root, text="Seleccione una cuenta para ver el saldo.", fg_color="transparent")
    label_saldo.grid(row=12, column=0, columnspan=3, pady=10)

    # Iniciar el bucle de la aplicación
    root.mainloop()

if __name__ == "__main__":
    main_gui()
