# Función: dbo.MovimientoInventario
**Tipo**: Función de tabla (inline table-valued function)
**Módulo**: Inventario
**Descripción de Negocio**: Es el **kardex unificado** de Profit Plus — la única fuente que combina, en una sola tabla virtual, absolutamente todos los movimientos de inventario del sistema (compras, ventas, notas de recepción/entrega, devoluciones, ajustes, traslados, órdenes/cotizaciones de compra). Es consumida por `RepMovimientoInventarioxArticulo` (ver [doc](RepMovimientoInventarioxArticulo.md)) y por los demás reportes `RepMovimientoInventario*`. Verificado leyendo el `OBJECT_DEFINITION` completo (18.828 caracteres, 12 ramas `UNION ALL`) contra la base `Ncake_a`. **No existía documentación previa de esta función** — es la pieza central recomendada como fuente de datos para el módulo de Inventario nuevo (gráfico de evolución de stock + cálculo de consumo).

## Firma
```sql
CREATE FUNCTION [dbo].[MovimientoInventario]
    (
    @sCo_Art_d CHAR(30) = NULL, @sCo_Art_h CHAR(30) = NULL,          -- rango de código de artículo
    @dCo_fecha_d DATETIME = NULL, @dCo_fecha_h DATETIME = NULL,      -- rango de fecha
    @sCo_Almacen CHAR(6) = NULL,                                     -- filtro de almacén
    @sCo_Linea_d CHAR(6) = NULL, @sCo_Linea_h CHAR(6) = NULL,        -- rango de línea de artículo
    @sCo_Categoria_d CHAR(6) = NULL, @sCo_Categoria_h CHAR(6) = NULL,-- rango de categoría
    @sCo_Movimiento CHAR(4) = NULL,                                  -- filtra a un solo tipo (ver tabla abajo); NULL = todos
    @sCo_Sucursal CHAR(6) = NULL
    )
RETURNS TABLE
```

## Columnas devueltas
| Columna | Significado |
|---|---|
| `co_art` | Artículo. |
| `co_alma` | Almacén afectado por esta línea de movimiento. |
| `tipo` | Código de sub-tipo de movimiento (ver tabla de ramas abajo) — más granular que `@sCo_Movimiento`. |
| `doc_num` | Número del documento origen (factura, ajuste, traslado, etc., según `tipo`). |
| `reng_num` | Número de línea dentro del documento origen. |
| `co_cliprov` | Cliente o proveedor asociado, cuando aplica (vacío en ajustes/traslados). |
| `fecha` | Fecha del movimiento (fecha de negocio del documento, no de inserción). |
| `total_entrada` | Cantidad que **entró** al almacén en esta línea, ya convertida a unidad base (`dbo.ArtUnidadBase`). `0.00` si la línea es una salida o si el documento está anulado. |
| `total_salida` | Cantidad que **salió** del almacén en esta línea, misma lógica. |
| `anulado` | Estado del documento origen. **La función NO filtra por este campo** — el consumidor debe hacerlo (`WHERE anulado = 0`), aunque cuando `anulado=1` los propios `total_entrada`/`total_salida` ya vienen en 0.00, así que sumarlos sin filtrar no distorsiona un total acumulado, pero sí puede confundir un listado línea por línea. |
| `rowguidR` / `rowguidE` | GUID de la línea / del encabezado del documento origen — útil para navegar de vuelta al documento exacto (p. ej. de una línea `AJUS` a su fila en `saAjusteReng`). |
| `fe_us_in` | Fecha de inserción del registro (para desempate de orden dentro del mismo día). |

## Las 12 ramas (`UNION ALL`), qué tabla origina cada una y cuándo aplica
| `tipo` | Filtro `@sCo_Movimiento` | Tabla origen | Sentido | Notas |
|---|---|---|---|---|
| `COMP` | `'COMP'` | `saFacturaCompraReng` + `saFacturaCompra` | Entrada | Compras facturadas directamente (sin nota de recepción previa). |
| `FACT` | `'FACT'` | `saFacturaVentaReng` + `saFacturaVenta` | Salida | Ventas facturadas. Excluye líneas que ya se descontaron por una nota de entrega previa (`R.tipo_doc <> 'NENT'`) — evita doble conteo. Filtra `co_alma` por línea, fecha por `fec_emis`. |
| `NREC` | (no filtrable individualmente vía `@sCo_Movimiento`, aparece como `'NREC'`) | Notas de recepción de compra | Entrada | Mercancía recibida físicamente antes de facturar. |
| `NENT` | — | Notas de entrega de venta | Salida | Mercancía despachada antes de facturar — es la que la rama `FACT` excluye para no duplicar. |
| `DCLI` | — | Devoluciones de cliente | Entrada | Mercancía que vuelve del cliente. |
| `DPRO` | — | Devoluciones a proveedor | Salida | Mercancía devuelta al proveedor. |
| `AJUS` | `'AJUS'` | `saAjusteReng` + `saAjuste` + `saTipoAjuste` | Entrada o Salida según `saTipoAjuste.tipo_trans` | **Esta es la rama que reflejará los ajustes creados por el módulo nuevo.** Usa `ST.tipo_trans='0'` → entrada, `='1'` → salida — exactamente la misma tabla y misma columna que gobierna `pStockActualizar`. |
| `TRA1` | `'TRAS'` | `saTrasladoReng` + `saTraslado`, almacén = `alm_orig` | Salida | Traslado: salida del almacén origen. |
| `TRA2` | `'TRAS'` | ídem, almacén = `alm_tmp` | Entrada | Traslado: entrada al almacén temporal/tránsito. |
| `TRA3` | `'TRAS'` | ídem, almacén = `alm_tmp` | Salida | Traslado: salida del almacén temporal (cuando se completa la recepción). |
| `TRA4` | — | ídem, presumible almacén destino | Entrada | Traslado: entrada al almacén destino final. |
| `GCOM` | — | Giro de compra (relacionado a `saGiroCompra`) | — | Movimiento contable/documental de compra, revisar caso de uso puntual antes de incluir en cálculos de stock físico. |
| `GCOR` | — | Similar a `GCOM`, variante | — | Idem. |

**Nota importante sobre `@sCo_Movimiento`**: el parámetro solo tiene ramas explícitas para `'COMP'`, `'FACT'`, `'AJUS'` y `'TRAS'` (agrupa `TRA1`-`TRA4`); las demás ramas (`NREC`, `NENT`, `DCLI`, `DPRO`, `GCOM`, `GCOR`) no comprueban el parámetro y **siempre se incluyen** salvo que se filtre después por la columna `tipo` del resultado.

## Recomendación de uso para el módulo de Inventario nuevo
1. **Gráfico de evolución de inventario**: llamar sin `@sCo_Movimiento` (todas las ramas), filtrar `anulado=0`, agrupar por fecha (día/semana) y calcular saldo corrido = stock inicial (vía `dbo.ConsultarStockActualxAlmacenxFecha`) + `SUM(total_entrada - total_salida)` acumulado hasta cada fecha.
2. **Cálculo de "consumo reciente" / velocidad de agotamiento**: para artículos de tipo `M` (materia prima) o `V` (producto terminado/venta), sumar `total_salida` de las ramas `FACT` y `AJUS` (con `tipo_trans='1'`) en una ventana de N días (p. ej. últimos 30), dividir entre N para obtener consumo diario promedio, y proyectar `stock_actual / consumo_diario_promedio` como "días restantes". Las ramas de traslado (`TRA1`-`TRA4`) no deben contarse como consumo real — son movimiento interno entre almacenes, no salida del negocio.
3. Dado que esta base de datos (`Ncake_a`) no usa lotes ni seriales (`maneja_lote=0` y `maneja_serial=0` en los 166 artículos existentes), no hace falta considerar las ramas de lote/serial de otras funciones hermanas (`RepMovimientoInventarioxArticuloXlote`, `...xSeriales`) para la v1 del módulo.

## Tablas Referenciadas
`saFacturaCompra(Reng)`, `saFacturaVenta(Reng)`, `saNotaRecepcionCompra(Reng)`, `saNotaEntregaVenta(Reng)`, `saDevolucionCliente(Reng)`, `saDevolucionProveedor(Reng)`, [`saAjuste`](../tables/saAjuste.md), [`saAjusteReng`](../tables/saAjusteReng.md), [`saTipoAjuste`](../tables/saTipoAjuste.md), `saTraslado(Reng)`, `saGiroCompra(Reng)`, `saArticulo`. Funciones: `dbo.ArtUnidadBase`, `dbo.fechasimple`.

## Recetario SQL de Negocio
```sql
-- Consumo diario promedio (últimos 30 días) por artículo, solo ventas + salidas de ajuste,
-- para alimentar la señal de "se agota rápido" del módulo de Inventario
SELECT
    m.co_art, art.art_des,
    SUM(m.total_salida) AS salida_total_30d,
    SUM(m.total_salida) / 30.0 AS consumo_diario_prom
FROM dbo.MovimientoInventario(NULL, NULL, DATEADD(day, -30, GETDATE()), GETDATE(), '14', NULL, NULL, NULL, NULL, NULL, NULL) m
INNER JOIN saArticulo art ON art.co_art = m.co_art
WHERE m.anulado = 0
  AND m.tipo IN ('FACT', 'AJUS')
GROUP BY m.co_art, art.art_des
HAVING SUM(m.total_salida) > 0
ORDER BY consumo_diario_prom DESC;

-- Serie de tiempo para el gráfico de evolución de stock de un artículo en un almacén
SELECT fecha, tipo, total_entrada, total_salida,
       SUM(total_entrada - total_salida) OVER (ORDER BY fecha, fe_us_in ROWS UNBOUNDED PRECEDING) AS saldo_corrido
FROM dbo.MovimientoInventario('0000063','0000063', '2026-01-01', GETDATE(), '14', NULL, NULL, NULL, NULL, NULL, NULL)
WHERE anulado = 0
ORDER BY fecha, fe_us_in;
```
