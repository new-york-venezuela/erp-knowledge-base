# Tabla: saAlmacen
**Módulo**: Inventario
**Descripción de Negocio**: Maestro de almacenes (bodegas/depósitos). Define los depósitos físicos de inventario de la empresa. Los flags `nocompra` y `noventa` controlan si el almacén puede recibir compras o hacer salidas de venta. Un almacén de `produccion=1` es donde se procesan artículos compuestos (ensamble).

## Campos Clave
| Campo | Tipo | Nulo | Descripción de Negocio | Relación |
|---|---|---|---|---|
| `co_alma` | char | NOT NULL | Código del almacén (PK) | Clave Primaria |
| `des_alma` | varchar | NULL | Descripción del almacén | — |
| `co_sucur` | char | NULL | Sucursal a la que pertenece | FK → `saSucursal` |
| `noventa` | bit | NULL | `1` = no permite ventas desde este almacén | — |
| `nocompra` | bit | NULL | `1` = no permite compras a este almacén | — |
| `materiales` | bit | NULL | `1` = almacén de materiales/insumos (producción) | — |
| `produccion` | bit | NULL | `1` = almacén de producción/ensamble | — |
| `alm_temp` | bit | NULL | `1` = almacén temporal (tránsito) | — |
| `direccion` | varchar | NULL | Dirección física del almacén | — |

## ⚠️ Uso real observado (base `Ncake_a`, producción) — crítico para diseño de UI
La tabla tiene **52 registros de almacén**, pero:
- Sólo **14** tienen `noventa=0` (permiten venta) y sólo **4** tienen `nocompra=0` (permiten compra).
- Muchos son almacenes de ruta de reparto ("RUTA 2", "RUTA 000003", etc.) o placeholders sin usar ("\*\*\*\*\*NO USAR\*\*\*\*\*", nombre en blanco).
- **Sólo 2 almacenes tienen stock real (`saStockAlmacen.stock > 0`) hoy**: `13` (Depósito Gastos/Administrativos, 16 artículos) y `14` (Materia Prima / Depósito Urbina, 45 artículos).
- **Las ventas de producto terminado (166 artículos, tipo `V`) se registran contra el almacén `000015` ("OFICINA")**, que no tiene fila alguna con stock positivo en `saStockAlmacen`. Esto es consistente con una operación de panadería *make-to-order*: el producto terminado no se lleva en inventario formal, sólo se despacha.

**Implicación de diseño**: el módulo de Inventario NO debe presentar un selector con los 52 almacenes. Debe:
1. Filtrar a los almacenes que efectivamente tienen movimiento de stock (`materiales=1` o presencia en `saStockAlmacen`), que en la práctica actual son sólo `13` y `14`.
2. Tratar el alcance real del módulo como **materia prima e insumos**, no producto terminado — el "inventario" que este negocio gestiona activamente es harina, insumos de limpieza, café, equipo de oficina, etc., no las tortas/panes vendidos.
3. Si se requiere trazabilidad de producto terminado en el futuro, es un cambio de proceso en Profit Plus (empezar a registrar salidas contra almacén con stock), no sólo una feature de UI — anotar como fuera de alcance para v1 y confirmarlo con el usuario de negocio antes de prometerlo.

## Recetario SQL de Negocio
```sql
-- Almacenes relevantes para el módulo de Inventario (los que realmente mueven stock)
SELECT DISTINCT a.co_alma, a.des_alma, a.materiales, a.produccion
FROM saAlmacen a
WHERE a.materiales = 1
   OR EXISTS (SELECT 1 FROM saStockAlmacen s WHERE s.co_alma = a.co_alma AND s.stock <> 0)
ORDER BY a.co_alma;
```
