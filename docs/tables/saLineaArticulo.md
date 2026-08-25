# Tabla: saLineaArticulo
**Módulo**: Inventario
**Descripción de Negocio**: Catálogo de líneas de artículo (`co_lin`/`lin_des`) — primer nivel de la jerarquía de clasificación de producto (Línea → Sub-Línea, ver `saSubLinea`). Referenciada por `saArticulo.co_lin`. Además de clasificar, define comisión por defecto para vendedores (`comi_lin` = % comisión por ventas, `comi_lin2` = % comisión por cobros) y retención ISLR/impuesto municipal por defecto (`co_reten`, `co_imun`) heredable por los artículos de la línea. **No verificado en vivo** — descripción derivada del esquema de columnas y FKs explícitas.

## Campos
| Campo | Tipo | Nulo | Descripción | Relación |
|---|---|---|---|---|
| `co_lin` | char(6) | NOT NULL | b'Codigo de Linea' | — |
| `lin_des` | varchar(60) | NOT NULL | b'Descripci\xc3\xb3n de la Linea' | — |
| `dis_cen` | xml | NULL | b'Informacion Contable: cuenta contable, cuenta de gasto, distribucion de centro de costo (formato XML)' | — |
| `co_imun` | char(15) | NULL | b'C\xc3\xb3digo Impuesto Municipal' | — |
| `co_reten` | char(6) | NULL | b'Codigo de concepto de I.S.L.R.' | FK → `saConISLR.co_islr` |
| `comi_lin` | decimal(18,2) | NOT NULL | b'Porcentaje de Comisi\xc3\xb3n por Ventas' | — |
| `comi_lin2` | decimal(18,2) | NOT NULL | b'Porcentaje de Comisi\xc3\xb3n por Cobros' | — |
| `i_lin_des` | varchar(60) | NULL | b'Descripci\xc3\xb3n Otro Idioma' | — |
| `va` | bit(1,0) | NOT NULL | b'Enviar a eProfit' | — |
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
| `feccom` | smalldatetime(16,0) | NULL | b'Informacion Contable: fecha de procesamiento en contabilidad' | — |
| `numcom` | int(10,0) | NULL | b'Informacion Contable: numero de comprobante de contabilidad asociado' | — |

## Triggers Relacionados
_Ninguno_

## Foreign Keys (explícitas)
- `FK_saLineaArticulo_saConISLR`: `co_reten` → `saConISLR.co_islr`

## Relaciones Clave
- **Sub-líneas**: `saSubLinea.co_lin` (jerarquía Línea → Sub-Línea)
- **Artículos de esta línea**: `saArticulo.co_lin` (FK implícita)

## Recetario SQL de Negocio (no verificado en vivo — inferido del esquema)
```sql
-- Ventas netas y comisión de vendedor esperada por línea de artículo
SELECT l.co_lin, l.lin_des, l.comi_lin AS pct_comision_venta,
       SUM(r.reng_neto) AS venta_neta,
       SUM(r.reng_neto) * l.comi_lin / 100.0 AS comision_estimada
FROM saFacturaVentaReng r
INNER JOIN saFacturaVenta f  ON f.doc_num = r.doc_num
INNER JOIN saArticulo a      ON a.co_art  = r.co_art
INNER JOIN saLineaArticulo l ON l.co_lin  = a.co_lin
WHERE f.anulado = 0
GROUP BY l.co_lin, l.lin_des, l.comi_lin
ORDER BY venta_neta DESC;
```
