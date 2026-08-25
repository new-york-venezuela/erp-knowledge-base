# Tabla: saSubLinea
**Módulo**: Inventario
**Descripción de Negocio**: Catálogo de sub-líneas de artículo (`co_subl`/`subl_des`), anidadas bajo una Línea (`co_lin` → `saLineaArticulo`) — segundo nivel de la jerarquía Línea → Sub-Línea. Clave primaria compuesta (`co_lin`, `co_subl`). Referenciada por `saArticulo.co_subl` (junto con `co_lin` para resolver la sub-línea completa, ya que `co_subl` no es único por sí solo — depende de la línea padre). **No verificado en vivo** — descripción derivada del esquema de columnas y FKs explícitas.

## Campos
| Campo | Tipo | Nulo | Descripción | Relación |
|---|---|---|---|---|
| `co_lin` | char(6) | NOT NULL | b'Codigo de Linea' | FK → `saLineaArticulo.co_lin` |
| `co_subl` | char(6) | NOT NULL | b'Codigo de Sub Linea' | — |
| `subl_des` | varchar(60) | NOT NULL | b'Descripci\xc3\xb3n de la l\xc3\xadnea' | — |
| `co_imun` | char(15) | NULL | b'C\xc3\xb3digo Impuesto Municipal' | — |
| `co_reten` | char(6) | NULL | b'Codigo de concepto de I.S.L.R.' | FK → `saConISLR.co_islr` |
| `i_subl_des` | varchar(60) | NULL | b'Descripci\xc3\xb3n otro idioma' | — |
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
- `FK_saSubLinea_saConISLR`: `co_reten` → `saConISLR.co_islr`
- `FK_saSubLinea_saLineaArticulo`: `co_lin` → `saLineaArticulo.co_lin`

## Relaciones Clave
- **Línea padre**: `saLineaArticulo` vía `co_lin`
- **Artículos de esta sub-línea**: `saArticulo` vía (`co_lin`, `co_subl`) compuesto — no unir sólo por `co_subl`

## Recetario SQL de Negocio (no verificado en vivo — inferido del esquema)
```sql
-- Jerarquía completa Línea > Sub-Línea con conteo de artículos activos
SELECT l.co_lin, l.lin_des, s.co_subl, s.subl_des,
       COUNT(a.co_art) AS num_articulos
FROM saLineaArticulo l
INNER JOIN saSubLinea s ON s.co_lin = l.co_lin
LEFT JOIN saArticulo a  ON a.co_lin = s.co_lin AND a.co_subl = s.co_subl AND a.anulado = 0
GROUP BY l.co_lin, l.lin_des, s.co_subl, s.subl_des
ORDER BY l.co_lin, s.co_subl;
```
