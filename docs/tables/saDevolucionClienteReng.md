# Tabla: saDevolucionClienteReng
**Módulo**: Ventas
**Descripción de Negocio**: Renglones (líneas de detalle) de devoluciones de cliente. Cada fila es un artículo devuelto dentro de un documento de `saDevolucionCliente`, con su cantidad, precio y prorrateo de impuestos/descuentos — mismo patrón estructural que `saFacturaVentaReng`. Se une a `saDevolucionCliente` por `doc_num`. **No verificado en vivo** — descripción derivada del esquema de columnas y por analogía estructural con `saFacturaVentaReng`.

⚠️ **Sin motivo de devolución a nivel de renglón tampoco**: igual que en el encabezado (`saDevolucionCliente.md`), no hay columna de razón/motivo codificada; sólo `comentario` (texto libre, opcional). `tipo_doc`/`num_doc`/`rowguid_doc` permiten rastrear el documento de origen que se está devolviendo (normalmente `FACT`), pero no el porqué.

## Campos
| Campo | Tipo | Nulo | Descripción | Relación |
|---|---|---|---|---|
| `reng_num` | int(10,0) | NOT NULL | b'Numero de Renglon' | — |
| `doc_num` | char(20) | NOT NULL | b'Numero de documento' | FK → `saDevolucionCliente.doc_num` |
| `co_art` | char(30) | NOT NULL | b'Codigo del articulo' | FK → `saArtUnidad.co_art` |
| `des_art` | varchar(120) | NULL | b'Descripcion adicional del articulo' | — |
| `co_alma` | char(6) | NOT NULL | b'Codigo del almacen' | FK → `saAlmacen.co_alma` |
| `total_art` | decimal(18,5) | NOT NULL | b'Total art\xc3\xadculos del documento en encabezados o total de art\xc3\xadculos comprados o vendidos en renglones' | — |
| `stotal_art` | decimal(18,5) | NOT NULL | b'Total art\xc3\xadculos (en unidad secundaria) del documento en encabezados o total de art\xc3\xadculos comprados o vendidos en renglones' | — |
| `co_uni` | char(6) | NOT NULL | b'Codigo de la unidad' | FK → `saArtUnidad.co_uni` |
| `sco_uni` | char(6) | NULL | b'Codigo de la unidad secundaria' | FK → `saArtUnidad.co_uni` |
| `co_precio` | char(6) | NULL | b'Codigo del tipo de precio' | — |
| `prec_vta` | decimal(18,5) | NOT NULL | b'Precio de venta o compra' | — |
| `prec_vta_om` | decimal(18,5) | NULL | b'Reservado para futuras implementaciones' | — |
| `porc_desc` | varchar(15) | NULL | b'Porcentaje de descuento' | — |
| `monto_desc` | decimal(18,5) | NOT NULL | b'Monto del descuento aplicado' | — |
| `tipo_imp` | char(1) | NOT NULL | b'Tipo de impuesto (1) aplicado' | — |
| `tipo_imp2` | char(1) | NULL | b'Tipo de impuesto (2) aplicado' | — |
| `tipo_imp3` | char(1) | NULL | b'Tipo de impuesto (3) aplicado' | — |
| `porc_imp` | decimal(18,5) | NOT NULL | b'Porcentaje de impuesto (1) aplicado' | — |
| `porc_imp2` | decimal(18,5) | NOT NULL | b'Porcentaje de impuesto (2) aplicado' | — |
| `porc_imp3` | decimal(18,5) | NOT NULL | b'Porcentaje de impuesto (3) aplicado' | — |
| `monto_imp` | decimal(18,5) | NOT NULL | b'Monto de impuesto (1) aplicado' | — |
| `monto_imp2` | decimal(18,5) | NOT NULL | b'Monto de impuesto (2) aplicado' | — |
| `monto_imp3` | decimal(18,5) | NOT NULL | b'Monto de impuesto (3) aplicado' | — |
| `reng_neto` | decimal(18,2) | NOT NULL | b'Monto neto del renglon' | — |
| `pendiente` | decimal(18,5) | NOT NULL | b'Cantidad pendiente por exportar a otros documentos' | — |
| `pendiente2` | decimal(18,5) | NOT NULL | b'Reservado para futruras implementaciones' | — |
| `tipo_doc` | char(4) | NULL | b'Tipo documento de origen, FACT: Factura de Venta, NENT: Nota de Entrega, DCLI: Devolucion de Cliente, COMP: Factura de Compra, NREC: Nota de Recepcion, DPRO: Devolucion a Proveedor OCOM: Orden de Compra, CPRO: Cotizacion de Compra, PCOM: Plantilla de Compra, PCLI: Pedido de CLiente, CCLI: Cotizacion a Cliente,NDES: Nota de Despacho, PVEN: Plantilla de Venta, AJUE: Ajuste de Entrada, AJUS: Ajuste de Salida, TRAE: Traslado de Entrada, TRAS: Traslado de Salida, GCOM: Generacion de Compuesto, RGEN: Renglones de Compuesto' | — |
| `num_doc` | varchar(20) | NULL | b'Numero de documento del cual fue importado (referencia, usar rowguid_doc)' | — |
| `rowguid_doc` | uniqueidentifier | NULL | b'identificador del renglon importado' | — |
| `total_dev` | decimal(18,5) | NOT NULL | b'Cantidad devuelta' | — |
| `monto_dev` | decimal(18,5) | NOT NULL | b'Reservado para futuras implementaciones' | — |
| `otros` | decimal(18,5) | NOT NULL | b'Monto correspondiente a otros' | — |
| `comentario` | varchar(max) | NULL | b'Comentario' | — |
| `lote_asignado` | bit(1,0) | NOT NULL | b'Posee asignado informacion de lotes' | — |
| `dis_cen` | xml | NULL | b'Informacion Contable: cuenta contable, cuenta de gasto, distribucion de centro de costo (formato XML)' | — |
| `monto_desc_glob` | decimal(18,5) | NOT NULL | b'Monto de descuento global' | — |
| `monto_reca_glob` | decimal(18,5) | NOT NULL | b'Monto correspondiente al recargo global' | — |
| `otros1_glob` | decimal(18,5) | NOT NULL | b'Monto correspondiente a otros 1 global' | — |
| `otros2_glob` | decimal(18,5) | NOT NULL | b'Monto correspondiente a otros 2 global' | — |
| `otros3_glob` | decimal(18,5) | NOT NULL | b'Monto correspondiente a otros 3 global' | — |
| `monto_imp_afec_glob` | decimal(18,5) | NOT NULL | b'Monto correspondiente impuesto 1 global' | — |
| `monto_imp2_afec_glob` | decimal(18,5) | NOT NULL | b'Monto correspondiente impuesto 2 global' | — |
| `monto_imp3_afec_glob` | decimal(18,5) | NOT NULL | b'Monto correspondiente impuesto 3 global' | — |
| `co_us_in` | char(6) | NOT NULL | b'Codigo del usuario que ingreso el registro' | — |
| `co_sucu_in` | char(6) | NULL | b'Codigo de la sucursal donde fue ingresado el registro' | — |
| `fe_us_in` | datetime(23,3) | NOT NULL | b'Fecha de insercion del registro' | — |
| `co_us_mo` | char(6) | NOT NULL | b'Codigo del usuario que hizo la ultima modificaci\xc3\xb3n en el registro' | — |
| `co_sucu_mo` | char(6) | NULL | b'Codigo de la sucursal donde fue modificado por ultima vez el registro' | — |
| `fe_us_mo` | datetime(23,3) | NOT NULL | b'Fecha de la ultima modificacion del registro' | — |
| `revisado` | char(1) | NULL | b'Reservado por el sistema' | — |
| `trasnfe` | char(1) | NULL | b'Reservado por el sistema' | — |
| `rowguid` | uniqueidentifier | NOT NULL | b'Identificador Unico' | — |

## Triggers Relacionados
_Ninguno_

## Foreign Keys (explícitas)
- `FK_saDevolucionClienteReng_saAlmacen`: `co_alma` → `saAlmacen.co_alma`
- `FK_saDevolucionClienteReng_saArtUnidad`: `co_art` → `saArtUnidad.co_art`
- `FK_saDevolucionClienteReng_saArtUnidad`: `co_uni` → `saArtUnidad.co_uni`
- `FK_saDevolucionClienteReng_saArtUnidadSecundaria`: `co_art` → `saArtUnidad.co_art`
- `FK_saDevolucionClienteReng_saArtUnidadSecundaria`: `sco_uni` → `saArtUnidad.co_uni`
- `FK_saDevolucionClienteReng_saDevolucionCliente`: `doc_num` → `saDevolucionCliente.doc_num`

## Relaciones Clave
- **Encabezado**: `saDevolucionCliente` (JOIN por `doc_num`)
- **Renglón de factura original devuelto**: `num_doc`/`rowguid_doc` → apunta al renglón de origen (normalmente `saFacturaVentaReng`, cuando `tipo_doc='FACT'`)
- **Artículo**: `saArticulo` vía `co_art` (nota: la FK explícita apunta a `saArtUnidad`, tabla intermedia de unidades por artículo — para el catálogo maestro usar `saArticulo.co_art`)

## Recetario SQL de Negocio (no verificado en vivo — inferido por analogía con saFacturaVentaReng)
```sql
-- Artículos más devueltos del mes (en unidades y Bs)
SELECT
    r.co_art, a.art_des,
    SUM(r.total_art)  AS cant_devuelta,
    SUM(r.reng_neto)  AS monto_bs
FROM saDevolucionClienteReng r
INNER JOIN saDevolucionCliente d ON r.doc_num = d.doc_num
LEFT JOIN  saArticulo a          ON r.co_art  = a.co_art
WHERE d.fec_emis BETWEEN '2024-01-01' AND '2024-01-31'
  AND d.anulado = 0
GROUP BY r.co_art, a.art_des
ORDER BY monto_bs DESC;
```
