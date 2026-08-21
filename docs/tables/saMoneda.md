# Tabla: saMoneda
**Módulo**: Configuración (Multimoneda)
**Descripción de Negocio**: Catálogo de monedas. Define las divisas disponibles en el sistema. La columna `cambio` es la tasa base almacenada en el maestro (no historial); para conversiones históricas siempre usar `saTasa`. El campo `relacion` indica si la moneda es relativa a otra (ej: USD como moneda de referencia).

## ⚠️ Código real de la moneda base (base `Ncake_a`) — no asumir `VES`
El código ISO estándar del bolívar es `VES`, pero **esta base de datos no usa ese código**: la fila con `cambio=1` (la moneda base del sistema) está codificada `'BS'` (padded a `char(6)`: `'BS    '`), descripción "Bolívares". Verificado en vivo insertando contra `saAjuste.co_mone` (FK `FK_saAjuste_saMoneda`): un insert con `co_mone='VES'` falla la FK porque esa fila no existe en esta tabla. Cualquier procedimiento o script nuevo que necesite la moneda base de esta instalación debe usar `'BS    '`, no `'VES'` — o mejor, resolverlo dinámicamente con `SELECT co_mone FROM saMoneda WHERE cambio = 1`.

## Campos Clave
| Campo | Tipo | Nulo | Descripción de Negocio | Relación |
|---|---|---|---|---|
| `co_mone` | char | NOT NULL | Código de la moneda (PK). En esta base: `BS` (base, no `VES`), más monedas extranjeras como `USD`, `EUR` | Clave Primaria |
| `mone_des` | varchar | NULL | Nombre de la moneda (ej: Bolívar Digital, Dólar) | — |
| `cambio` | decimal | NULL | Tasa de cambio base actual (referencia, no histórico). `cambio=1` identifica la moneda base del sistema. | — |
| `relacion` | bit | NULL | `1` = moneda relativa a la moneda base del sistema | — |
