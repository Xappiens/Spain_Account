"""
Script para copiar el catálogo de cuentas (solo grupos) de una empresa modelo
a ESTUDIA FP ONLINE, S.L.

Ejecutar con:
bench --site erp.grupoatu.com execute spain_account.copy_chart_to_estudia.copy_accounts
"""
import re
import frappe

# Configuración
MODEL_COMPANY = "ASOCIACIÓN SOCIOCULTURAL DE AVENTURA ATU"
MODEL_COMPANY_ABBR = "ASA"
TARGET_COMPANY = "ESTUDIA FP ONLINE, S.L."
TARGET_COMPANY_ABBR = "EFPO"


def clean_account_name(account_name, abbr_to_remove):
    """
    Limpia el account_name eliminando el sufijo de abreviatura.
    "Financiación básica - ASA" -> "Financiación básica"
    """
    if not account_name:
        return account_name
    
    # Eliminar el sufijo específico de la abreviatura
    pattern = rf'\s*-\s*{re.escape(abbr_to_remove)}$'
    cleaned = re.sub(pattern, '', account_name)
    
    return cleaned.strip()


def copy_accounts():
    """
    Copia los grupos de cuentas de la empresa modelo a la empresa destino.
    Limpia los nombres de cuentas para quitar la abreviatura de la empresa modelo.
    """
    # Verificar que la empresa destino existe
    if not frappe.db.exists("Company", TARGET_COMPANY):
        print(f"ERROR: Empresa destino '{TARGET_COMPANY}' no encontrada")
        return False
    
    # Verificar que no tiene cuentas ya
    existing = frappe.db.count("Account", {"company": TARGET_COMPANY})
    if existing > 0:
        print(f"ADVERTENCIA: La empresa ya tiene {existing} cuentas. Continuando...")
    
    # Obtener moneda de la empresa destino
    currency = frappe.db.get_value("Company", TARGET_COMPANY, "default_currency") or "EUR"
    
    # Obtener todos los grupos de cuentas de la empresa modelo
    # Ordenados por nivel para crear padres antes que hijos
    model_accounts = frappe.db.sql("""
        SELECT 
            account_name,
            account_number,
            is_group,
            root_type,
            account_type,
            report_type,
            parent_account,
            balance_must_be,
            freeze_account,
            include_in_gross
        FROM tabAccount 
        WHERE company = %s 
        AND is_group = 1
        AND account_number IS NOT NULL
        AND account_number != ''
        ORDER BY 
            LENGTH(account_number),
            account_number
    """, (MODEL_COMPANY,), as_dict=True)
    
    print(f"Encontrados {len(model_accounts)} grupos de cuentas en '{MODEL_COMPANY}'")
    
    # Diccionario para mapear account_number -> nuevo name
    # Esto nos permite calcular correctamente los parent_account
    account_name_map = {}
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for account in model_accounts:
        try:
            # Verificar si ya existe
            existing = frappe.db.exists("Account", {
                "account_number": account.account_number,
                "company": TARGET_COMPANY
            })
            
            if existing:
                skipped_count += 1
                continue
            
            # Limpiar el account_name quitando la abreviatura de la empresa modelo
            clean_name = clean_account_name(account.account_name, MODEL_COMPANY_ABBR)
            
            # Calcular el nuevo parent_account
            new_parent = None
            if account.parent_account:
                # El parent_account original tiene formato: "X - Nombre - ASA"
                # Lo reemplazamos por el nuevo name que calculamos
                # Extraer el account_number del parent
                parent_match = re.match(r'^(\d+)\s*-', account.parent_account)
                if parent_match:
                    parent_number = parent_match.group(1)
                    if parent_number in account_name_map:
                        new_parent = account_name_map[parent_number]
            
            # Crear la nueva cuenta
            new_account = frappe.new_doc("Account")
            new_account.account_name = clean_name
            new_account.account_number = account.account_number
            new_account.is_group = 1
            new_account.company = TARGET_COMPANY
            new_account.parent_account = new_parent
            new_account.root_type = account.root_type
            new_account.account_type = account.account_type or ""
            new_account.report_type = account.report_type
            new_account.account_currency = currency
            new_account.balance_must_be = account.balance_must_be or ""
            new_account.freeze_account = account.freeze_account or ""
            new_account.include_in_gross = account.include_in_gross or 0
            
            new_account.flags.ignore_permissions = True
            new_account.flags.ignore_mandatory = True
            new_account.insert()
            
            # Guardar el name generado para usarlo como parent de las cuentas hijas
            account_name_map[account.account_number] = new_account.name
            
            created_count += 1
            
            if created_count % 100 == 0:
                print(f"  Creadas {created_count} cuentas...")
                frappe.db.commit()
            
        except Exception as e:
            error_count += 1
            if error_count <= 10:
                print(f"ERROR creando {account.account_number} - {account.account_name}: {str(e)}")
    
    frappe.db.commit()
    
    print(f"\n=== RESULTADO ===")
    print(f"Cuentas creadas: {created_count}")
    print(f"Cuentas omitidas (ya existían): {skipped_count}")
    print(f"Errores: {error_count}")
    
    return error_count == 0


if __name__ == "__main__":
    copy_accounts()
