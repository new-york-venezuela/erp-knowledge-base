# SP: pStockActualizar
**Tipo**: Actualización de stock (procedimiento de negocio de bajo nivel)
**Módulo**: Inventario
**Descripción de Negocio**: Es el **único** procedimiento en todo Profit Plus que efectivamente modifica `saStockAlmacen.stock`. Ningún trigger sincroniza automáticamente el stock cuando se insertan líneas de ajuste, factura, traslado, etc. — todos esos flujos (ventas, compras, ajustes, traslados) deben llamar explícitamente a `pStockActualizar` por cada línea que mueva inventario. Verificado leyendo `OBJECT_DEFINITION` completo en la base `Ncake_a`.

## Firma
```sql
CREATE PROCEDURE [pStockActualizar]
    (
      @sCo_Alma CHAR(6) ,
      @sCo_Art CHAR(30) ,
      @sCo_Uni CHAR(6) ,              -- unidad en la que viene @deCantidad
      @deCantidad DECIMAL(18, 5) ,    -- siempre positiva; el signo lo decide @bSumarStock
      @sTipoStock CHAR(4) ,           -- 'ACT'|'SACT'|'LLE'|'SLLE'|'COM'|'SCOM'|'DES'|'SDES'
      @bSumarStock BIT ,              -- 1 = sumar (entrada), 0 = restar (salida)
      @bPermiteStockNegativo BIT      -- decisión explícita del llamador, no hay bandera de config
    )
```

## Lógica (verificada línea por línea)
1. Si `@bSumarStock = 0`, `@deCantidad` se vuelve negativa internamente.
2. `@deCantidad` se convierte a la unidad base del artículo vía `dbo.ArtUnidadBase(@sCo_Art, @sCo_Uni, @deCantidad)`. Si la función devuelve `NULL` (no existe relación artículo/unidad en `saArtUnidad`), se lanza `RAISERROR` y se aborta — **el módulo nuevo debe garantizar que la unidad enviada tenga fila en `saArtUnidad` para el artículo**.
3. Valida que `@sTipoStock` sea uno de los 8 códigos válidos (`ACT`, `SACT`, `LLE`, `SLLE`, `COM`, `SCOM`, `DES`, `SDES`). Para el módulo de inventario manual, el código relevante es **`ACT`** ("Actual" = existencia real; es el que usa `saStockAlmacen` para todo el resto del sistema — ventas, reportes, etc.).
4. Abre una transacción (o `SAVE TRANSACTION` si ya hay una activa — es seguro llamarlo dentro de una transacción más grande).
5. `UPDATE saStockAlmacen SET stock = stock + @deCantidad WHERE co_alma=@sCo_Alma AND co_art=@sCo_Art AND tipo=@sTipoStock`, capturando el `OUTPUT inserted.stock`.
6. **Si no existe fila previa** (`(co_alma, co_art, tipo)` no está en `saStockAlmacen`):
   - Si es una resta (`@bSumarStock=0`) y `@bPermiteStockNegativo=0`: `ROLLBACK` + `RAISERROR('No existe stock "Actual" para el artículo "..." en el almacén "...". El stock actual es 0.00000 y el stock final es de <cantidad>')`.
   - En cualquier otro caso: `INSERT INTO saStockAlmacen (co_alma, co_art, tipo, stock, revisado, trasnfe) VALUES (..., @deCantidad, NULL, NULL)` — es decir, la fila se crea sola la primera vez que un artículo tiene movimiento en un almacén.
7. **Si el UPDATE sí afectó una fila** y el resultado quedó negativo: si `@bSumarStock=0 AND @bPermiteStockNegativo=0 AND stockFinal<0` → `ROLLBACK` + mismo `RAISERROR` con los valores reales de stock actual/final.
8. Si nada de lo anterior abortó, `COMMIT` y devuelve `stockFinal` como resultset.

## Implicación para el módulo de Inventario nuevo
- Para "Ajuste de inventario", llamar con `@sTipoStock='ACT'`, `@sCo_Uni` = la unidad base del artículo (evitar conversiones innecesarias), `@bSumarStock` derivado de `saTipoAjuste.tipo_trans` de la línea (`0`→sumar, `1`→restar).
- `@bPermiteStockNegativo` debe ser una decisión de negocio explícita, expuesta en la UI o en la política del módulo — no existe un default seguro en el propio ERP. Dato real de esta BD: el almacén `000015` (OFICINA) ya tiene stock total negativo (-53.279 sumado), así que el negocio ya opera, al menos en un almacén, sin bloqueo estricto de negativos.
- Este SP debe llamarse **después** de `pInsertarRenglonesAjusteEntradaSalida` (que solo actualiza costeo), como tercer paso del flujo de creación de ajuste — ver [`saAjuste`](../tables/saAjuste.md).
- Si `RAISERROR` se dispara, la transacción de stock hace `ROLLBACK` internamente, pero el `INSERT` en `saAjuste`/`saAjusteReng` de los pasos previos **no se revierte automáticamente** a menos que la aplicación los envuelva en una transacción externa común — riesgo real de inconsistencia (ajuste registrado, stock no aplicado) si no se maneja con cuidado en el código de la API.

### ⚠️ `XACT_ABORT ON` por sí solo NO basta para revertir una transacción externa — confirmado reproduciendo el fallo
Si un procedimiento externo envuelve los 3 pasos de creación de ajuste (`pInsertarAjusteEntradaSalida` → `pInsertarRenglonesAjusteEntradaSalida` → `pStockActualizar`) en una transacción propia usando solo `SET XACT_ABORT ON; BEGIN TRAN; ... COMMIT TRAN;`, **una falla de stock negativo dentro de `pStockActualizar` no revierte el `INSERT` del encabezado en `saAjuste`** — reproducido en vivo: forzando una salida que excede el stock disponible con `@bPermiteStockNegativo=0`, el conteo de filas de `saAjuste` subió de 3 a 4 a pesar de que la llamada "falló" y `saStockAlmacen.stock` correctamente no cambió.

**Causa raíz**: este SP abre su transacción vía `SAVE TRANSACTION`/`ROLLBACK TRANSACTION` (un *savepoint*) cuando detecta que ya hay una transacción abierta alrededor (línea "Abre una transacción (o `SAVE TRANSACTION` si ya hay una activa...)" arriba) — el `RAISERROR` + `RETURN` que sigue a ese rollback de savepoint no escala de forma confiable a abortar la transacción *externa* bajo `XACT_ABORT` solo.

**Solución verificada**: el procedimiento externo debe usar `BEGIN TRY`/`BEGIN CATCH` explícito, y en el `CATCH` comprobar `XACT_STATE() <> 0` antes de emitir su propio `ROLLBACK TRAN`, luego re-lanzar el error original vía `RAISERROR`. Reprobado el mismo escenario de stock negativo contra la versión corregida: el conteo de filas de `saAjuste`, `saStockAlmacen.stock`, **y** el contador de `saSerie.prox_n` avanzado por `pConsecutivoProximoOutPut` (si se llamó antes en la misma transacción) revirtieron correctamente en conjunto. Ejemplo completo de este patrón: `pApiCrearAjusteInventario` en `profitplus-exporter/mssql-migrations/0002_pApiCrearAjusteInventario.sql`.

## Tablas Referenciadas
- [`saStockAlmacen`](../tables/saStockAlmacen.md) (lectura/escritura)
- `saArtUnidad` (vía función `dbo.ArtUnidadBase`, lectura)

## Recetario SQL de Negocio
```sql
-- Llamada típica para aplicar una línea de ajuste de ENTRADA (tipo_trans='0')
EXEC pStockActualizar
    @sCo_Alma = '14', @sCo_Art = '0000063', @sCo_Uni = 'UND',
    @deCantidad = 25.00000, @sTipoStock = 'ACT',
    @bSumarStock = 1, @bPermiteStockNegativo = 0;

-- Llamada típica para aplicar una línea de ajuste de SALIDA (tipo_trans='1')
-- con negativo permitido explícitamente por política del almacén/negocio
EXEC pStockActualizar
    @sCo_Alma = '000015', @sCo_Art = '0000063', @sCo_Uni = 'UND',
    @deCantidad = 10.00000, @sTipoStock = 'ACT',
    @bSumarStock = 0, @bPermiteStockNegativo = 1;
```
