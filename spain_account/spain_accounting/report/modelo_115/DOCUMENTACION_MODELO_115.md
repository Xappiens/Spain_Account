# Documentación del Reporte Modelo 115 - Retenciones por Arrendamientos

## Índice
1. [Descripción General](#descripción-general)
2. [¿Qué es el Modelo 115?](#qué-es-el-modelo-115)
3. [Origen de los Datos](#origen-de-los-datos)
4. [Configuración Necesaria en ERPNext](#configuración-necesaria-en-erpnext)
5. [Columnas del Reporte](#columnas-del-reporte)
6. [Cómo se Calculan los Importes](#cómo-se-calculan-los-importes)
7. [Filtros Disponibles](#filtros-disponibles)
8. [Ejemplo Práctico](#ejemplo-práctico)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Descripción General

El reporte **Modelo 115** es una herramienta que ayuda a preparar la declaración trimestral de retenciones e ingresos a cuenta sobre rentas o rendimientos procedentes del arrendamiento o subarrendamiento de inmuebles urbanos.

En términos sencillos: cuando pagamos un alquiler a un arrendador (propietario del local, oficina, etc.), debemos retenerle el **19% de IRPF** y declararlo a Hacienda mediante este modelo.

---

## ¿Qué es el Modelo 115?

### Obligados a presentar el Modelo 115

Deben presentar este modelo las empresas y autónomos que:
- Paguen alquileres de locales, oficinas, naves industriales u otros inmuebles urbanos
- Retengan el 19% de IRPF al arrendador (propietario)

### Información que se declara

Por cada arrendador (propietario) al que hayamos pagado alquiler:
- **NIF** del arrendador
- **Nombre** del arrendador
- **Código Postal** del inmueble arrendado
- **Base Imponible**: Importe del alquiler (sin IVA, sin retención)
- **Retención**: 19% del importe del alquiler

### Plazos de presentación

| Trimestre | Período | Plazo presentación |
|-----------|---------|-------------------|
| 1T | Enero - Marzo | 1-20 abril |
| 2T | Abril - Junio | 1-20 julio |
| 3T | Julio - Septiembre | 1-20 octubre |
| 4T | Octubre - Diciembre | 1-30 enero |

---

## Origen de los Datos

### ¿De dónde saca la información el reporte?

El reporte obtiene los datos de **dos fuentes principales**:

1. **Tax Withholding Category (Categoría de Retención)**
   - Busca categorías configuradas con tasa del **19%** (IRPF de arrendamientos)
   - Obtiene las **cuentas contables** asociadas a cada categoría por empresa

2. **GL Entry (Libro Mayor)**
   - Busca movimientos en las cuentas de retención del 19%
   - Identifica el proveedor (arrendador) de cada movimiento
   - Suma todas las retenciones por arrendador

### Flujo de datos

```
Tax Withholding Category (ej: "IRPF 19%")
    │
    ├── Tax Withholding Rate: 19%
    │
    └── Tax Withholding Account (por empresa)
            │
            └── Cuenta contable (ej: "475105100 - I.R.P.F. ALQUILERES")
                    │
                    └── GL Entry (movimientos del período)
                            │
                            └── Agrupado por Proveedor (Arrendador)
```

---

## Configuración Necesaria en ERPNext

Para que el reporte funcione correctamente, debe existir la siguiente configuración:

### 1. Tax Withholding Category

Debe existir una categoría de retención para alquileres con:

| Campo | Valor |
|-------|-------|
| **Nombre** | IRPF 19% (o similar) |
| **Tasa** | 19% |

### 2. Tax Withholding Rate (Tabla de tasas)

Dentro de la categoría, debe haber al menos una tasa configurada:

| Campo | Valor |
|-------|-------|
| **Tax Withholding Rate** | 19 |
| **From Date** | Fecha desde la que aplica |
| **To Date** | Fecha hasta (opcional) |

### 3. Tax Withholding Account (Tabla de cuentas)

Por cada empresa, debe configurarse la cuenta contable donde se registran las retenciones:

| Campo | Valor Ejemplo |
|-------|---------------|
| **Company** | INDEX BUSINESS INTELLIGENT S.L. |
| **Account** | 475105100 - I.R.P.F. ALQUILERES - IBI |

### ¿Dónde se configura esto en ERPNext?

1. Ir a **Configuración > Contabilidad > Tax Withholding Category**
2. Buscar o crear la categoría "IRPF 19%" (o el nombre que use su empresa)
3. Verificar que tenga:
   - Una tasa del 19% en la tabla de Rates
   - La cuenta contable correcta para cada empresa en la tabla de Accounts

---

## Columnas del Reporte

El reporte muestra una fila por cada arrendador (proveedor) al que se le haya aplicado retención del 19%:

| Columna | Descripción | Origen del dato |
|---------|-------------|-----------------|
| **Nombre del Arrendador** | Nombre del propietario del inmueble | Campo `supplier_name` del Proveedor |
| **NIF** | Identificador fiscal del arrendador | Campo `tax_id` del Proveedor |
| **Código Postal** | CP del inmueble arrendado | Campo `custom_cp` del Proveedor (o de su dirección principal) |
| **Base Imponible** | Importe del alquiler antes de retención | Calculado: Retención / 0.19 |
| **Retención (19%)** | Importe retenido al arrendador | Suma de movimientos en cuenta de retención |

---

## Cómo se Calculan los Importes

### Paso 1: Identificar las cuentas de retención

El reporte busca todas las categorías de retención (Tax Withholding Category) que tengan configurada una tasa del **19%** y obtiene las cuentas contables asociadas.

Ejemplo de cuenta: `475105100 - I.R.P.F. ALQUILERES - IBI`

### Paso 2: Obtener los movimientos del período

Se consultan todos los movimientos (GL Entry) de esas cuentas en el período seleccionado (trimestre).

### Paso 3: Identificar el arrendador

Para cada movimiento, se identifica el proveedor (arrendador) de tres formas:
1. Si el GL Entry tiene `party_type = 'Supplier'`, usa ese proveedor
2. Si viene de una Factura de Compra (Purchase Invoice), obtiene el proveedor de la factura
3. Si viene de un Pago (Payment Entry), obtiene el proveedor del pago

### Paso 4: Calcular la retención neta

Por cada arrendador, se suman todos los movimientos:

```
Retención Neta = Total Créditos - Total Débitos
```

- **Créditos**: Retenciones aplicadas en facturas normales
- **Débitos**: Retenciones devueltas por facturas rectificativas (abonos)

### Paso 5: Calcular la base imponible

La base imponible se calcula a partir de la retención:

```
Base Imponible = Retención Neta / 0.19
```

Por ejemplo:
- Si la retención es 1.900 €
- La base imponible = 1.900 / 0.19 = 10.000 €

### Paso 6: Filtrar resultados

Solo se muestran arrendadores con **retención neta positiva**. Si un arrendador tiene más abonos que facturas en el período, no aparece en el reporte.

---

## Filtros Disponibles

| Filtro | Descripción | Ejemplo |
|--------|-------------|---------|
| **Compañía** | Empresa para la que se genera el reporte | INDEX BUSINESS INTELLIGENT S.L. |
| **Año Fiscal** | Ejercicio contable | 2025 |
| **Trimestre** | Período del modelo 115 | 1T, 2T, 3T, 4T |

---

## Ejemplo Práctico

### Escenario

La empresa INDEX BUSINESS INTELLIGENT S.L. alquila un local a "EMPRESA MALAGUEÑA DE SOCORRISMO Y ESPECTACULO DE ANIMACION S.L." durante el 4T de 2025.

### Movimientos en el período

| Fecha | Documento | Concepto | Crédito | Débito |
|-------|-----------|----------|---------|--------|
| 01/10/2025 | Factura alquiler octubre | Retención 19% | 454,86 € | - |
| 01/11/2025 | Factura alquiler noviembre | Retención 19% | 287,28 € | - |
| 01/12/2025 | Factura alquiler diciembre | Retención 19% | 359,10 € | - |
| 16/12/2025 | Abono parcial | Rectificación | - | 69,43 € |
| **TOTAL** | | | **2.520,54 €** | **331,40 €** |

### Cálculo

```
Retención Neta = 2.520,54 - 331,40 = 2.189,14 €
Base Imponible = 2.189,14 / 0.19 = 11.521,79 €
```

### Resultado en el reporte

| Arrendador | NIF | CP | Base Imponible | Retención |
|------------|-----|-----|----------------|-----------|
| EMPRESA MALAGUEÑA DE SOCORRISMO... | B93579332 | 29XXX | 11.521,79 € | 2.189,14 € |

---

## Preguntas Frecuentes

### ¿Por qué no aparece un arrendador en el reporte?

Posibles causas:
1. **No tiene retención del 19%**: Verifique que la factura tiene aplicada la categoría de retención correcta
2. **La cuenta no está configurada**: Verifique que la Tax Withholding Category tiene la cuenta contable para su empresa
3. **La tasa no es 19%**: El reporte solo muestra retenciones al 19%
4. **Retención neta negativa**: Si hay más abonos que facturas, el arrendador no aparece

### ¿Por qué el importe no coincide con mis facturas?

El reporte usa el **Libro Mayor (GL Entry)**, que incluye:
- Todas las facturas de compra con retención
- Facturas rectificativas (abonos) que reducen la retención
- Posibles ajustes manuales

El importe mostrado es el **neto** de todos los movimientos.

### ¿De dónde sale el Código Postal?

El reporte busca el código postal en este orden:
1. **Campo `custom_cp`** en la ficha del Proveedor (Supplier)
2. **Dirección principal** del proveedor (campo `pincode` de la Address marcada como principal)

Si no encuentra ninguno, la columna aparece vacía.

### ¿Se incluyen las facturas rectificativas?

**Sí**. Las facturas rectificativas (abonos) se restan automáticamente de la retención total. Esto es importante porque:
- Si se anuló un alquiler, la retención también se anula
- El reporte muestra el importe **neto** real que debe declararse

### ¿Qué pasa si un proveedor tiene varios inmuebles?

El reporte agrupa todas las retenciones por proveedor, independientemente del número de inmuebles. Si necesita desglose por inmueble, debería crear proveedores separados o usar el campo de código postal del inmueble.

### ¿Por qué la categoría de retención debe ser exactamente 19%?

El Modelo 115 es específico para retenciones de arrendamientos urbanos, que en España tributan al 19%. Si su empresa usa otra tasa (por ejemplo, en Canarias con IGIC), necesitaría adaptar el reporte.

---

## Información Técnica (para administradores)

### Ubicación del código
```
apps/spain_account/spain_account/spain_accounting/report/modelo_115/modelo_115.py
```

### DocTypes relacionados en ERPNext

| DocType | Descripción | Uso en el reporte |
|---------|-------------|-------------------|
| **Tax Withholding Category** | Categorías de retención (IRPF) | Identifica categorías con tasa 19% |
| **Tax Withholding Rate** | Tasas de retención (tabla hija) | Filtra por tasa = 19% |
| **Tax Withholding Account** | Cuentas por empresa (tabla hija) | Obtiene las cuentas contables |
| **GL Entry** | Asientos del libro mayor | Fuente principal de datos |
| **Supplier** | Proveedores (arrendadores) | Datos del arrendador (nombre, NIF) |
| **Address** | Direcciones | Código postal del inmueble |
| **Purchase Invoice** | Facturas de compra | Para identificar el proveedor |
| **Payment Entry** | Pagos | Para identificar el proveedor |

### Consulta principal

El reporte ejecuta una consulta SQL que:
1. Busca movimientos en cuentas de Tax Withholding Account donde la categoría tenga tasa 19%
2. Hace JOIN con Purchase Invoice y Payment Entry para obtener el proveedor
3. Agrupa por proveedor sumando créditos y débitos
4. Calcula retención neta (créditos - débitos) y base imponible (retención / 0.19)
5. Obtiene datos del proveedor (nombre, NIF, CP)

### Cuentas contables típicas

| Cuenta | Descripción |
|--------|-------------|
| 4751 | H.P. Acreedora por retenciones practicadas (grupo padre) |
| 475105100 | I.R.P.F. ALQUILERES (subcuenta específica) |

---

## Diferencia con el Modelo 111

| Aspecto | Modelo 115 | Modelo 111 |
|---------|------------|------------|
| **Concepto** | Retenciones por arrendamientos | Retenciones por trabajo y profesionales |
| **Tipo retención** | 19% | 15% y 7% |
| **Arrendadores/Profesionales** | Propietarios de inmuebles | Autónomos y profesionales |
| **Cuenta contable típica** | 475105100 (IRPF Alquileres) | 4751XXXXX (otras retenciones) |

---

**Documento generado el**: Febrero 2026  
**Versión del reporte**: 1.0  
**Aplicación**: spain_account
