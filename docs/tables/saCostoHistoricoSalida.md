# Tabla: saCostoHistoricoSalida
**Módulo**: Inventario
**Descripción de Negocio**: Historial de TODAS las salidas de inventario (ventas, ajustes de salida, traslados de salida, generación de compuestos) con su costo. Es la fuente de verdad para reconstruir movimientos pasados de stock — a diferencia de `saStockAlmacen` (sólo el balance actual), esta tabla es un log append-only. Verificado en vivo vía `sys.columns` + `MS_Description`; reemplaza doc previo incompleto (dump crudo sin síntesis).

## Campos Clave (verificado en vivo, 10 columnas)
| Campo | Tipo | Nulo | Descripción de Negocio | Relación |
|---|---|---|---|---|
| `cod_costo_historico_salida` | uniqueidentifier | NOT NULL | Identificador único del registro de salida (PK) | — |
| `cod_costo_historico_entrada` | uniqueidentifier | NULL | Enlaza a la entrada que originó el costo consumido (costeo FIFO/PEPS) | FK → `saCostoHistoricoEntrada.cod_costo_historico_entrada` |
| `cod_articulo_rowguid` | uniqueidentifier | NOT NULL | Identificador único del artículo relacionado | FK → `saArticulo.rowguid` (NO `co_art` — usa el GUID, no el código) |
| `doc_orig` | uniqueidentifier | NOT NULL | Identificador único del registro origen del movimiento (rowguid en la tabla indicada por `tipo_doc`) | FK dinámica según `tipo_doc` |
| `costo_pro` | decimal | NOT NULL | Costo promedio al momento de la salida | — |
| `cantidad` | decimal | NOT NULL | **Cantidad que salió** | — |
| `tipo_doc` | char | NOT NULL | Tipo de documento origen: `FACT`=Factura Venta, `NENT`=Nota Entrega, `DCLI`=Devolución Cliente, `NDES`=Nota Despacho, `AJUS`=Ajuste de Salida, `TRAS`=Traslado de Salida, `RGEN`=Renglón de Compuesto, entre otros (mismo dominio que `saFacturaVentaReng.tipo_doc`) | — |
| `fecha_emision` | datetime | NOT NULL | **Fecha del documento asociado a la salida — columna clave para análisis de velocidad de consumo** | — |
| `cod_almacen` | char | NOT NULL | Código del almacén de la salida | FK → `saAlmacen.co_alma` |
| `validador` | timestamp | NOT NULL | Control de concurrencia optimista | — |

**No tiene columna `anulado`** — a diferencia de `saFacturaVenta`, este historial no se filtra por anulación directamente; si se necesita excluir movimientos de documentos anulados, hay que unir contra la tabla origen (ej. `saFacturaVenta.anulado`) usando `doc_orig`.

## Uso recomendado: fuente de datos para "consumo rápido / próximo a agotarse"
Esta tabla es la mejor fuente para calcular velocidad de consumo por artículo/almacén porque:
1. Ya está filtrada a movimientos de salida (no hay que distinguir entradas/salidas como en `saFacturaVentaReng`, que mezcla ambos vía `tipo_doc`).
2. Incluye TODAS las causas de salida (ventas, mermas, ajustes, traslados), dando una vista completa de consumo real — no sólo ventas.
3. Tiene `cod_almacen`, permitiendo el cálculo por almacén (relevante dado que sólo 2 almacenes llevan stock real, ver `saAlmacen.md`).

**Gotcha**: usa `cod_articulo_rowguid` (GUID), no `co_art` — requiere join contra `saArticulo.rowguid`, no contra `saArticulo.co_art` directamente.

Forma de la consulta recomendada para "días de stock restantes":
```sql
-- Consumo diario promedio (últimos 30 días) por artículo/almacén, comparado con stock actual
WITH consumo AS (
    SELECT a.co_art, h.cod_almacen,
           SUM(h.cantidad) / 30.0 AS consumo_diario_promedio
    FROM saCostoHistoricoSalida h
    JOIN saArticulo a ON a.rowguid = h.cod_articulo_rowguid
    WHERE h.fecha_emision >= DATEADD(DAY, -30, GETDATE())
    GROUP BY a.co_art, h.cod_almacen
)
SELECT s.co_alma, s.co_art, ar.art_des, s.stock,
       c.consumo_diario_promedio,
       CASE WHEN c.consumo_diario_promedio > 0
            THEN s.stock / c.consumo_diario_promedio
            ELSE NULL END AS dias_restantes
FROM saStockAlmacen s
JOIN saArticulo ar ON ar.co_art = s.co_art
LEFT JOIN consumo c ON c.co_art = s.co_art AND c.cod_almacen = s.co_alma
WHERE s.co_alma IN ('13    ', '14    ') AND ar.anulado = 0
ORDER BY dias_restantes ASC;
```
**Nota de calibración**: con sólo 4608 filas históricas totales en esta tabla (toda la vida del sistema) y una operación de 61 artículos activos con stock, una ventana de 30 días puede tener muy pocos puntos de datos por artículo para insumos de compra poco frecuente (ej. equipo de oficina). Considerar una ventana más larga (60-90 días) o un mínimo de N movimientos antes de mostrar una proyección de "días restantes", para evitar alertas falsas por datos escasos.

## Triggers Relacionados
_Ninguno_

## Relaciones Clave
- `cod_articulo_rowguid` → `saArticulo.rowguid`
- `cod_almacen` → `saAlmacen.co_alma`
- `doc_orig` → tabla determinada por `tipo_doc` (ej. `saFacturaVenta.rowguid` si `tipo_doc='FACT'`)
- Tabla hermana: `saCostoHistoricoEntrada` (mismo patrón, para entradas — no verificada en este pase, pendiente si se requiere historial de compras/entradas para el mismo dashboard)
