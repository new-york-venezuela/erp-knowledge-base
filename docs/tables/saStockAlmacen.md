# Tabla: saStockAlmacen
**Módulo**: Inventario
**Descripción de Negocio**: Stock actual por almacén y artículo. Tabla de 7 columnas, desnormalizada por diseño para máxima velocidad de lectura. Es el balance de inventario en tiempo real: cada `(co_alma, co_art)` tiene exactamente una fila. Los movimientos de entrada/salida la actualizan vía procedimientos almacenados (ver `pStockActualizar`) — **no tiene triggers propios** (verificado: 0 triggers en `sys.triggers` para esta tabla), por lo que cualquier proceso que la modifique debe llamar explícitamente al SP correspondiente; un `UPDATE` directo no dispara efectos secundarios pero tampoco los reemplaza (ej. no crea el registro histórico en `saCostoHistoricoEntrada/Salida`). Para histórico usar `saCostoHistoricoEntrada`/`saCostoHistoricoSalida`.

## Campos Clave
| Campo | Tipo | Nulo | Descripción de Negocio | Relación |
|---|---|---|---|---|
| `co_alma` | char | NOT NULL | Código del almacén (PK con co_art) | FK → `saAlmacen.co_alma` |
| `co_art` | char | NOT NULL | Código del artículo (PK con co_alma) | FK → `saArticulo.co_art` |
| `tipo` | char | NULL | Tipo de stock: `E`=existencia, `A`=apartado | — |
| `stock` | decimal | NULL | **Cantidad en existencia actual** | — |
| `revisado` | char | NULL | Flag de sincronización replicación | — |
| `trasnfe` | char | NULL | Flag de transferencia multiempresa | — |
| `validador` | timestamp | NULL | Timestamp para control de concurrencia optimista | — |

## ⚠️ Uso real observado (base `Ncake_a`, producción) — ver también `saAlmacen.md`
- **92 filas totales**, pero stock positivo (`stock > 0`) sólo en **2 almacenes**: `13` (Gastos/Administrativos — 16 artículos, insumos de oficina/limpieza) y `14` (Materia Prima/Urbina — 45 artículos, ingredientes: harina, aceite, avena, esencias).
- El almacén de ventas (`000015`, "OFICINA"), donde se registran las 4710 líneas de `saFacturaVentaReng`, **no aparece con stock positivo aquí** — el producto terminado no se controla por inventario formal en esta instalación (operación make-to-order de panadería).
- **Conclusión para el módulo**: el "inventario que evoluciona en el tiempo" y las "alertas de stock bajo" tienen sentido de negocio real sobre materia prima/insumos (almacenes 13 y 14), no sobre producto terminado. Diseñar el dashboard y las alertas alrededor de esos ~61 artículos activos con stock, no sobre el catálogo completo de 166.

## Recetario SQL de Negocio
```sql
-- Inventario valorizado al costo promedio
SELECT
    s.co_alma, al.des_alma,
    s.co_art, a.art_des, a.co_lin,
    s.stock,
    s.stock * ISNULL(cp.costo_prom, 0)         AS valor_bs,
    s.stock * ISNULL(cp.costo_prom, 0)
        / NULLIF((SELECT TOP 1 tasa_v FROM saTasa
                  WHERE co_mone='USD' ORDER BY fecha DESC), 0) AS valor_usd
FROM saStockAlmacen s
INNER JOIN saArticulo a ON s.co_art = a.co_art
INNER JOIN saAlmacen al ON s.co_alma = al.co_alma
LEFT JOIN (
    SELECT co_art, co_alma, AVG(cost_unit) AS costo_prom
    FROM saFacturaCompraReng fcr
    INNER JOIN saFacturaCompra fc ON fcr.doc_num = fc.doc_num
    WHERE fc.anulado = 0
    GROUP BY co_art, co_alma
) cp ON cp.co_art = s.co_art AND cp.co_alma = s.co_alma
WHERE s.stock > 0 AND a.anulado = 0
ORDER BY s.co_alma, a.co_lin, a.co_art;

-- Artículos que efectivamente se gestionan en este módulo (almacenes con stock real)
SELECT s.co_alma, s.co_art, a.art_des, s.stock, a.stock_min, a.stock_pedido
FROM saStockAlmacen s
JOIN saArticulo a ON a.co_art = s.co_art
WHERE s.co_alma IN ('13    ', '14    ') AND a.anulado = 0
ORDER BY s.co_alma, a.art_des;
```
