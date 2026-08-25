# Tabla: saTasa
**Módulo**: Configuración (Multimoneda)
**Descripción de Negocio**: Historial de tasas de cambio por moneda. Registra la tasa de compra (`tasa_c`) y venta (`tasa_v`) para cada moneda en cada fecha. Es la fuente de conversión Bs↔USD para todos los cálculos multimoneda. Para indexar montos históricos a USD, siempre usar la tasa del documento (`saFacturaVenta.tasa`), NO la tasa actual.

**Corrección (verificado en vivo, 2026-08-25 vía `INFORMATION_SCHEMA.COLUMNS`)**: la versión anterior de este documento sólo listaba 4 de 22 columnas reales. **Sí tiene `validador`** (tipo `timestamp`/rowversion) — es válido usarla como watermark de carga incremental igual que en la mayoría de las demás tablas de Profit Plus, contrario a lo que se asumió antes de verificar en vivo.

## Campos Clave (verificado en vivo, 22 columnas)
| Campo | Tipo | Nulo | Descripción de Negocio | Relación |
|---|---|---|---|---|
| `co_mone` | char | NOT NULL | Código de moneda (PK con fecha) | FK → `saMoneda.co_mone` |
| `fecha` | smalldatetime | NOT NULL | Fecha de vigencia de la tasa | PK (con co_mone) |
| `tasa_c` | decimal | NULL | Tasa de compra (Bs por unidad de moneda extranjera) | — |
| `tasa_v` | decimal | NULL | Tasa de venta (Bs por unidad de moneda extranjera) | — |
| `campo1`…`campo8` | varchar | NULL | Campos personalizables libres | — |
| `co_us_in` | char | NULL | Usuario que creó el registro | — |
| `co_sucu_in` | char | NULL | Sucursal donde fue ingresado | — |
| `fe_us_in` | datetime | NULL | Fecha de inserción | — |
| `co_us_mo` | char | NULL | Último usuario que modificó | — |
| `co_sucu_mo` | char | NULL | Sucursal de última modificación | — |
| `fe_us_mo` | datetime | NULL | Fecha de última modificación | — |
| `revisado` | char | NULL | Reservado por el sistema (replicación) | — |
| `trasnfe` | char | NULL | Reservado por el sistema (transferencia multiempresa) | — |
| `validador` | timestamp | NOT NULL | **Control de concurrencia optimista — usable como watermark de carga incremental** | — |
| `rowguid` | uniqueidentifier | NOT NULL | Identificador único | — |

## Recetario SQL de Negocio
```sql
-- Tasa USD más reciente
SELECT TOP 1 co_mone, fecha, tasa_c, tasa_v
FROM saTasa
WHERE co_mone = 'USD'
ORDER BY fecha DESC;

-- Evolución de la tasa USD en el año
SELECT co_mone, CAST(fecha AS DATE) AS fecha_dia,
       tasa_c, tasa_v
FROM saTasa
WHERE co_mone = 'USD' AND YEAR(fecha) = 2024
ORDER BY fecha;

-- Tasa vigente en una fecha específica
SELECT TOP 1 tasa_v
FROM saTasa
WHERE co_mone = 'USD' AND fecha <= '2024-06-30'
ORDER BY fecha DESC;
```
