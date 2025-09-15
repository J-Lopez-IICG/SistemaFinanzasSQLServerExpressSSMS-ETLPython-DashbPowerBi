-- DDL para la Dimensión de Fechas
CREATE TABLE DimFecha (
    FechaID INT PRIMARY KEY,
    Fecha DATE NOT NULL,
    Dia INT NOT NULL,
    Mes INT NOT NULL,
    Anio INT NOT NULL,
    NombreMes VARCHAR(50),
    Trimestre INT,
    DiaSemana VARCHAR(50)
);

-- DDL para la Dimensión de Tipos de Gastos
CREATE TABLE DimTipoGasto (
    TipoGastoID INT IDENTITY(1,1) PRIMARY KEY,
    TipoGasto VARCHAR(50) NOT NULL,
    CategoriaPrincipal VARCHAR(50)
);

-- DDL para la Dimensión de Personas
CREATE TABLE DimPersona (
    PersonaID INT IDENTITY(1,1) PRIMARY KEY,
    NombrePersona VARCHAR(50) NOT NULL,
    Relacion VARCHAR(50)
);

-- DDL para la Dimensión de Ubicación
CREATE TABLE DimUbicacion (
    UbicacionID INT IDENTITY(1,1) PRIMARY KEY,
    Ciudad VARCHAR(100),
    Pais VARCHAR(100)
);

-- DDL para la Dimensión de Cuentas
CREATE TABLE DimCuenta (
    CuentaID INT IDENTITY(1,1) PRIMARY KEY,
    NombreCuenta VARCHAR(100) NOT NULL,
    TipoCuenta VARCHAR(50),
    Banco VARCHAR(100)
);

-- DDL para la Tabla de Hechos (Fact Table)
CREATE TABLE FactTransacciones (
    TransaccionID INT IDENTITY(1,1) PRIMARY KEY,
    FechaID INT NOT NULL,
    TipoGastoID INT NOT NULL,
    PersonaID INT NOT NULL,
    UbicacionID INT NOT NULL,
    CuentaID INT NOT NULL,
    Monto DECIMAL(10, 2) NOT NULL,
    Descripcion VARCHAR(255),
    FOREIGN KEY (FechaID) REFERENCES DimFecha(FechaID),
    FOREIGN KEY (TipoGastoID) REFERENCES DimTipoGasto(TipoGastoID),
    FOREIGN KEY (PersonaID) REFERENCES DimPersona(PersonaID),
    FOREIGN KEY (UbicacionID) REFERENCES DimUbicacion(UbicacionID),
    FOREIGN KEY (CuentaID) REFERENCES DimCuenta(CuentaID)
);