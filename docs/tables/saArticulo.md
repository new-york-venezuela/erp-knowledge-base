# Tabla: saArticulo
**Módulo**: Inventario
**Descripción de Negocio**: Catálogo maestro de artículos (mercancía, materia prima, servicios, envases). Tabla de referencia central para todo movimiento de inventario, facturación y compras. Define clasificación, impuestos, stock mín/máx, manejo de seriales/lotes y márgenes. Verificado contra `sys.columns` + `MS_Description` en vivo (base `Ncake_a`) — el listado previo estaba truncado a 40 columnas; esta tabla tiene 64.

## Campos Clave (verificado en vivo, 64 columnas)
| Campo | Tipo | Nulo | Descripción de Negocio (MS_Description) | Relación |
|---|---|---|---|---|
| `co_art` | char(30) | NOT NULL | Código del artículo (PK) | Clave Primaria |
| `fecha_reg` | smalldatetime | NOT NULL | Fecha en que se registra la información | — |
| `art_des` | varchar(120) | NOT NULL | Descripción del artículo (nombre visible) | — |
| `tipo` | char(1) | NOT NULL | `V`=Venta, `C`=Consumo, `S`=Servicio, `F`=Fabricación, `M`=Materia Prima, `N`=Material de envase, `E`=Material de empaque | — |
| `anulado` | bit | NOT NULL | `1` = artículo inactivo/eliminado | — |
| `fecha_inac` | smalldatetime | NULL | Fecha en la que fue inhabilitado el producto | — |
| `co_lin` | char(6) | NOT NULL | Código de Línea | FK Implícita → `saLineaArticulo.co_lin` |
| `co_subl` | char(6) | NOT NULL | Código de Sub Línea | FK Implícita → `saSubLinea.(co_lin, co_subl)` |
| `co_cat` | char(6) | NOT NULL | Código de Categoría | FK Implícita → `saCatArticulo.co_cat` |
| `co_color` | char(6) | NOT NULL | Código del color relacionado con el artículo | FK Implícita → `saColor.co_color` |
| `co_ubicacion` | char(6) | NOT NULL | Ubicación del artículo | FK Implícita → `saUbicacion` |
| `cod_proc` | char(6) | NULL | Código de procedencia | FK Implícita → `saProcedencia.co_proc` |
| `item` | char(10) | NULL | Correlativo de clasificación al cual pertenece el artículo | — |
| `modelo` | varchar(20) | NULL | Modelo — codificación alterna del artículo | — |
| `ref` | varchar(20) | NULL | Referencia — codificación alterna del artículo | — |
| `generico` | bit | NOT NULL | `1` = artículo genérico | — |
| `maneja_serial` | bit | NOT NULL | `1` = requiere número de serial en entradas/salidas | — |
| `maneja_lote` | bit | NOT NULL | `1` = maneja lotes | — |
| `maneja_lote_venc` | bit | NOT NULL | `1` = lotes con fecha de vencimiento | — |
| `margen_min` | decimal(18,2) | NOT NULL | Porcentaje del margen mínimo | — |
| `margen_max` | decimal(18,2) | NOT NULL | Porcentaje del margen máximo | — |
| `tipo_imp` | char(1) | NOT NULL | Tipo impuesto (1): `1`=Tasa General, `2`=A1, `3`=A2, `4`=A3, `5`=Ventas Exentas, `6`=Compras Exentas, `7`=Exentos | FK → `saImpuesto` |
| `tipo_imp2` | char(1) | NULL | Tipo impuesto (2), mismo dominio | — |
| `tipo_imp3` | char(1) | NULL | Tipo impuesto (3), mismo dominio | — |
| `co_reten` | char(6) | NULL | Código de concepto de I.S.L.R. | FK → `saConISLR.co_islr` |
| `garantia` | varchar(30) | NOT NULL | Garantía | — |
| `volumen` | decimal(18,5) | NOT NULL | Volumen | — |
| `peso` | decimal(18,5) | NOT NULL | Peso | — |
| `stock_min` | decimal(18,5) | NOT NULL | **Stock mínimo a mantener (umbral de reorden bajo)** | — |
| `stock_max` | decimal(18,5) | NOT NULL | **Stock máximo a mantener** | — |
| `stock_pedido` | decimal(18,5) | NOT NULL | **Punto de stock para hacer reposiciones (cantidad de reorden sugerida)** | — |
| `relac_unidad` | int | NOT NULL | `0`=maneja 1+ unidades con relación entre sí, `1`=maneja 2 unidades sin relación | — |
| `punt_ven` | decimal(18,2) | NOT NULL | Puntaje de fidelidad para el vendedor | — |
| `punt_cli` | decimal(18,2) | NOT NULL | Puntaje de fidelidad para el cliente | — |
| `lic_mon_ilc` | decimal(18,2) | NOT NULL | Monto del impuesto sobre licores | — |
| `lic_capacidad` | decimal(18,3) | NOT NULL | Capacidad del licor | — |
| `lic_grado_al` | decimal(10,2) | NOT NULL | Grado alcohólico | — |
| `lic_tipo` | char(1) | NULL | Tipo de licor | — |
| `prec_om` | bit | NOT NULL | `1` = precios manejados en otra moneda (USD) | — |
| `comentario` | varchar(MAX) | NULL | Comentario libre | — |
| `tipo_cos` | char(4) | NULL | Método de costeo para margen: `1`=Último Costo, `2`=Costo Promedio, `3`=Último Costo OM, `4`=Costo Promedio OM, `5`=Reposición, `6`=Proveedor | — |
| `porc_margen_minimo` | decimal(18,2) | NOT NULL | Monto comisión (nombre de campo engañoso, ver `mont_comi`) | — |
| `porc_margen_maximo` | decimal(18,2) | NOT NULL | (sin descripción en origen) | — |
| `mont_comi` | decimal(18,2) | NOT NULL | Monto comisión | — |
| `porc_arancel` | decimal(18,2) | NOT NULL | Porcentaje de arancel | — |
| `numcom` | int | NULL | Info. Contable: número de comprobante de contabilidad asociado | — |
| `feccom` | smalldatetime | NULL | Info. Contable: fecha de procesamiento en contabilidad | — |
| `dis_cen` | xml | NULL | Info. Contable: cuenta contable / distribución de centro de costo (XML) | — |
| `reten_iva_tercero` | char(16) | NULL | Código del proveedor al cual se aplica retención IVA a terceros | FK → `saProveedor` |
| `campo1`…`campo8` | varchar(60) | NULL | Campos personalizables adicionales | — |
| `co_us_in` | char(6) | NOT NULL | Usuario que ingresó el registro | — |
| `co_sucu_in` | char(6) | NULL | Sucursal donde fue ingresado | — |
| `fe_us_in` | datetime | NOT NULL | Fecha de inserción | — |
| `co_us_mo` | char(6) | NOT NULL | Usuario de última modificación | — |
| `co_sucu_mo` | char(6) | NULL | Sucursal de última modificación | — |
| `fe_us_mo` | datetime | NOT NULL | Fecha de última modificación | — |
| `revisado` | char(1) | NULL | Reservado por el sistema (replicación) | — |
| `trasnfe` | char(1) | NULL | Reservado por el sistema (transferencia multiempresa) | — |
| `validador` | timestamp | NOT NULL | Control de concurrencia optimista | — |
| `rowguid` | uniqueidentifier | NOT NULL | Identificador único (usado como FK lógica desde `saCostoHistoricoSalida.cod_articulo_rowguid`) | — |
| `aux_imp01` | decimal(18,5) | NULL | Auxiliar usado en migración para traer último costo | — |

## Campos seguros para edición rápida (módulo de Inventario propuesto)
**Editables sin riesgo** (descriptivos, sin impacto contable/fiscal/precio):
- `art_des` (nombre/descripción — el más solicitado)
- `ref`, `modelo` (referencias alternas)
- `comentario`
- `campo1`…`campo8` (campos libres, uso variable por instalación)
- `stock_min`, `stock_max`, `stock_pedido` (umbrales de reorden — habilitado por decisión de producto: el gerente de inventario ajusta sus propias alertas sin depender de Compras)

**NO editar desde este módulo** (impacto cruzado en Ventas/Compras/POS/Fiscal):
- Cualquier campo de precio (vive en `saArtPrecio`, tabla aparte)
- `tipo_imp`, `tipo_imp2`, `tipo_imp3`, `co_reten`, `reten_iva_tercero` (fiscal)
- `tipo_cos`, `margen_min`, `margen_max`, `porc_margen_minimo`, `porc_margen_maximo`, `mont_comi`, `porc_arancel` (costeo/comisiones)
- `co_lin`, `co_subl`, `co_cat` (clasificación — cambiar esto reclasifica el artículo en reportes de todos los módulos; fuera de alcance)
- `maneja_serial`, `maneja_lote`, `maneja_lote_venc` (cambia el comportamiento transaccional en todo el sistema)
- `anulado` (dar de baja un artículo es decisión de Procurement/Administración, no de Inventario)

## Triggers Relacionados
- `TrigEstado_saArticulo` (ON INSERT, UPDATE): si `anulado` cambia de valor respecto a la fila anterior, inserta una fila en `saHistoricoEstado`. **Verificado: no bloquea ni valida nada más** — es seguro hacer `UPDATE` directo sobre los campos descriptivos listados arriba; el trigger sólo reacciona a cambios en `anulado`, que este módulo no debe tocar.

## Datos reales observados (base `Ncake_a`, producción — panadería/repostería "Alimentos New York")
- 166 artículos activos (`anulado=0`) de 5 tipos: V=65 (venta/producto terminado), M=52 (materia prima), S=29 (servicio), C=12 (consumo), E=8 (empaque).
- **0 artículos usan `maneja_lote`, `maneja_serial` o `maneja_lote_venc`** en esta instalación — el módulo de Inventario NO necesita soportar UI de lotes/seriales en v1.

## Relaciones Clave
- **Stock por almacén**: `saStockAlmacen` (co_art) — ver nota de uso real en ese documento
- **Precios**: `saArtPrecio` (co_art) — fuera de alcance para edición
- **Facturas de venta**: `saFacturaVentaReng.co_art`
- **Facturas de compra**: `saFacturaCompraReng.co_art`
- **Ajustes de inventario**: `saAjusteReng.co_art`
- **Histórico de salidas**: `saCostoHistoricoSalida.cod_articulo_rowguid` → `saArticulo.rowguid`

## Recetario SQL de Negocio
```sql
-- Artículos con stock bajo mínimo (sólo tiene sentido en almacenes que SÍ llevan stock, ver saStockAlmacen)
SELECT a.co_art, a.art_des, s.co_alma,
       s.stock, a.stock_min, a.stock_pedido,
       a.stock_min - s.stock AS deficit
FROM saArticulo a
INNER JOIN saStockAlmacen s ON a.co_art = s.co_art
WHERE s.stock < a.stock_min AND a.anulado = 0
ORDER BY deficit DESC;

-- Quick-edit seguro: sólo campos descriptivos + umbrales
UPDATE saArticulo
SET art_des = @art_des, ref = @ref, comentario = @comentario,
    stock_min = @stock_min, stock_max = @stock_max, stock_pedido = @stock_pedido,
    co_us_mo = @usuario, fe_us_mo = GETDATE()
WHERE co_art = @co_art;
```
