# Tabla: saTipoAjuste
**Módulo**: Inventario
**Descripción de Negocio**: Catálogo de tipos/motivos de ajuste de inventario. Cada tipo se clasifica como Entrada o Salida vía `tipo_trans`. Este catálogo alimenta directamente el selector de "motivo del ajuste" en la UI del módulo de Inventario. (Reclasificado de "Configuración" a "Inventario" — es el catálogo de motivos usado exclusivamente por `saAjusteReng`.)

## Campos Clave
| Campo | Tipo | Nulo | Descripción de Negocio | Relación |
|---|---|---|---|---|
| `co_tipo` | char(6) | NOT NULL | Código del tipo de ajuste (PK) | Clave Primaria |
| `des_tipo` | varchar(60) | NOT NULL | Descripción del tipo de ajuste | — |
| `tipo_trans` | char(1) | NOT NULL | **`0` = Entrada (suma stock), `1` = Salida (resta stock)** — verificado contra datos reales | — |
| `campo1`…`campo8` | varchar(60) | NULL | Campos personalizables adicionales | — |
| `co_us_in` / `co_sucu_in` / `fe_us_in` | mixto | mixto | Usuario/sucursal/fecha de inserción | — |
| `co_us_mo` / `co_sucu_mo` / `fe_us_mo` | mixto | mixto | Usuario/sucursal/fecha de última modificación | — |
| `revisado` / `trasnfe` / `validador` / `rowguid` | mixto | mixto | Campos de sistema estándar | — |

## Datos reales (base `Ncake_a` — catálogo completo, 6 filas, sin cambios desde 2006-2009)
| Código | Descripción | tipo_trans |
|---|---|---|
| `E00001` | Entrada Producción | `0` (Entrada) |
| `E00002` | Entrada De Producción Por Merma Convertida A Materia Prima | `0` (Entrada) |
| `S00001` | Salida | `1` (Salida) |
| `S00002` | Merma De Producción | `1` (Salida) |
| `S00003` | Merma De Producción A Materia Prima | `1` (Salida) |
| `S00004` | Salida De Productos Dañados | `1` (Salida) |

**Implicación de diseño**: no hay un tipo genérico "conteo/recuento" — los ajustes de conteo físico se generan aparte vía `saInventarioFisico` → `saAjuste.co_invfisico`. Para el flujo manual de "crear ajuste" del nuevo módulo, el motivo más relevante para el negocio (insumos/materia prima) es probablemente `S00004` (producto dañado) y `S00001`/`S00002` (salida genérica / merma), con `E00001` para entradas de corrección positiva. Este catálogo es editable en Profit Plus (no es un `CHECK` ni un enum fijo en código) — confirmar con el usuario de negocio si necesita agregar un tipo específico (ej. "Ajuste por conteo manual", "Vencimiento") antes de construir el selector, en vez de asumir que estos 6 bastan.

## Triggers Relacionados
_Ninguno_

## Foreign Keys entrantes
- `saAjusteReng.co_tipo` → `saTipoAjuste.co_tipo`
