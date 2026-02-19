# Copyright (c) 2024, Xappiens and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, flt, nowdate
from erpnext.accounts.utils import get_fiscal_year

UMBRAL_MODELO_347 = 3005.06


def execute(filters=None):
    """
    Ejecuta el reporte Modelo 347.
    
    El Modelo 347 es la Declaración Anual de Operaciones con Terceras Personas.
    Es obligatorio declarar operaciones con terceros que superen 3.005,06€ (IVA incluido)
    durante el año natural. La información se desglosa trimestralmente.
    
    Fuente de datos:
    - Purchase Invoice (facturas de compra) -> Proveedores (excluye rectificativas)
    - Sales Invoice (facturas de venta) -> Clientes (excluye abonos)
    """
    filters = prepare_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def prepare_filters(filters):
    """Prepara los filtros con valores por defecto si no se especifican."""
    filters = frappe._dict(filters or {})
    filters.setdefault("company", frappe.defaults.get_defaults().get("company"))
    filters.setdefault("fiscal_year", get_fiscal_year(nowdate(), as_dict=True).get("name"))
    
    fiscal_year_dates = frappe.db.get_value(
        "Fiscal Year", 
        filters.fiscal_year, 
        ["year_start_date", "year_end_date"],
        as_dict=True
    )
    if fiscal_year_dates:
        filters.from_date = fiscal_year_dates.year_start_date
        filters.to_date = fiscal_year_dates.year_end_date
    
    return filters


def get_columns():
    """
    Define las columnas del reporte Modelo 347.
    
    Columnas necesarias para la presentación del modelo:
    - Tipo de tercero (Cliente/Proveedor)
    - NIF del tercero
    - Nombre/Razón social
    - Código Postal (provincia)
    - Clave de operación
    - Importes trimestrales (T1, T2, T3, T4)
    - Importe anual total
    """
    return [
        {
            "label": _("Tipo"),
            "fieldname": "party_type",
            "fieldtype": "Data",
            "width": 90,
        },
        {
            "label": _("Clave"),
            "fieldname": "clave_operacion",
            "fieldtype": "Data",
            "width": 60,
            "align": "center",
        },
        {
            "label": _("NIF"),
            "fieldname": "nif",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Nombre/Razón Social"),
            "fieldname": "party_name",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Provincia"),
            "fieldname": "provincia",
            "fieldtype": "Data",
            "width": 60,
            "align": "center",
        },
        {
            "label": _("1T"),
            "fieldname": "t1",
            "fieldtype": "Currency",
            "width": 110,
            "precision": 2,
        },
        {
            "label": _("2T"),
            "fieldname": "t2",
            "fieldtype": "Currency",
            "width": 110,
            "precision": 2,
        },
        {
            "label": _("3T"),
            "fieldname": "t3",
            "fieldtype": "Currency",
            "width": 110,
            "precision": 2,
        },
        {
            "label": _("4T"),
            "fieldname": "t4",
            "fieldtype": "Currency",
            "width": 110,
            "precision": 2,
        },
        {
            "label": _("Total Anual"),
            "fieldname": "total",
            "fieldtype": "Currency",
            "width": 130,
            "precision": 2,
        },
        {
            "label": _("Teléfono"),
            "fieldname": "telefono",
            "fieldtype": "Data",
            "width": 110,
        },
        {
            "label": _("Email"),
            "fieldname": "email",
            "fieldtype": "Data",
            "width": 180,
        },
    ]


def get_data(filters):
    """
    Obtiene los datos del reporte Modelo 347.
    
    Fuentes:
    1. Purchase Invoice -> Proveedores (excluyendo rectificativas: is_return = 1)
    2. Sales Invoice -> Clientes (excluyendo abonos: is_return = 1)
    
    Proceso:
    1. Obtiene todas las facturas del período
    2. Agrupa por tercero
    3. Calcula importes trimestrales basándose en los GL Entry de cada factura
    4. Filtra por umbral mínimo de 3.005,06€
    """
    company = filters.company
    from_date = filters.from_date
    to_date = filters.to_date
    party_type_filter = filters.get("party_type")
    
    results = {}
    
    # Procesar facturas de compra (Proveedores)
    if not party_type_filter or party_type_filter == "Supplier":
        purchase_data = get_purchase_invoice_data(company, from_date, to_date)
        merge_data(results, purchase_data, "Supplier")
    
    # Procesar facturas de venta (Clientes)
    if not party_type_filter or party_type_filter == "Customer":
        sales_data = get_sales_invoice_data(company, from_date, to_date)
        merge_data(results, sales_data, "Customer")
    
    # Convertir a lista y filtrar por umbral
    final_results = []
    for key, data in results.items():
        total = flt(data["t1"] + data["t2"] + data["t3"] + data["t4"], 2)
        
        if total < UMBRAL_MODELO_347:
            continue
        
        party_type_code = data["party_type_code"]
        
        # Obtener datos del tercero
        party_info = get_party_info(data["party"], party_type_code, company)
        
        final_results.append({
            "party_type": _("Proveedor") if party_type_code == "Supplier" else _("Cliente"),
            "party_type_code": party_type_code,
            "clave_operacion": "A" if party_type_code == "Supplier" else "B",
            "nif": party_info.get("nif", ""),
            "party_name": party_info.get("name", data["party"]),
            "provincia": party_info.get("provincia", ""),
            "t1": flt(data["t1"], 2),
            "t2": flt(data["t2"], 2),
            "t3": flt(data["t3"], 2),
            "t4": flt(data["t4"], 2),
            "total": total,
            "telefono": party_info.get("telefono", ""),
            "email": party_info.get("email", ""),
        })
    
    # Ordenar por tipo y nombre
    final_results = sorted(final_results, key=lambda x: (x["party_type"], x["party_name"]))
    
    return final_results


def get_purchase_invoice_data(company, from_date, to_date):
    """
    Obtiene los datos de las facturas de compra.
    
    - Incluye todas las Purchase Invoice del período
    - EXCLUYE las facturas rectificativas (is_return = 1)
    - EXCLUYE las facturas marcadas con custom_347 = 1
    - Obtiene los importes de los GL Entry asociados
    """
    # Obtener facturas de compra (excluyendo rectificativas y excluidas del 347)
    invoices = frappe.db.sql("""
        SELECT 
            pi.name,
            pi.supplier,
            pi.posting_date,
            pi.grand_total,
            pi.credit_to
        FROM `tabPurchase Invoice` pi
        WHERE pi.company = %(company)s
          AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
          AND pi.docstatus = 1
          AND pi.is_return = 0
          AND IFNULL(pi.custom_347, 0) = 0
    """, {
        "company": company,
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=True)
    
    if not invoices:
        return {}
    
    # Agrupar por proveedor y trimestre
    data = {}
    invoice_names = [inv.name for inv in invoices]
    
    # Obtener los GL Entry de las facturas para calcular el importe real
    gl_entries = get_gl_entries_for_invoices(invoice_names, "Purchase Invoice", company)
    
    for invoice in invoices:
        supplier = invoice.supplier
        if not supplier:
            continue
        
        posting_date = getdate(invoice.posting_date)
        quarter = get_quarter(posting_date.month)
        
        # Obtener el importe del GL Entry (credit en cuenta de proveedor)
        amount = get_invoice_amount_from_gl(
            gl_entries, 
            invoice.name, 
            invoice.credit_to,
            "credit"
        )
        
        # Si no hay GL Entry, usar grand_total
        if amount == 0:
            amount = flt(invoice.grand_total)
        
        if supplier not in data:
            data[supplier] = {"t1": 0, "t2": 0, "t3": 0, "t4": 0}
        
        data[supplier][f"t{quarter}"] += amount
    
    return data


def get_sales_invoice_data(company, from_date, to_date):
    """
    Obtiene los datos de las facturas de venta.
    
    - Incluye todas las Sales Invoice del período
    - EXCLUYE las facturas de abono (is_return = 1)
    - EXCLUYE las facturas marcadas con custom_347 = 1
    - Obtiene los importes de los GL Entry asociados
    """
    # Obtener facturas de venta (excluyendo abonos y excluidas del 347)
    invoices = frappe.db.sql("""
        SELECT 
            si.name,
            si.customer,
            si.posting_date,
            si.grand_total,
            si.debit_to
        FROM `tabSales Invoice` si
        WHERE si.company = %(company)s
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          AND si.docstatus = 1
          AND si.is_return = 0
          AND IFNULL(si.custom_347, 0) = 0
    """, {
        "company": company,
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=True)
    
    if not invoices:
        return {}
    
    # Agrupar por cliente y trimestre
    data = {}
    invoice_names = [inv.name for inv in invoices]
    
    # Obtener los GL Entry de las facturas para calcular el importe real
    gl_entries = get_gl_entries_for_invoices(invoice_names, "Sales Invoice", company)
    
    for invoice in invoices:
        customer = invoice.customer
        if not customer:
            continue
        
        posting_date = getdate(invoice.posting_date)
        quarter = get_quarter(posting_date.month)
        
        # Obtener el importe del GL Entry (debit en cuenta de cliente)
        amount = get_invoice_amount_from_gl(
            gl_entries, 
            invoice.name, 
            invoice.debit_to,
            "debit"
        )
        
        # Si no hay GL Entry, usar grand_total
        if amount == 0:
            amount = flt(invoice.grand_total)
        
        if customer not in data:
            data[customer] = {"t1": 0, "t2": 0, "t3": 0, "t4": 0}
        
        data[customer][f"t{quarter}"] += amount
    
    return data


def get_gl_entries_for_invoices(invoice_names, voucher_type, company):
    """Obtiene los GL Entry asociados a las facturas."""
    if not invoice_names:
        return []
    
    return frappe.db.sql("""
        SELECT 
            voucher_no,
            account,
            debit,
            credit
        FROM `tabGL Entry`
        WHERE voucher_type = %(voucher_type)s
          AND voucher_no IN %(invoice_names)s
          AND company = %(company)s
          AND is_cancelled = 0
    """, {
        "voucher_type": voucher_type,
        "invoice_names": invoice_names,
        "company": company
    }, as_dict=True)


def get_invoice_amount_from_gl(gl_entries, invoice_name, party_account, field):
    """
    Obtiene el importe de la factura desde los GL Entry.
    
    - Para Purchase Invoice: suma el credit de la cuenta credit_to (cuenta de proveedor)
    - Para Sales Invoice: suma el debit de la cuenta debit_to (cuenta de cliente)
    """
    amount = 0
    for entry in gl_entries:
        if entry.voucher_no == invoice_name and entry.account == party_account:
            amount += flt(entry.get(field, 0))
    return amount


def get_quarter(month):
    """Devuelve el trimestre (1-4) según el mes."""
    if month <= 3:
        return 1
    elif month <= 6:
        return 2
    elif month <= 9:
        return 3
    else:
        return 4


def merge_data(results, new_data, party_type_code):
    """Combina los datos de facturas en el diccionario de resultados."""
    for party, quarters in new_data.items():
        key = (party, party_type_code)
        if key not in results:
            results[key] = {
                "party": party,
                "party_type_code": party_type_code,
                "t1": 0,
                "t2": 0,
                "t3": 0,
                "t4": 0,
            }
        
        results[key]["t1"] += quarters.get("t1", 0)
        results[key]["t2"] += quarters.get("t2", 0)
        results[key]["t3"] += quarters.get("t3", 0)
        results[key]["t4"] += quarters.get("t4", 0)


def get_party_info(party, party_type_code, company):
    """Obtiene la información del tercero (NIF, nombre, dirección, contacto)."""
    info = {
        "nif": "",
        "name": party,
        "provincia": "",
        "telefono": "",
        "email": "",
    }
    
    if party_type_code == "Supplier":
        supplier_data = frappe.db.get_value(
            "Supplier", party,
            ["tax_id", "supplier_name", "custom_cp"],
            as_dict=True
        )
        if supplier_data:
            info["nif"] = supplier_data.tax_id or ""
            info["name"] = supplier_data.supplier_name or party
            info["provincia"] = (supplier_data.custom_cp or "")[:2] if supplier_data.custom_cp else ""
    else:
        customer_data = frappe.db.get_value(
            "Customer", party,
            ["tax_id", "customer_name"],
            as_dict=True
        )
        if customer_data:
            info["nif"] = customer_data.tax_id or ""
            info["name"] = customer_data.customer_name or party
    
    # Obtener datos de contacto desde Address
    contact_data = get_party_contact(party, party_type_code)
    if contact_data:
        if not info["provincia"]:
            info["provincia"] = contact_data.get("cp", "")
        info["telefono"] = contact_data.get("phone", "")
        info["email"] = contact_data.get("email", "")
    
    return info


def get_party_contact(party, doctype):
    """Obtiene los datos de contacto del tercero desde Address."""
    result = frappe.db.sql("""
        SELECT 
            LEFT(ad.pincode, 2) as cp, 
            ad.email_id as email, 
            ad.phone
        FROM `tabAddress` ad
        INNER JOIN `tabDynamic Link` dl ON dl.parent = ad.name
        WHERE dl.link_doctype = %(doctype)s
          AND dl.link_name = %(party)s
        LIMIT 1
    """, {
        "doctype": doctype,
        "party": party
    }, as_dict=True)
    
    if result:
        return result[0]
    return None
