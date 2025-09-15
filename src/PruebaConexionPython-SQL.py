import pyodbc
server = 'Javier-Asus\\SQLEXPRESS' 
database = 'FinanzasPersonales'  
cnxn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
)
try:
    cnxn = pyodbc.connect(cnxn_str)
    cursor = cnxn.cursor()
    print("¡Conexión a la base de datos establecida con éxito!")
    cursor.execute("SELECT GETDATE() AS CurrentDateTime;")
    row = cursor.fetchone()
    if row:
        print(f"La fecha y hora actual en el servidor es: {row.CurrentDateTime}")
    cnxn.close()
except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"¡Error al conectar a la base de datos! Código de estado SQL: {sqlstate}")
    print(f"Detalles del error: {ex}")
