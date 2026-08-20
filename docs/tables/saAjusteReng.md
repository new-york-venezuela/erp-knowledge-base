# Tabla: saAjusteReng
**Módulo**: Inventario
**Descripción de Negocio**: Línea de detalle de un ajuste de inventario. Cada fila mueve UN artículo en UN almacén con UN tipo de ajuste (entrada o salida, ver `saTipoAjuste`) y su costo unitario asociado. Verificado en vivo vía `sys.columns` + `MS_Description`; reemplaza doc previo incompleto (dump crudo sin síntesis).

## Campos Clave (verificado en vivo, 22 columnas)
| Campo | Tipo | Nulo | Descripción de Negocio | Relación |
|---|---|---|---|---|
| `ajue_num` | char | NOT NULL | No. de Ajuste (PK compuesta, FK a encabezado) | FK → `saAjuste.ajue_num` |
| `reng_num` | int | NOT NULL | Número de Renglón (PK compuesta) | — |
| `co_tipo` | char | NOT NULL | **Tipo de ajuste de esta línea** (el texto "Tipo de proveedor" en `MS_Description` de origen es un error de copy-paste del propio Profit Plus — el valor real es el tipo de ajuste) | FK → `saTipoAjuste.co_tipo` |
| `co_art` | char | NOT NULL | Código del artículo | FK → `saArticulo.co_art` (también existe FK explícita hacia `saArtUnidad.co_art`) |
| `co_alma` | char | NOT NULL | **Código del almacén de esta línea** | FK → `saAlmacen.co_alma` |
| `co_uni` | char | NOT NULL | Código de la unidad (unidad primaria) | FK → `saArtUnidad.co_uni` |
| `sco_uni` | char | NULL | Código de la unidad secundaria | FK → `saArtUnidad.co_uni` |
| `dis_cen` | xml | NULL | Info. Contable: distribución de centro de costo (XML) | — |
| `total_art` | decimal | NOT NULL | **Cantidad de artículos movida en esta línea (unidad primaria)** | — |
| `stotal_art` | decimal | NOT NULL | Cantidad en unidad secundaria | — |
| `cost_unit` | decimal | NOT NULL | Costo unitario asignado a esta línea | — |
| `lote_asignado` | bit | NOT NULL | `1` = tiene información de lote asignada | — |
| `costo_adi1` | decimal | NOT NULL | Costo promedio unitario | — |
| `costo_adi2` | decimal | NOT NULL | Último costo en otra moneda | — |
| `costo_adi3` | decimal | NOT NULL | Costo promedio en otra moneda | — |
| `co_us_in` / `co_sucu_in` / `fe_us_in` | mixto | mixto | Usuario/sucursal/fecha de inserción | — |
| `co_us_mo` / `co_sucu_mo` / `fe_us_mo` | mixto | mixto | Usuario/sucursal/fecha de última modificación | — |
| `revisado` / `trasnfe` | char | NULL | Reservado por el sistema | — |
| `rowguid` | uniqueidentifier | NOT NULL | Identificador único — es el valor que aparecería como `doc_orig` en `saCostoHistoricoEntrada`/`saCostoHistoricoSalida` cuando el origen del movimiento es un ajuste | — |

**No tiene columna `validador` (timestamp)** — a diferencia de la mayoría de tablas del ERP, no implementa control de concurrencia optimista en las líneas.

## Foreign Keys (explícitas, verificadas)
- `FK_saAjusteReng_saAjuste`: `ajue_num` → `saAjuste.ajue_num`
- `FK_saAjusteReng_saTipoAjuste`: `co_tipo` → `saTipoAjuste.co_tipo`
- `FK_saAjusteReng_saAlmacen`: `co_alma` → `saAlmacen.co_alma`
- `FK_saAjusteReng_saArtUnidad` (×2): `co_art` → `saArtUnidad.co_art`; `co_uni` → `saArtUnidad.co_uni`
- `FK_saAjusteReng_saArtUnidadSec` (×2): `co_art` → `saArtUnidad.co_art`; `sco_uni` → `saArtUnidad.co_uni`

## Triggers Relacionados
_Ninguno verificado en `sys.triggers` para esta tabla._ Esto confirma que **el proceso de actualización de `saStockAlmacen` a partir de un ajuste NO ocurre automáticamente por trigger** — debe ser orquestado explícitamente por el stored procedure que crea el ajuste (o replicado por la aplicación cliente). Cualquier implementación en el módulo nuevo debe llamar al procedimiento de negocio correspondiente, no limitarse a un `INSERT` en `saAjuste`/`saAjusteReng`.

## Recetario SQL de Negocio
```sql
-- Próximo número de renglón para una línea nueva de un ajuste existente
SELECT ISNULL(MAX(reng_num), 0) + 1 AS next_reng_num
FROM saAjusteReng
WHERE ajue_num = @ajue_num;
```
