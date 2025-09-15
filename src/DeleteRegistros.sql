USE FinanzasPersonales;
GO

-- Paso 1: Borrar todas las tablas para una limpieza completa
-- El orden es crucial para evitar errores de clave foránea.
IF OBJECT_ID('FactTransacciones', 'U') IS NOT NULL DROP TABLE FactTransacciones;
IF OBJECT_ID('FactSaldo', 'U') IS NOT NULL DROP TABLE FactSaldo;
GO

-- Ahora, borramos las tablas de dimensiones.
IF OBJECT_ID('DimTipoGasto', 'U') IS NOT NULL DROP TABLE DimTipoGasto;
IF OBJECT_ID('DimPersona', 'U') IS NOT NULL DROP TABLE DimPersona;
IF OBJECT_ID('DimUbicacion', 'U') IS NOT NULL DROP TABLE DimUbicacion;
IF OBJECT_ID('DimCuenta', 'U') IS NOT NULL DROP TABLE DimCuenta;
IF OBJECT_ID('DimFecha', 'U') IS NOT NULL DROP TABLE DimFecha;
GO