# Tabla: saAjuste
**Módulo**: Inventario
**Descripción de Negocio**: Encabezado de un documento de ajuste de inventario. Un ajuste agrupa una o más líneas (`saAjusteReng`), cada una con su propio tipo (`co_tipo`, entrada o salida) y almacén (`co_alma`) — es decir, **un mismo documento de ajuste puede mover varios artículos en varios almacenes con distintos motivos**. Verificado en vivo vía `sys.columns` + `MS_Description` (base `Ncake_a`); reemplaza doc previo incompleto (dump crudo sin síntesis).

## Campos Clave (verificado en vivo, 30 columnas)
| Campo | Tipo | Nulo | Descripción de Negocio | Relación |
|---|---|---|---|---|
| `ajue_num` | char | NOT NULL | Número de Ajuste (PK, consecutivo) | Clave Primaria |
| `fecha` | smalldatetime | NOT NULL | Fecha del Ajuste | — |
| `motivo` | varchar | NULL | Motivo del Ajuste (texto libre) | — |
| `co_mone` | char | NOT NULL | Código de la moneda | FK → `saMoneda.co_mone` |
| `tasa` | decimal | NOT NULL | Tasa de conversión de la moneda del documento respecto a la moneda base | — |
| `seriales_s` | int | NULL | Reservado para futuras implementaciones | — |
| `seriales_e` | int | NULL | Reservado para futuras implementaciones | — |
| `feccom` | smalldatetime | NULL | Info. Contable: fecha de procesamiento en contabilidad | — |
| `numcom` | int | NULL | Info. Contable: número de comprobante de contabilidad asociado | — |
| `anulado` | bit | NOT NULL | **`1` = ajuste anulado.** Regla universal del ERP: filtrar `anulado=0` en reportes. | — |
| `co_invfisico` | char | NULL | Código de Inventario Físico — **si no es NULL, este ajuste fue generado automáticamente por el cierre de un conteo físico** (ver `saInventarioFisico`), no por captura manual | FK → `saInventarioFisico.co_invfisico` |
| `aux01` | decimal | NULL | Reservado para futuras implementaciones | — |
| `aux02` | varchar | NULL | Reservado para futuras implementaciones | — |
| `dis_cen` | xml | NULL | Info. Contable: distribución de centro de costo (XML) | — |
| `campo1`…`campo8` | varchar | NULL | Campos personalizables adicionales | — |
| `co_us_in` / `co_sucu_in` / `fe_us_in` | mixto | mixto | Usuario, sucursal y fecha de inserción — usar para "quién creó el ajuste" en la UI | — |
| `co_us_mo` / `co_sucu_mo` / `fe_us_mo` | mixto | mixto | Usuario, sucursal y fecha de última modificación | — |
| `revisado` / `trasnfe` | char | NULL | Reservado por el sistema (replicación / transferencia multiempresa) | — |
| `validador` | timestamp | NOT NULL | Control de concurrencia optimista | — |
| `rowguid` | uniqueidentifier | NOT NULL | Identificador único | — |

**Nota**: el encabezado NO tiene columna `co_alma` ni `co_tipo` — ambas viven en `saAjusteReng` (por línea). Un ajuste no es "de entrada" o "de salida" en sí mismo; cada línea lo es.

## Datos reales observados (base `Ncake_a`)
**0 filas** — no hay ningún ajuste manual registrado históricamente en esta instalación productiva. El módulo nuevo será, en la práctica, el primer flujo sistemático de ajustes para este negocio — sin patrones históricos que imitar, pero también sin riesgo de romper reportes existentes basados en datos previos.

## Foreign Keys (explícitas, verificadas)
- `FK_saAjuste_saMoneda`: `co_mone` → `saMoneda.co_mone`
- `FK_saAjuste_saInventarioFisico`: `co_invfisico` → `saInventarioFisico.co_invfisico`

## Triggers Relacionados
- `TrigEstado_saAjuste`: registra en `saHistoricoEstado` cada cambio del flag `anulado` (mismo patrón que `TrigEstado_saArticulo`).

## Procedimientos Almacenados Asociados — flujo de creación verificado (código fuente leído en vivo)

`ajue_num` se genera vía el mecanismo genérico de consecutivos (`saConsecutivo`, clave `co_consecutivo='AJUS_NUM'`, serie `I001-1` en esta BD) — **no** vía `pObtenerNroAjuste` (ese SP solo resuelve el número a partir de un `co_invfisico`; solo aplica al flujo de conteo físico, que esta BD tampoco usa: `saInventarioFisico` también tiene 0 filas). La llamada correcta, verificada en vivo (deployada y ejecutada repetidamente contra esta BD), es [`pConsecutivoProximoOutPut`](../procedures/pConsecutivoProximoOutPut.md) con `@sCo_Consecutivo='AJUS_NUM'` y `@sCo_Sucur` de la sucursal que crea el ajuste — **no** leer/incrementar `saConsecutivo`/`saSerie` a mano: esa tabla es un mapeo, no un contador (ver [`saConsecutivo`](saConsecutivo.md)), y el SP hace el cálculo + avance de forma atómica, segura bajo concurrencia.

El flujo de creación de un ajuste **NO es una sola llamada atómica** — el cliente ERP orquesta 3 pasos, y ninguno de los dos primeros toca `saStockAlmacen`:

1. **`pInsertarAjusteEntradaSalida`** — inserta el encabezado en `saAjuste`. Firma real: `(@sAjue_Num, @sCo_Mone, @sMotivo, @sdFecha, @deTasa, @bAnulado, @sCo_InvFisico=NULL, @deAux01, @sAux02, @sDis_Cen=NULL, @sCampo1..8=NULL, @sCo_Us_In, @sCo_Sucu_In, @sMaquina=NULL, @sRevisado=NULL, @sTrasnfe=NULL)`. Solo hace el `INSERT` + registra una "pista" de auditoría (`pInsertarPista`).
2. **`pInsertarRenglonesAjusteEntradaSalida`** — inserta cada línea en `saAjusteReng`. Al final, consulta `saTipoAjuste.tipo_trans` para la línea: si `tipo_trans=0` llama a `pCostoActualizarEntrada`, si no a `pCostoActualizarSalida` (ambos actualizan `saCostoHistoricoEntrada`/`saCostoHistoricoSalida` para costeo — **tampoco tocan `saStockAlmacen`**).
3. **`pStockActualizar`** — es el **único** SP que efectivamente escribe `saStockAlmacen.stock`. Debe llamarse explícitamente por cada línea del ajuste, con `@sTipoStock='ACT'` (el tipo de stock "existencia actual", el que usa el resto del sistema), `@bSumarStock` = 1 si la línea es de entrada (`tipo_trans='0'`) o 0 si es de salida (`tipo_trans='1'`), y `@bPermiteStockNegativo` decidido explícitamente por quien llama — no existe ninguna bandera en `saArticulo` ni `saAlmacen` que lo controle a nivel de configuración.

**Implicación de diseño para el módulo nuevo**: como no hay trigger de servidor que sincronice `saAjusteReng` → `saStockAlmacen`, la aplicación debe envolver los 3 pasos en una transacción SQL explícita del lado del cliente/API — si falla entre el paso 2 y 3, queda una línea de ajuste sin reflejo en el stock real.

### Validación de stock negativo (dentro de `pStockActualizar`)
Si `@bSumarStock=0` (restando) y `@bPermiteStockNegativo=0`: cuando no existe fila en `saStockAlmacen` para `(co_alma, co_art, tipo)`, o el resultado quedaría negativo, el SP hace `ROLLBACK TRANSACTION` y `RAISERROR` con: `'No existe stock "Actual" para el artículo "<co_art>" en el almacén "<co_alma>". El stock actual es <X> y el stock final es de <Y>'`.

**Dato real de esta BD**: el almacén `000015` (OFICINA) tiene stock total de **-53,279** sumado entre sus 88 artículos — es decir, en la operación real de este negocio ya existe stock negativo, así que `@bPermiteStockNegativo=1` se ha usado (o el negativo llegó por otra vía, p. ej. ventas sin control de stock). El módulo nuevo debe tratar "permitir negativo" como una decisión explícita por ajuste, no asumir un valor fijo global.

## Recetario SQL de Negocio
```sql
-- Historial de ajustes con su detalle
SELECT h.ajue_num, h.fecha, h.motivo, h.co_us_in, h.anulado,
       r.co_art, ar.art_des, r.co_alma, al.des_alma,
       t.des_tipo, t.tipo_trans, r.total_art, r.cost_unit
FROM saAjuste h
JOIN saAjusteReng r ON r.ajue_num = h.ajue_num
JOIN saArticulo ar ON ar.co_art = r.co_art
JOIN saAlmacen al ON al.co_alma = r.co_alma
JOIN saTipoAjuste t ON t.co_tipo = r.co_tipo
WHERE h.anulado = 0
ORDER BY h.fecha DESC;
```
