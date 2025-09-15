import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
from decimal import Decimal

# Importa las funciones del módulo db_manager
from db_manager import get_db_connection, get_dimension_values, record_transaction, get_current_saldo_by_account

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

def update_saldo_display(event=None):
    """Actualiza la etiqueta del saldo en la interfaz gráfica."""
    selected_account = combo_cuenta.get()
    if not selected_account:
        label_saldo.config(text="Seleccione una cuenta para ver el saldo.")
        return

    cnxn = get_db_connection()
    if not cnxn:
        label_saldo.config(text="Error de conexión a la base de datos.")
        return

    saldo_valor = get_current_saldo_by_account(cnxn, selected_account)
    cnxn.close()

    monto_formateado = f"${saldo_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    label_saldo.config(text=f"Saldo en '{selected_account}': {monto_formateado}")

def add_new_dimension(dim_name, col_name, additional_data=None):
    """Abre una nueva ventana para agregar un nuevo valor a una dimensión."""
    new_window = tk.Toplevel(root)
    new_window.title(f"Agregar {dim_name}")
    
    tk.Label(new_window, text=f"Nuevo {col_name}:").grid(row=0, column=0, padx=5, pady=5)
    entry = tk.Entry(new_window)
    entry.grid(row=0, column=1, padx=5, pady=5)
    
    if additional_data:
        tk.Label(new_window, text=f"Dato Adicional ({list(additional_data.keys())[0]}):").grid(row=1, column=0, padx=5, pady=5)
        entry_adicional = tk.Entry(new_window)
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

    btn_save = tk.Button(new_window, text="Guardar", command=save_new_value)
    btn_save.grid(row=2, column=0, columnspan=2, pady=10)


def update_combobox_values(combobox, table, column):
    """Función para actualizar los valores de un combobox desde la base de datos."""
    cnxn = get_db_connection()
    if cnxn:
        values = get_dimension_values(cnxn, table, column)
        combobox['values'] = values
        cnxn.close()


def main_gui():
    global root, combo_tipo_gasto, combo_categoria, combo_persona, combo_relacion, combo_ubicacion, combo_pais, combo_cuenta, combo_tipo_cuenta, entry_fecha, entry_monto, entry_descripcion, label_saldo
    
    # Crear la ventana principal y obtener datos de la BD
    root = tk.Tk()
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
    tk.Label(root, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_fecha = tk.Entry(root)
    entry_fecha.grid(row=0, column=1, padx=10, pady=5)
    entry_fecha.insert(0, str(date.today()))

    tk.Label(root, text="Monto:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_monto = tk.Entry(root)
    entry_monto.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="Descripción:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    entry_descripcion = tk.Entry(root)
    entry_descripcion.grid(row=2, column=1, padx=10, pady=5)

    # Combobox para las dimensiones
    tk.Label(root, text="Tipo de Gasto:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    combo_tipo_gasto = ttk.Combobox(root, values=tipos_gasto_list)
    combo_tipo_gasto.grid(row=3, column=1, padx=10, pady=5)
    btn_add_tipo_gasto = tk.Button(root, text="+", command=lambda: add_new_dimension("DimTipoGasto", "TipoGasto", {"CategoriaPrincipal": ""}))
    btn_add_tipo_gasto.grid(row=3, column=2, padx=2, pady=5)

    tk.Label(root, text="Categoría:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    combo_categoria = ttk.Combobox(root, values=categorias_list)
    combo_categoria.grid(row=4, column=1, padx=10, pady=5)
    btn_add_categoria = tk.Button(root, text="+", command=lambda: add_new_dimension("DimTipoGasto", "CategoriaPrincipal"))
    btn_add_categoria.grid(row=4, column=2, padx=2, pady=5)
            
    tk.Label(root, text="Persona:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    combo_persona = ttk.Combobox(root, values=personas_list)
    combo_persona.grid(row=5, column=1, padx=10, pady=5)
    btn_add_persona = tk.Button(root, text="+", command=lambda: add_new_dimension("DimPersona", "NombrePersona", {"Relacion": ""}))
    btn_add_persona.grid(row=5, column=2, padx=2, pady=5)


    tk.Label(root, text="Relación:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
    combo_relacion = ttk.Combobox(root, values=relaciones_list)
    combo_relacion.grid(row=6, column=1, padx=10, pady=5)
    btn_add_relacion = tk.Button(root, text="+", command=lambda: add_new_dimension("DimPersona", "Relacion"))
    btn_add_relacion.grid(row=6, column=2, padx=2, pady=5)

    tk.Label(root, text="Ciudad:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
    combo_ubicacion = ttk.Combobox(root, values=ciudades_list)
    combo_ubicacion.grid(row=7, column=1, padx=10, pady=5)
    btn_add_ubicacion = tk.Button(root, text="+", command=lambda: add_new_dimension("DimUbicacion", "Ciudad", {"Pais": ""}))
    btn_add_ubicacion.grid(row=7, column=2, padx=2, pady=5)


    tk.Label(root, text="País:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
    combo_pais = ttk.Combobox(root, values=paises_list)
    combo_pais.grid(row=8, column=1, padx=10, pady=5)
    btn_add_pais = tk.Button(root, text="+", command=lambda: add_new_dimension("DimUbicacion", "Pais"))
    btn_add_pais.grid(row=8, column=2, padx=2, pady=5)

    tk.Label(root, text="Cuenta:").grid(row=9, column=0, padx=10, pady=5, sticky="w")
    combo_cuenta = ttk.Combobox(root, values=cuentas_list)
    combo_cuenta.grid(row=9, column=1, padx=10, pady=5)
    combo_cuenta.bind("<<ComboboxSelected>>", update_saldo_display)
    btn_add_cuenta = tk.Button(root, text="+", command=lambda: add_new_dimension("DimCuenta", "NombreCuenta", {"TipoCuenta": ""}))
    btn_add_cuenta.grid(row=9, column=2, padx=2, pady=5)

    tk.Label(root, text="Tipo de Cuenta:").grid(row=10, column=0, padx=10, pady=5, sticky="w")
    combo_tipo_cuenta = ttk.Combobox(root, values=tipos_cuenta_list)
    combo_tipo_cuenta.grid(row=10, column=1, padx=10, pady=5)
    btn_add_tipo_cuenta = tk.Button(root, text="+", command=lambda: add_new_dimension("DimCuenta", "TipoCuenta"))
    btn_add_tipo_cuenta.grid(row=10, column=2, padx=2, pady=5)

    # Botón para enviar
    button_submit = tk.Button(root, text="Registrar Transacción", command=submit_form)
    button_submit.grid(row=11, column=0, columnspan=3, pady=10)

    # Etiqueta para mostrar el saldo
    label_saldo = tk.Label(root, text="Seleccione una cuenta para ver el saldo.", fg="blue")
    label_saldo.grid(row=12, column=0, columnspan=3, pady=10)

    # Iniciar el bucle de la aplicación
    root.mainloop()

if __name__ == "__main__":
    main_gui()
