SELECT
    T1.Fecha,
    T1.DiaSemana,
    T1.NombreMes AS Mes,
    T2.Descripcion AS DescripcionTransaccion,
    T2.Monto,
    T3.TipoGasto,
    T3.CategoriaPrincipal,
    T4.NombrePersona,
    T4.Relacion,
    T5.Ciudad,
    T5.Pais,
    T6.NombreCuenta,
    T6.TipoCuenta
FROM
    DimFecha AS T1
JOIN
    FactTransacciones AS T2 ON T1.FechaID = T2.FechaID
JOIN
    DimTipoGasto AS T3 ON T2.TipoGastoID = T3.TipoGastoID
JOIN
    DimPersona AS T4 ON T2.PersonaID = T4.PersonaID
JOIN
    DimUbicacion AS T5 ON T2.UbicacionID = T5.UbicacionID
JOIN
    DimCuenta AS T6 ON T2.CuentaID = T6.CuentaID;