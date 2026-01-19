# Spain Account - README Técnico

## Información General

**App:** Spain Account
**Versión:** 0.0.1
**Rama:** main
**Repositorio:** [Xappiens/Spain_Account](https://github.com/Xappiens/Spain_Account)
**Tamaño:** 1.4M
**Tipo:** Contabilidad Específica para España

---

## Descripción

Spain Account es el módulo de contabilidad específico para España del proyecto ERA Digital Murcia desarrollado para Grupo ATU. Proporciona funcionalidades completas para la gestión contable según la normativa española, incluyendo el Plan General de Contabilidad, modelos fiscales y el Suministro Inmediato de Información (SII).

### Características Principales
- **Plan de Cuentas Español:** Plan General de Contabilidad
- **Modelos Fiscales:** Modelos 303, 115, 180, 190, 347, 349, 390
- **SII Integration:** Suministro Inmediato de Información
- **Asientos Contables:** Asientos específicos para España
- **Reportes Fiscales:** Reportes para Hacienda
- **Validaciones:** Validaciones según normativa española
- **Integración:** Integración con ERPNext

---

## Estructura de la App

```
spain_account/
├── spain_account/          # Módulo principal de contabilidad española
│   ├── spain_account/     # Submódulo principal
│   │   ├── doctype/       # Doctypes del sistema contable
│   │   │   ├── modelo_180/ # Modelo 180
│   │   │   ├── modelo_190/ # Modelo 190
│   │   │   ├── modelo_303/ # Modelo 303
│   │   │   ├── modelo_347/ # Modelo 347
│   │   │   ├── modelo_349/ # Modelo 349
│   │   │   ├── modelo_390/ # Modelo 390
│   │   │   ├── asiento_diario_desigual/ # Asientos desiguales
│   │   │   └── [otros]     # Doctypes adicionales
│   │   ├── api/           # APIs de contabilidad
│   │   ├── utils/         # Utilidades
│   │   ├── report/        # Reportes
│   │   └── [otros módulos] # Módulos adicionales
│   └── [otros módulos]    # Módulos adicionales
├── pyproject.toml         # Configuración Python
├── hooks.py              # Configuración de hooks
└── [archivos de config]  # Archivos de configuración
```

---

## Doctypes Principales

### Modelo 180
- **Descripción:** Modelo 180 - Retenciones e ingresos a cuenta
- **Funcionalidades:**
  - Generación automática
  - Validaciones fiscales
  - Exportación a Hacienda
  - Cálculos automáticos
- **Campos Principales:**
  - Período
  - Retenciones
  - Ingresos
  - Estado
  - Fecha de presentación

### Modelo 190
- **Descripción:** Modelo 190 - Retenciones e ingresos a cuenta
- **Funcionalidades:**
  - Generación automática
  - Validaciones fiscales
  - Exportación a Hacienda
  - Cálculos automáticos
- **Campos Principales:**
  - Período
  - Retenciones
  - Ingresos
  - Estado
  - Fecha de presentación

### Modelo 303
- **Descripción:** Modelo 303 - Declaración del IVA
- **Funcualidades:**
  - Generación automática
  - Validaciones fiscales
  - Exportación a Hacienda
  - Cálculos automáticos
- **Campos Principales:**
  - Período
  - IVA devengado
  - IVA deducible
  - Resultado
  - Estado

### Modelo 347
- **Descripción:** Modelo 347 - Declaración anual de operaciones
- **Funcionalidades:**
  - Generación automática
  - Validaciones fiscales
  - Exportación a Hacienda
  - Cálculos automáticos
- **Campos Principales:**
  - Período
  - Operaciones
  - Importes
  - Estado
  - Fecha de presentación

### Modelo 349
- **Descripción:** Modelo 349 - Declaración de operaciones intracomunitarias
- **Funcionalidades:**
  - Generación automática
  - Validaciones fiscales
  - Exportación a Hacienda
  - Cálculos automáticos
- **Campos Principales:**
  - Período
  - Operaciones
  - Importes
  - Estado
  - Fecha de presentación

### Modelo 390
- **Descripción:** Modelo 390 - Resumen anual del IVA
- **Funcionalidades:**
  - Generación automática
  - Validaciones fiscales
  - Exportación a Hacienda
  - Cálculos automáticos
- **Campos Principales:**
  - Período
  - Resumen
  - Importes
  - Estado
  - Fecha de presentación

### Asiento Diario Desigual
- **Descripción:** Asientos contables desiguales
- **Funcionalidades:**
  - Detección automática
  - Corrección automática
  - Validaciones
  - Reportes
- **Campos Principales:**
  - Fecha
  - Asiento
  - Diferencia
  - Estado
  - Corrección

---

## Configuración y Hooks

### hooks.py
```python
app_name = "spain_account"
app_title = "Spain Accounting"
app_publisher = "Xappiens"
app_description = "This app is designed to seamlessly integrate with ERPNext, enabling businesses to effortlessly establish and manage the Spanish chart of accounts. Comply with local accounting standards (Plan General de Contabilidad) and streamline your financial processes with this essential tool. Simplify the setup of your financial structure, ensuring accurate and compliant reporting according to Spanish regulations. Perfect for businesses operating in Spain, this extension brings precision and ease to your ERPNext system, making accounting management more efficient and reliable."
app_email = "xappiens@xappiens.com"
app_license = "mit"

# Override methods
override_whitelisted_methods = {
    "erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts.get_chart": "spain_account.spain_accounting.chart_of_accounts_loader.get_chart",
    "erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts.get_charts_for_country": "spain_account.spain_accounting.chart_of_accounts_loader.get_charts_for_country"
}
```

### Características Especiales
- **Licencia:** MIT
- **Publisher:** Xappiens
- **Email:** xappiens@xappiens.com
- **Override Methods:** Sobrescribe métodos de ERPNext
- **Chart of Accounts:** Plan de cuentas español

---

## Dependencias

### Python
- **Frappe Framework:** Framework base
- **ERPNext:** Sistema ERP base
- **MariaDB:** Base de datos principal

### Funcionalidades Adicionales
- **Chart of Accounts:** Plan de cuentas español
- **Fiscal Reports:** Reportes fiscales
- **SII Integration:** Integración con SII
- **Validation:** Validaciones fiscales

---

## Desarrollo y Customización

### Estructura de Desarrollo
```bash
# Navegar a la app
cd /home/frappe/frappe-bench/apps/spain_account

# Activar entorno virtual
source ../env/bin/activate

# Instalar dependencias de desarrollo
pip install -e .
```

### Comandos de Desarrollo
```bash
# Migrar doctypes
bench --site erp.grupoatu.com migrate

# Crear fixtures
bench --site erp.grupoatu.com make-fixture

# Ejecutar tests
python -m pytest
```

### Customizaciones Específicas del Proyecto

#### Modificaciones Realizadas
1. **Plan de Cuentas:** Adaptado para España
2. **Modelos Fiscales:** Específicos para España
3. **Validaciones:** Según normativa española
4. **Reportes:** Reportes para Hacienda

#### Archivos de Customización
- `spain_account/spain_account/doctype/` - Doctypes personalizados
- `spain_account/spain_account/api/` - APIs personalizadas
- `spain_account/spain_account/utils/` - Utilidades personalizadas
- `spain_account/spain_account/report/` - Reportes personalizados

---

## API y Endpoints

### Endpoints Principales
```bash
# Modelos Fiscales
GET    /api/resource/Modelo 180
POST   /api/resource/Modelo 180
GET    /api/resource/Modelo 180/{name}

GET    /api/resource/Modelo 190
POST   /api/resource/Modelo 190
GET    /api/resource/Modelo 190/{name}

GET    /api/resource/Modelo 303
POST   /api/resource/Modelo 303
GET    /api/resource/Modelo 303/{name}

# Asientos
GET    /api/resource/Asiento Diario Desigual
POST   /api/resource/Asiento Diario Desigual
GET    /api/resource/Asiento Diario Desigual/{name}

# APIs específicas
POST   /api/method/spain_account.api.generate_modelo_303
GET    /api/method/spain_account.api.get_chart_of_accounts
POST   /api/method/spain_account.api.validate_asiento
```

### Ejemplos de Uso
```python
# En consola de Frappe
>>> frappe.get_doc("Modelo 303", "MOD-001")
>>> frappe.db.sql("SELECT * FROM `tabAsiento Diario Desigual` WHERE estado='Pendiente'")
>>> frappe.get_value("Modelo 180", "MOD-001", "periodo")
```

---

## Funcionalidades Principales

### Plan de Cuentas Español
- **Configuración:** Configuración automática
- **Validación:** Validación según normativa
- **Migración:** Migración desde plan estándar
- **Personalización:** Personalización de cuentas

### Modelos Fiscales
- **Generación:** Generación automática
- **Validación:** Validaciones fiscales
- **Exportación:** Exportación a Hacienda
- **Presentación:** Presentación electrónica

### SII Integration
- **Suministro:** Suministro inmediato
- **Validación:** Validaciones automáticas
- **Exportación:** Exportación de datos
- **Seguimiento:** Seguimiento de estado

---

## Reportes Principales

### Reportes Fiscales
- **Modelo 180:** Retenciones e ingresos
- **Modelo 190:** Retenciones e ingresos
- **Modelo 303:** Declaración del IVA
- **Modelo 347:** Operaciones anuales
- **Modelo 349:** Operaciones intracomunitarias
- **Modelo 390:** Resumen anual del IVA

### Reportes Contables
- **Asientos Desiguales:** Asientos desiguales
- **Plan de Cuentas:** Plan de cuentas
- **Balance:** Balance de comprobación
- **Mayor:** Libro mayor

### Reportes de Validación
- **Validación Fiscal:** Validaciones fiscales
- **Errores de Asientos:** Errores de asientos
- **Conciliación:** Conciliación de cuentas
- **Auditoría:** Reportes de auditoría

---

## Testing

### Tests Unitarios
```bash
# Ejecutar todos los tests
python -m pytest

# Tests específicos de modelos
python -m pytest spain_account/tests/test_modelo_303.py

# Tests de asientos
python -m pytest spain_account/tests/test_asiento_diario_desigual.py

# Tests de plan de cuentas
python -m pytest spain_account/tests/test_chart_of_accounts.py
```

### Tests de Integración
```bash
# Tests de API
python -m pytest spain_account/tests/test_api.py

# Tests de validaciones
python -m pytest spain_account/tests/test_validations.py

# Tests de reportes
python -m pytest spain_account/tests/test_reports.py
```

---

## Monitoreo y Logs

### Logs Específicos
- `logs/frappe.log` - Logs principales de contabilidad
- `logs/web.log` - Logs del servidor web
- `logs/worker.log` - Logs de workers

### Métricas Importantes
- **Tiempo de respuesta:** < 200ms para operaciones
- **Uso de memoria:** Monitorear crecimiento de workers
- **Conexiones DB:** Máximo 50 conexiones simultáneas
- **Cache hit ratio:** > 85% para Redis

---

## Troubleshooting

### Problemas Comunes

#### Error de Modelos Fiscales
```bash
# Verificar modelos
bench --site erp.grupoatu.com console
>>> frappe.get_doc("Modelo 303", "MOD-001")

# Verificar configuración
>>> frappe.get_system_settings("spain_account_settings")
```

#### Problemas de Asientos
```bash
# Verificar asientos desiguales
bench --site erp.grupoatu.com console
>>> frappe.db.sql("SELECT * FROM `tabAsiento Diario Desigual` WHERE estado='Pendiente'")

# Verificar validaciones
>>> frappe.get_system_settings("enable_asiento_validation")
```

#### Problemas de Plan de Cuentas
```bash
# Verificar plan de cuentas
bench --site erp.grupoatu.com console
>>> frappe.get_doc("Account", "CUENTA-001")

# Verificar configuración
>>> frappe.get_system_settings("chart_of_accounts")
```

---

## Documentación Adicional

### Recursos Oficiales
- **Hacienda:** [https://www.agenciatributaria.es](https://www.agenciatributaria.es)
- **SII:** [https://sede.agenciatributaria.gob.es](https://sede.agenciatributaria.gob.es)
- **Documentación:** [https://github.com/Xappiens/Spain_Account](https://github.com/Xappiens/Spain_Account)

### Repositorios
- **Proyecto:** [https://github.com/Xappiens/Spain_Account](https://github.com/Xappiens/Spain_Account)

---

## Contacto y Soporte

**Desarrollador Principal:** Xappiens
**Email:** xappiens@xappiens.com
**Proyecto:** ERA Digital Murcia - Grupo ATU
**Ubicación:** `/home/frappe/frappe-bench/apps/spain_account/`

---

*Documento generado el 16 de Septiembre de 2025*
