INSERT INTO DimTipoGasto (TipoGasto, CategoriaPrincipal) VALUES
('Arriendo', 'Gastos Fijos'),
('Seguros', 'Gastos Fijos'),
('Sueldo', 'Ingresos'),
('Ventas', 'Ingresos'),
('Entretenimiento', 'Gastos Variables'),
('Comida', 'Gastos Variables');
GO

INSERT INTO DimPersona (NombrePersona, Relacion) VALUES
('Javier', 'Yo'),
('Maria', 'Pareja'),
('Lucas', 'Hijo');
GO

INSERT INTO DimUbicacion (Ciudad, Pais) VALUES
('Puerto Montt', 'Chile'),
('Santiago', 'Chile'),
('Madrid', 'España');
GO

INSERT INTO DimCuenta (NombreCuenta, TipoCuenta, Banco) VALUES
('Cuenta Banco BCI', 'Banco', 'BCI'),
('Tarjeta Credito Banco de Chile', 'Tarjeta de Credito', 'Banco de Chile'),
('Billetera (Efectivo)', 'Efectivo', NULL);
GO

--Correr script de las fechas Python primero "AutomatizacionPoblacionDimFecha.py"

-- Paso 4: Inicializar un saldo de 0 para cada cuenta para evitar errores
INSERT INTO FactSaldo (CuentaID, FechaID, Saldo) VALUES
(1, 20250915, 0), -- Para Cuenta Banco BCI
(2, 20250915, 0), -- Para Tarjeta Credito Banco de Chile
(3, 20250915, 0); -- Para Billetera (Efectivo)
GO