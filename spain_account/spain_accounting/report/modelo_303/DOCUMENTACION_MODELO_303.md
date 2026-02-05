# Documentación del Reporte Modelo 303 - Declaración Trimestral de IVA

## Índice
1. [Descripción General](#descripción-general)
2. [Origen de los Datos](#origen-de-los-datos)
3. [Cuentas Contables Utilizadas](#cuentas-contables-utilizadas)
4. [Columnas del Reporte y Casillas AEAT](#columnas-del-reporte-y-casillas-aeat)
5. [Cómo se Calculan los Importes](#cómo-se-calculan-los-importes)
6. [Filtros Disponibles](#filtros-disponibles)
7. [Ejemplo Práctico](#ejemplo-práctico)
8. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Descripción General

El reporte **Modelo 303** es una herramienta que ayuda a preparar la declaración trimestral de IVA que se presenta ante la Agencia Tributaria (AEAT). Este reporte calcula automáticamente:

- **IVA Devengado (Repercutido)**: El IVA que la empresa ha cobrado a sus clientes en las ventas.
- **IVA Deducible (Soportado)**: El IVA que la empresa ha pagado a sus proveedores en las compras.
- **Diferencia**: Lo que la empresa debe ingresar a Hacienda (si es positivo) o lo que puede compensar/solicitar devolución (si es negativo).

---

## Origen de los Datos

### ¿De dónde saca la información el reporte?

El reporte obtiene los datos del **Libro Mayor (GL Entry)** de ERPNext. Esto significa que:

1. **Incluye TODAS las operaciones contabilizadas**, no solo las facturas.
2. Incluye:
   - Facturas de Venta (Sales Invoice)
   - Facturas de Compra (Purchase Invoice)
   - Asientos Manuales (Journal Entry) que afecten a cuentas de IVA
   - Cualquier otro documento que genere movimientos en las cuentas de IVA

### ¿Por qué se usa el Libro Mayor y no directamente las facturas?

Usar el Libro Mayor garantiza que:
- Se incluyen **todas** las operaciones, incluyendo ajustes manuales
- Los datos coinciden exactamente con la contabilidad
- Se capturan correctamente las facturas rectificativas (abonos)
- El reporte es coherente con el **Libro de Facturas por Empresas**

---

## Cuentas Contables Utilizadas

El reporte busca movimientos en dos grupos de cuentas del Plan General Contable:

### Grupo 472 - Hacienda Pública, IVA Soportado (Compras)

Estas son las cuentas donde se registra el IVA que pagamos a nuestros proveedores:

| Cuenta | Descripción | Tipo IVA |
|--------|-------------|----------|
| 472021000 | IVA SOPORTADO AL 21% | 21% |
| 472010000 | IVA SOPORTADO AL 10% | 10% |
| 472000400 | IVA SOPORTADO 4% | 4% |
| 472022100 | H.P. IVA SOPORTADO SUJETO PASIVO | 21% (ISP) |
| ... | Otras subcuentas del grupo 472 | Según % |

### Grupo 477 - Hacienda Pública, IVA Repercutido (Ventas)

Estas son las cuentas donde se registra el IVA que cobramos a nuestros clientes:

| Cuenta | Descripción | Tipo IVA |
|--------|-------------|----------|
| 477021000 | IVA REPERCUTIDO AL 21% | 21% |
| 477001000 | HP IVA REPERCUTIDO 10% | 10% |
| 477022100 | H.P. IVA REPERCUTIDO SUJETO PASIVO | 21% (ISP) |
| ... | Otras subcuentas del grupo 477 | Según % |

### ¿Cómo detecta el reporte el tipo de IVA?

El reporte extrae automáticamente el porcentaje de IVA del **nombre de la cuenta contable**. Por ejemplo:
- "IVA SOPORTADO AL **21%**" → detecta 21%
- "HP IVA REPERCUTIDO **10%**" → detecta 10%
- "IVA SOPORTADO **4%**" → detecta 4%

---

## Columnas del Reporte y Casillas AEAT

Cada columna del reporte corresponde a una casilla del formulario oficial del Modelo 303:

### IVA Devengado (Lo que cobramos a clientes)

| Columna en Reporte | Casilla AEAT | Qué significa |
|--------------------|--------------|---------------|
| [07] Base 21% | Casilla 07 | Total de ventas gravadas al 21% (sin IVA) |
| [09] Cuota 21% | Casilla 09 | IVA cobrado al 21% |
| [04] Base 10% | Casilla 04 | Total de ventas gravadas al 10% (sin IVA) |
| [06] Cuota 10% | Casilla 06 | IVA cobrado al 10% |
| [01] Base 4% | Casilla 01 | Total de ventas gravadas al 4% (sin IVA) |
| [03] Cuota 4% | Casilla 03 | IVA cobrado al 4% |
| [27] Total Devengado | Casilla 27 | Suma de todas las cuotas de IVA cobradas |

### IVA Deducible (Lo que pagamos a proveedores)

| Columna en Reporte | Casilla AEAT | Qué significa |
|--------------------|--------------|---------------|
| [28] Base 21% Ded | Casilla 28 | Total de compras gravadas al 21% (sin IVA) |
| [29] Cuota 21% Ded | Casilla 29 | IVA pagado al 21% |
| [28] Base 10% Ded | Casilla 28 | Total de compras gravadas al 10% (sin IVA) |
| [29] Cuota 10% Ded | Casilla 29 | IVA pagado al 10% |
| [28] Base 4% Ded | Casilla 28 | Total de compras gravadas al 4% (sin IVA) |
| [29] Cuota 4% Ded | Casilla 29 | IVA pagado al 4% |
| [45] Total Deducible | Casilla 45 | Suma de todo el IVA que podemos deducir |

### Resultado

| Columna en Reporte | Casilla AEAT | Qué significa |
|--------------------|--------------|---------------|
| [46] Diferencia | Casilla 46 | Total Devengado - Total Deducible |

**Interpretación del resultado:**
- **Diferencia positiva**: Debemos ingresar ese importe a Hacienda
- **Diferencia negativa**: Podemos compensar en próximos trimestres o solicitar devolución

---

## Cómo se Calculan los Importes

### Fórmula para el IVA Repercutido (Grupo 477 - Ventas)

```
Cuota IVA = Créditos de la cuenta - Débitos de la cuenta
```

- Cuando emitimos una factura de venta, el IVA se registra como **crédito** en la cuenta 477.
- Si hay una factura rectificativa (abono), se registra como **débito**.
- El reporte suma todo y calcula el neto.

### Fórmula para el IVA Soportado (Grupo 472 - Compras)

```
Cuota IVA = Débitos de la cuenta - Créditos de la cuenta
```

- Cuando recibimos una factura de compra, el IVA se registra como **débito** en la cuenta 472.
- Si hay una factura rectificativa del proveedor, se registra como **crédito**.
- El reporte suma todo y calcula el neto.

### Cálculo de la Base Imponible

La base imponible se calcula automáticamente a partir de la cuota:

```
Base Imponible = Cuota IVA / (Tipo IVA / 100)
```

Por ejemplo:
- Si la cuota de IVA al 21% es 2.100 €
- La base imponible = 2.100 / 0,21 = 10.000 €

---

## Filtros Disponibles

Al ejecutar el reporte, puede filtrar por:

| Filtro | Descripción | Ejemplo |
|--------|-------------|---------|
| **Compañía** | Empresa para la que se genera el reporte | INDEX BUSINESS INTELLIGENT S.L. |
| **Año Fiscal** | Ejercicio contable | 2025 |
| **Trimestre** | Período del modelo 303 | 1T, 2T, 3T, 4T |

### Períodos y sus fechas

| Trimestre | Fecha Inicio | Fecha Fin | Plazo presentación AEAT |
|-----------|--------------|-----------|-------------------------|
| 1T | 1 enero | 31 marzo | 1-20 abril |
| 2T | 1 abril | 30 junio | 1-20 julio |
| 3T | 1 julio | 30 septiembre | 1-20 octubre |
| 4T | 1 octubre | 31 diciembre | 1-30 enero |

---

## Ejemplo Práctico

### Datos del 4T 2025 - INDEX BUSINESS INTELLIGENT S.L.

| Concepto | Importe |
|----------|---------|
| **IVA DEVENGADO** | |
| Base imponible 21% | 2.326.208,86 € |
| Cuota 21% | 488.503,86 € |
| Base imponible 10% | 23,80 € |
| Cuota 10% | 2,38 € |
| **Total IVA Devengado** | **488.506,24 €** |
| | |
| **IVA DEDUCIBLE** | |
| Base imponible 21% | 1.203.712,02 € |
| Cuota 21% | 252.779,53 € |
| Base imponible 10% | 23.334,33 € |
| Cuota 10% | 2.333,43 € |
| Base imponible 4% | 5.210,77 € |
| Cuota 4% | 208,43 € |
| **Total IVA Deducible** | **255.321,39 €** |
| | |
| **DIFERENCIA (a ingresar)** | **233.184,85 €** |

---

## Preguntas Frecuentes

### ¿Por qué el importe no coincide con mis facturas?

El reporte usa el **Libro Mayor (GL Entry)**, que puede incluir:
- Ajustes manuales mediante asientos contables
- Regularizaciones de IVA
- Facturas rectificativas que modifican importes anteriores

Si hay discrepancias, revise los asientos manuales del período en las cuentas 472 y 477.

### ¿Se incluyen las facturas rectificativas (abonos)?

**Sí**. Las facturas rectificativas se incluyen automáticamente porque:
- En ventas: reducen el IVA repercutido (aparecen como débito en cuenta 477)
- En compras: reducen el IVA soportado (aparecen como crédito en cuenta 472)

El reporte calcula el **neto** de todos los movimientos.

### ¿Qué pasa con las operaciones de Inversión del Sujeto Pasivo?

Las operaciones de Inversión del Sujeto Pasivo (ISP) se registran en cuentas específicas:
- 472022100 - H.P. IVA SOPORTADO SUJETO PASIVO
- 477022100 - H.P. IVA REPERCUTIDO SUJETO PASIVO

Estas cuentas se incluyen en el cálculo del reporte y aparecen agrupadas con el tipo impositivo del 21%.

### ¿Por qué veo cuentas con "PTE DEDUCIR"?

Algunas cuentas como "IVA SOPORTADO 21% - PTE DEDUCIR" representan IVA pendiente de deducir (por ejemplo, por criterio de caja). Estas cuentas también se incluyen en el cálculo.

### ¿Cómo verifico que los datos son correctos?

Puede comparar con:
1. **Libro de Facturas por Empresas**: Debe coincidir ya que usa la misma fuente de datos
2. **Balance de Sumas y Saldos**: Revisar los saldos de las cuentas 472 y 477
3. **Listado de GL Entry**: Filtrar por cuentas 472% y 477% en el período

---

## Información Técnica (para administradores)

### Ubicación del código
```
apps/spain_account/spain_account/spain_accounting/report/modelo_303/modelo_303.py
```

### DocTypes relacionados en ERPNext
- **GL Entry**: Asientos del libro mayor (fuente principal de datos)
- **Account**: Cuentas contables (para filtrar por grupo 472/477)
- **Fiscal Year**: Ejercicios fiscales (para determinar fechas)
- **Company**: Empresas (para filtrar por compañía)

### Consulta principal del reporte
El reporte ejecuta una consulta SQL que:
1. Busca todas las cuentas con `account_number LIKE '472%'` o `'477%'`
2. Obtiene los movimientos (GL Entry) de esas cuentas en el período
3. Agrupa por tipo de IVA (extraído del nombre de la cuenta)
4. Calcula cuotas (crédito-débito o débito-crédito según el grupo)
5. Calcula bases imponibles dividiendo la cuota entre el tipo

---

**Documento generado el**: Febrero 2026  
**Versión del reporte**: 1.0  
**Aplicación**: spain_account  
