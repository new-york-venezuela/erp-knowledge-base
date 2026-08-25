# Tabla: saCatArticulo
**Módulo**: Inventario
**Descripción de Negocio**: Catálogo de categorías de artículo (`co_cat`/`cat_des`). Es el tercer nivel de clasificación jerárquica de producto en Profit Plus, junto a Línea (`saLineaArticulo`) y Sub-Línea (`saSubLinea`) — a diferencia de éstas, la Categoría (`saArticulo.co_cat`) no está anidada bajo Línea/Sub-Línea; es un eje de clasificación independiente y paralelo. Referenciada por `saArticulo.co_cat`. Usada para reportería de ventas/margen por categoría y para asignar el concepto de retención ISLR (`co_reten`) e impuesto municipal (`co_imun`) por defecto a nivel de categoría. **No verificado en vivo** — descripción derivada del esquema de columnas y por analogía con `saLineaArticulo`/`saSubLinea` (mismo patrón de campos).

## Campos
| Campo | Tipo | Nulo | Descripción | Relación |
|---|---|---|---|---|
| `co_cat` | char(6) | NOT NULL | b'Codigo de Categoria' | — |
| `cat_des` | varchar(60) | NOT NULL | b'Descripci\xc3\xb3n de la categor\xc3\xada' | — |
| `co_imun` | char(15) | NULL | b'C\xc3\xb3digo del impuesto municipal' | — |
| `co_reten` | char(6) | NULL | b'Codigo de concepto de I.S.L.R.' | FK → `saConISLR.co_islr` |
| `feccom` | smalldatetime(16,0) | NULL | b'Informacion Contable: fecha de procesamiento en contabilidad' | — |
| `numcom` | int(10,0) | NULL | b'Informacion Contable: numero de comprobante de contabilidad asociado' | — |
| `dis_cen` | xml | NULL | b'Informacion Contable: cuenta contable, cuenta de gasto, distribucion de centro de costo (formato XML)' | — |
| `movil` | bit(1,0) | NOT NULL | b'Registro proveniente de Profit M\xc3\xb3vil' | — |
| `campo1` | varchar(60) | NULL | b'Campo Adicional' | — |
| `campo2` | varchar(60) | NULL | b'Campo Adicional' | — |
| `campo3` | varchar(60) | NULL | b'Campo Adicional' | — |
| `campo4` | varchar(60) | NULL | b'Campo Adicional' | — |
| `campo5` | varchar(60) | NULL | b'Campo Adicional' | — |
| `campo6` | varchar(60) | NULL | b'Campo Adicional' | — |
| `campo7` | varchar(60) | NULL | b'Campo Adicional' | — |
| `campo8` | varchar(60) | NULL | b'Campo Adicional' | — |
| `co_us_in` | char(6) | NOT NULL | b'Codigo del usuario que ingreso el registro' | — |
| `co_sucu_in` | char(6) | NULL | b'Codigo de la sucursal donde fue ingresado el registro' | — |
| `fe_us_in` | datetime(23,3) | NOT NULL | b'Fecha de insercion del registro' | — |
| `co_us_mo` | char(6) | NOT NULL | b'Codigo del usuario que hizo la ultima modificaci\xc3\xb3n en el registro' | — |
| `co_sucu_mo` | char(6) | NULL | b'Codigo de la sucursal donde fue modificado por ultima vez el registro' | — |
| `fe_us_mo` | datetime(23,3) | NOT NULL | b'Fecha de la ultima modificacion del registro' | — |
| `revisado` | char(1) | NULL | b'Reservado por el sistema' | — |
| `trasnfe` | char(1) | NULL | b'Reservado por el sistema' | — |
| `validador` | timestamp | NOT NULL | b'Marca de tiempo usada en el control de concurrencia' | — |
| `rowguid` | uniqueidentifier | NOT NULL | b'Identificador Unico' | — |

## Triggers Relacionados
_Ninguno_

## Foreign Keys (explícitas)
- `FK_saCatArticulo_saConISLR`: `co_reten` → `saConISLR.co_islr`

## Relaciones Clave
- **Artículos de esta categoría**: `saArticulo.co_cat` (FK implícita, no declarada como FK explícita en el esquema)

## Recetario SQL de Negocio (no verificado en vivo — inferido del esquema)
```sql
-- Margen bruto por categoría de artículo (requiere costo — ver saCostoHistoricoSalida.md)
SELECT c.co_cat, c.cat_des,
       SUM(r.reng_neto) AS venta_neta,
       COUNT(DISTINCT r.doc_num) AS num_facturas
FROM saFacturaVentaReng r
INNER JOIN saFacturaVenta f ON f.doc_num = r.doc_num
INNER JOIN saArticulo a     ON a.co_art  = r.co_art
INNER JOIN saCatArticulo c  ON c.co_cat  = a.co_cat
WHERE f.anulado = 0
GROUP BY c.co_cat, c.cat_des
ORDER BY venta_neta DESC;
```
