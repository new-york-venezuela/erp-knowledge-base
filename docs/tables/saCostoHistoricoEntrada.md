# Tabla: saCostoHistoricoEntrada
**Módulo**: Inventario
**Descripción de Negocio**: Historial de capas de costo de entrada por artículo (soporte para costeo PEPS/UEPS). Cada fila es una "capa" de costo creada cuando entra inventario (compra, ajuste de entrada, traslado de entrada, etc.); `saCostoHistoricoSalida` consume estas capas cuando sale inventario. Actualizada por `pCostoActualizarEntrada`/`pCostoActualizarEntradaTodos`, llamada desde `pInsertarRenglonesAjusteEntradaSalida` para ajustes — no la actualiza ningún trigger.

## ⚠️ No tiene columna `co_art` — unir vía `cod_articulo_rowguid` (verificado en vivo)
Esta tabla identifica el artículo por `cod_articulo_rowguid` (`uniqueidentifier`, FK a `saArticulo.rowguid`), **no** por el código legible `co_art`. Confirmado vía `INFORMATION_SCHEMA.COLUMNS` — no existe columna `co_art` en `saCostoHistoricoEntrada`. Para resolver el costo más reciente de un artículo por su código:
```sql
SELECT TOP 1 CHE.costo
FROM saCostoHistoricoEntrada CHE
JOIN saArticulo A ON A.rowguid = CHE.cod_articulo_rowguid
WHERE A.co_art = @co_art
ORDER BY CHE.fecha_emision DESC
```
Un diseño que asuma un filtro directo `WHERE co_art = @co_art` contra esta tabla fallará en tiempo de compilación/ejecución.

## Campos
| Campo | Tipo | Nulo | Descripción | Relación |
|---|---|---|---|---|
| `cod_costo_historico_entrada` | uniqueidentifier | NOT NULL | b'Identificador unico del registro de entrada de costo' | — |
| `cod_articulo_rowguid` | uniqueidentifier | NOT NULL | b'Identificador unico del articulo relacionado (saArticulo.rowguid)' | FK → `saArticulo.rowguid` |
| `cod_almacen` | char(6) | NOT NULL | b'Codigo del almacen' | FK → `saAlmacen.co_alma` |
| `tipo_doc` | char(4) | NOT NULL | b'Tipo documento de origen, FACT: Factura de Venta, NENT: Nota de Entrega, DCLI: Devolucion de Cliente, COMP: Factura de Compra, NREC: Nota de Recepcion, DPRO: Devolucion a Proveedor OCOM: Orden de Compra, CPRO: Cotizacion de Compra, PCOM: Plantilla de Compra, PCLI: Pedido de CLiente, CCLI: Cotizacion a Cliente,NDES: Nota de Despacho, PVEN: Plantilla de Venta, AJUE: Ajuste de Entrada, AJUS: Ajuste de Salida, TRAE: Traslado de Entrada, TRAS: Traslado de Salida, GCOM: Generacion de Compuesto, RGEN: Renglones de Compuesto' | — |
| `doc_orig` | uniqueidentifier | NOT NULL | b'Identificador unico del registro del cual procede (saNombreTabla.rowguid)' | — |
| `cod_costo_historico_salida_orig` | uniqueidentifier | NULL | — | FK → `saCostoHistoricoSalida.cod_costo_historico_salida` |
| `cantidad` | decimal(18,5) | NOT NULL | b'Cantidad de articulos relacionados a la entrada de costo' | — |
| `cantidad_usada` | decimal(18,5) | NOT NULL | b'Cantidad de ariculos relacionados en historico de salida  (UEPS, PEPS) ' | — |
| `costo` | decimal(18,5) | NOT NULL | b'Costo del articulo' | — |
| `costo_pro` | decimal(18,5) | NOT NULL | b'Costo promedio' | — |
| `fecha_emision` | datetime(23,3) | NOT NULL | b'Fecha del documento asociado a la entrada de costo' | — |
| `fecha_registro` | datetime(23,3) | NOT NULL | b'Fecha de registro fisico en la base de datos del registro (Generalmente fe_us_in)' | — |
| `fecha_recepcion` | datetime(23,3) | NULL | b'Reservado para implementaciones futuras' | — |
| `rengNum` | int(10,0) | NOT NULL | — | — |
| `validador` | timestamp | NOT NULL | b'Marca de tiempo usada en el control de concurrencia' | — |

## Triggers Relacionados
_Ninguno_

## Foreign Keys (explícitas)
- `FK_saCostoHistoricoEntrada_saAlmacen`: `cod_almacen` → `saAlmacen.co_alma`
- `FK_saCostoHistoricoEntrada_saArticulo`: `cod_articulo_rowguid` → `saArticulo.rowguid`
- `FK_saCostoHistoricoEntrada_saCostoHistoricoSalida`: `cod_costo_historico_salida_orig` → `saCostoHistoricoSalida.cod_costo_historico_salida`
