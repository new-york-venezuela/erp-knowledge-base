# Tabla: saSerie
**Módulo**: Inventario
**Descripción de Negocio**: El contador vivo detrás de cualquier numeración consecutiva del sistema (facturas, órdenes, ajustes, etc.) — `saConsecutivo` sólo mapea a *qué fila* de esta tabla corresponde un tipo de documento; el valor que realmente avanza en cada nuevo documento es `prox_n` (numérico) / `prox_a` (alfanumérico), dentro del rango `desde_n`/`hasta_n` (o `desde_a`/`hasta_a`). Nunca leer/incrementar `prox_n`/`prox_a` a mano — usar [`pConsecutivoProximoOutPut`](../procedures/pConsecutivoProximoOutPut.md), que hace el cálculo (vía `pConsecutivoProximoCalcular`, aplicando `saSerieTipo.prefijo`/`sufijo`/`longitud`) y el `UPDATE` de avance en la misma llamada — esto es lo que hace segura la generación de números bajo escritura concurrente (dos llamadas simultáneas obtienen valores distintos gracias al comportamiento estándar de SQL Server ante escritores concurrentes sobre la misma fila).

## Campos
| Campo | Tipo | Nulo | Descripción | Relación |
|---|---|---|---|---|
| `reng_num` | int(10,0) | NOT NULL | b'Numero de Renglon' | — |
| `co_tipo_serie` | char(6) | NOT NULL | — | FK → `saSerieTipo.co_tipo_serie` |
| `co_serie` | char(20) | NULL | — | — |
| `desde_a` | char(20) | NULL | — | — |
| `desde_n` | bigint(19,0) | NULL | — | — |
| `hasta_a` | char(20) | NULL | — | — |
| `hasta_n` | bigint(19,0) | NULL | — | — |
| `prox_a` | char(20) | NULL | — | — |
| `prox_n` | bigint(19,0) | NULL | — | — |
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
- `FK_saSerie_saSerieTipo`: `co_tipo_serie` → `saSerieTipo.co_tipo_serie`
