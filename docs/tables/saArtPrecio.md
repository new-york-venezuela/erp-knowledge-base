# Tabla: saArtPrecio
**Módulo**: Inventario
**Descripción de Negocio**: Lista de precios vigentes y con vigencia histórica por artículo. Cada fila define el `monto` de un artículo (`co_art`) para un tipo de precio (`co_precio`, FK → `saTipoPrecio` — ej. contado, mayorista, distribuidor), opcionalmente restringido a un almacén específico (`co_alma`; `NULL` = todos los almacenes), con un rango de vigencia `desde`/`hasta`. Es la fuente de verdad de "precio de lista" — distinta del precio efectivo de venta (`saFacturaVentaReng.prec_vta`), que puede diferir por descuentos manuales o comisión aplicada en el momento de la factura. **No verificado en vivo** — descripción derivada del esquema de columnas y FKs explícitas.

**Nota de diseño**: el hecho de que `desde`/`hasta` definan vigencia significa que esta tabla ya funciona como un historial de precios de lista sin necesidad de replicarlo — útil para un dashboard de "Cost Volatility / Price Variance" que compare el precio de lista vigente contra el precio efectivamente facturado en `saFacturaVentaReng.prec_vta` a lo largo del tiempo.

## Campos
| Campo | Tipo | Nulo | Descripción | Relación |
|---|---|---|---|---|
| `co_art` | char(30) | NOT NULL | b'Codigo del articulo' | FK → `saArticulo.co_art` |
| `co_precio` | char(6) | NOT NULL | b'Codigo del tipo de precio' | FK → `saTipoPrecio.co_precio` |
| `co_alma_calculado` | char(6) | NOT NULL | b'Codigo del almacen o TODOS cuando aplica a todos los almacenes (Campo calculado)' | — |
| `desde` | datetime(23,3) | NOT NULL | b'Fecha inicial de vigencia del precio' | — |
| `hasta` | datetime(23,3) | NULL | b'Fecha final de vigencia de precio' | — |
| `co_alma` | char(6) | NULL | b'Codigo del almacen (null equivale a todos los almacenes)' | FK → `saAlmacen.co_alma` |
| `monto` | decimal(18,5) | NOT NULL | b'Monto del precio' | — |
| `montoadi1` | decimal(18,5) | NULL | b'Reservado para futuras implementaciones' | — |
| `montoadi2` | decimal(18,5) | NULL | b'Reservado para futuras implementaciones' | — |
| `montoadi3` | decimal(18,5) | NULL | b'Reservado para futuras implementaciones' | — |
| `montoadi4` | decimal(18,5) | NULL | b'Reservado para futuras implementaciones' | — |
| `montoadi5` | decimal(18,5) | NULL | b'Reservado para futuras implementaciones' | — |
| `precioOm` | bit(1,0) | NOT NULL | b'Reservado para futuras implementaciones' | — |
| `co_us_in` | char(6) | NOT NULL | b'Codigo del usuario que ingreso el registro' | — |
| `co_sucu_in` | char(6) | NULL | b'Codigo de la sucursal donde fue ingresado el registro' | — |
| `fe_us_in` | datetime(23,3) | NOT NULL | b'Fecha de insercion del registro' | — |
| `co_us_mo` | char(6) | NOT NULL | b'Codigo del usuario que hizo la ultima modificaci\xc3\xb3n en el registro' | — |
| `co_sucu_mo` | char(6) | NULL | b'Codigo de la sucursal donde fue modificado por ultima vez el registro' | — |
| `fe_us_mo` | datetime(23,3) | NOT NULL | b'Fecha de la ultima modificacion del registro' | — |
| `revisado` | char(1) | NULL | b'Reservado por el sistema' | — |
| `trasnfe` | char(1) | NULL | b'Reservado por el sistema' | — |
| `validador` | timestamp | NOT NULL | b'Marca de tiempo usada en el control de concurrencia' | — |
| `co_mone` | char(6) | NULL | — | FK Implícita → `saMoneda.co_mone` |
| `Inactivo` | bit(1,0) | NOT NULL | — | — |
| `rowguid` | uniqueidentifier | NOT NULL | b'Identificador Unico' | — |

## Triggers Relacionados
_Ninguno_

## Foreign Keys (explícitas)
- `FK_saArtPrecio_saAlmacen`: `co_alma` → `saAlmacen.co_alma`
- `FK_saArtPrecio_saTipoPrecio`: `co_precio` → `saTipoPrecio.co_precio`
- `FK_saArtPrecio_saArticulo`: `co_art` → `saArticulo.co_art`

## Relaciones Clave
- **Artículo**: `saArticulo` vía `co_art`
- **Tipo de precio**: `saTipoPrecio` vía `co_precio` (ej. contado/crédito/mayorista)
- **Almacén**: `saAlmacen` vía `co_alma` (nullable — precio global si no aplica un almacén específico)
- **Margen asociado**: `saArtMargen` (mismo par `co_art`/`co_precio`) define el rango de margen mínimo/máximo permitido para este precio (ver SP `pObtenerMargenXTipoPrecio`)

## Recetario SQL de Negocio (no verificado en vivo — inferido del esquema)
```sql
-- Precio de lista vigente hoy por artículo y tipo de precio
SELECT co_art, co_precio, co_alma, monto, co_mone
FROM saArtPrecio
WHERE Inactivo = 0
  AND desde <= GETDATE()
  AND (hasta IS NULL OR hasta >= GETDATE());

-- Comparar precio de lista vigente vs. precio efectivo facturado (variación de precio)
SELECT r.co_art, r.doc_num, f.fec_emis,
       r.prec_vta AS precio_facturado,
       p.monto    AS precio_lista_vigente,
       r.prec_vta - p.monto AS variacion
FROM saFacturaVentaReng r
INNER JOIN saFacturaVenta f ON f.doc_num = r.doc_num
LEFT JOIN saArtPrecio p
    ON p.co_art = r.co_art AND p.co_precio = r.co_precio
    AND p.Inactivo = 0 AND f.fec_emis BETWEEN p.desde AND ISNULL(p.hasta, '9999-12-31')
WHERE f.anulado = 0;
```
