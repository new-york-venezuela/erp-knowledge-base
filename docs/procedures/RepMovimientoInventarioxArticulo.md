# SP: RepMovimientoInventarioxArticulo
**Tipo**: Reporte / Kardex
**Módulo**: Inventario
**Descripción de Negocio**: Es el reporte canónico de **kardex de movimientos de inventario por artículo** — la fuente de verdad para "cómo evolucionó el stock de este artículo en el tiempo". Es el candidato ideal como fuente de datos para el gráfico de evolución de inventario y el cálculo de tasa de consumo del módulo nuevo, porque agrega en una sola secuencia ordenada **todos** los tipos de movimiento (compras, ventas, ajustes, traslados, devoluciones), no solo uno. Verificado leyendo el `OBJECT_DEFINITION` completo (3687 caracteres) contra la base `Ncake_a`.

## Firma
```sql
CREATE PROCEDURE [dbo].[RepMovimientoInventarioxArticulo]
    @sCo_Art_d CHAR(30) = NULL, @sCo_Art_h CHAR(30) = NULL,        -- rango de artículo (código desde/hasta)
    @dCo_fecha_d DATETIME = NULL, @dCo_fecha_h DATETIME = NULL,    -- rango de fecha
    @sCo_Almacen CHAR(6) = NULL,                                   -- filtro de almacén (opcional)
    @sCo_Linea_d CHAR(6) = NULL, @sCo_Linea_h CHAR(6) = NULL,      -- rango de línea de artículo
    @sCo_Categoria_d CHAR(6) = NULL, @sCo_Categoria_h CHAR(6) = NULL, -- rango de categoría
    @sCo_Movimiento CHAR(4) = NULL,                                -- filtro por tipo: 'COMP','FACT','AJUS','TRAS', etc. NULL/'TODO' = todos
    @sCo_Sucursal CHAR(6) = NULL,
    @sCampOrderBy VARCHAR(16) = NULL, @sDir VARCHAR(6) = NULL,
    @bHeaderRep BIT = 0
```

## Cómo funciona
Por cada artículo (`saArticulo`, filtrado por rango de código/línea/categoría), hace `INNER JOIN` con el resultado de la función de tabla **`dbo.MovimientoInventario(...)`** — ver [`MovimientoInventario`](MovimientoInventario.md) — que es donde vive la lógica real de unión de movimientos. Además calcula:
- `StockInic`: stock inicial al comienzo del rango de fecha, vía `dbo.ConsultarStockActualxAlmacenxFecha(co_art, co_alma, fecha_desde - 1seg, NULL)`. Para artículos tipo `S` (servicio) siempre devuelve 0 — no tienen stock.
- `costo_pro`: costo ponderado de la línea, vía `dbo.ObtenerCostoPonderadoSalida`/`ObtenerCostoPonderadoEntrada` según si la línea es una salida o entrada.
- Trae también toda la info de unidades alternativas del artículo (`DetalleUnidadesArticulos`) — probablemente irrelevante para el módulo nuevo salvo que se necesite mostrar cantidades en unidades distintas a la base.

Ordena por `co_art, fecha, fe_us_in, tipo, doc_num, reng_num` — es decir, ya viene en orden cronológico por artículo, ideal para alimentar un gráfico de serie de tiempo o un cálculo de saldo corrido.

## Recomendación para el módulo de Inventario nuevo
Para el gráfico de "evolución de inventario en el tiempo" y el cálculo de "consumo reciente / velocidad de agotamiento", **usar directamente la función `dbo.MovimientoInventario(...)`** (no este SP completo, que trae columnas de unidades alternativas innecesarias) filtrando por artículo, almacén y rango de fecha, y sumando `total_salida` (para consumo) o `(total_entrada - total_salida)` acumulado (para el saldo corrido). Filtrar siempre `anulado=0` en la fuente subyacente — la función ya expone la columna `anulado` por fila para que el consumidor decida, no filtra ella misma.

## Tablas/Objetos Referenciados
- [`saArticulo`](../tables/saArticulo.md), `saArtUnidad`
- Función de tabla `dbo.MovimientoInventario` — ver [`MovimientoInventario`](MovimientoInventario.md)
- Funciones escalares: `dbo.ConsultarStockActualxAlmacenxFecha`, `dbo.ObtenerCostoPonderadoSalida`, `dbo.ObtenerCostoPonderadoEntrada`, `dbo.DetalleUnidadesArticulos`, `dbo.fechasimple`

## Recetario SQL de Negocio
```sql
-- Kardex de un artículo en un almacén, últimos 90 días, todos los tipos de movimiento
EXEC RepMovimientoInventarioxArticulo
    @sCo_Art_d = '0000063', @sCo_Art_h = '0000063',
    @dCo_fecha_d = '2026-05-22', @dCo_fecha_h = '2026-08-20',
    @sCo_Almacen = '14';

-- Equivalente más ligero, consumiendo la función directamente (recomendado para el backend del módulo)
SELECT co_art, co_alma, tipo, doc_num, fecha, total_entrada, total_salida, anulado
FROM dbo.MovimientoInventario('0000063','0000063','2026-05-22','2026-08-20','14',NULL,NULL,NULL,NULL,NULL,NULL)
WHERE anulado = 0
ORDER BY fecha;
```
