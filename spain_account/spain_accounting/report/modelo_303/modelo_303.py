# Copyright (c) 2024, Xappiens and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt
from erpnext.accounts.utils import get_fiscal_year
import re


def execute(filters=None):
    """Main entry point for Modelo 303 report."""
    filters = initialize_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def initialize_filters(filters):
    """Set default filters if not provided."""
    if not filters:
        filters = {}

    defaults = frappe.defaults.get_defaults()
    filters.setdefault("company", defaults.get("company"))
    filters.setdefault("fiscal_year", get_fiscal_year(nowdate(), as_dict=True).get("name"))

    return filters


def get_columns():
    """
    Define columns for Modelo 303 - IVA declaration.
    
    Casillas oficiales AEAT:
    IVA Devengado:
        - 21%: Casillas 07 (Base), 08 (Tipo), 09 (Cuota)
        - 10%: Casillas 04 (Base), 05 (Tipo), 06 (Cuota)
        - 4%:  Casillas 01 (Base), 02 (Tipo), 03 (Cuota)
        - Total cuotas devengadas: Casilla 27
    
    IVA Deducible:
        - Operaciones interiores corrientes: Casillas 28 (Base), 29 (Cuota)
        - Total a deducir: Casilla 45
    
    Resultado:
        - Diferencia: Casilla 46
    """
    columns = [
        # Identificación
        {"label": _("Período"), "fieldname": "period", "fieldtype": "Data", "width": 80},
        
        # IVA Devengado (Repercutido) - Ventas
        {"label": _("[07] Base 21%"), "fieldname": "base_21_dev", "fieldtype": "Currency", "width": 130},
        {"label": _("[09] Cuota 21%"), "fieldname": "cuota_21_dev", "fieldtype": "Currency", "width": 130},
        {"label": _("[04] Base 10%"), "fieldname": "base_10_dev", "fieldtype": "Currency", "width": 130},
        {"label": _("[06] Cuota 10%"), "fieldname": "cuota_10_dev", "fieldtype": "Currency", "width": 130},
        {"label": _("[01] Base 4%"), "fieldname": "base_4_dev", "fieldtype": "Currency", "width": 130},
        {"label": _("[03] Cuota 4%"), "fieldname": "cuota_4_dev", "fieldtype": "Currency", "width": 130},
        {"label": _("[27] Total Devengado"), "fieldname": "total_devengado", "fieldtype": "Currency", "width": 160},
        
        # IVA Deducible (Soportado) - Compras
        {"label": _("[28] Base 21% Ded"), "fieldname": "base_21_ded", "fieldtype": "Currency", "width": 140},
        {"label": _("[29] Cuota 21% Ded"), "fieldname": "cuota_21_ded", "fieldtype": "Currency", "width": 140},
        {"label": _("[28] Base 10% Ded"), "fieldname": "base_10_ded", "fieldtype": "Currency", "width": 140},
        {"label": _("[29] Cuota 10% Ded"), "fieldname": "cuota_10_ded", "fieldtype": "Currency", "width": 140},
        {"label": _("[28] Base 4% Ded"), "fieldname": "base_4_ded", "fieldtype": "Currency", "width": 140},
        {"label": _("[29] Cuota 4% Ded"), "fieldname": "cuota_4_ded", "fieldtype": "Currency", "width": 140},
        {"label": _("[45] Total Deducible"), "fieldname": "total_deducible", "fieldtype": "Currency", "width": 160},
        
        # Resultado
        {"label": _("[46] Diferencia"), "fieldname": "diferencia", "fieldtype": "Currency", "width": 150},
    ]
    return columns


def get_rate_from_account(account_name):
    """
    Extracts VAT percentage from account name.
    Examples:
        "IVA SOPORTADO 21%" -> 21
        "IVA REPERCUTIDO AL 10%" -> 10
        "472021000 - IVA SOPORTADO AL 21% - IBI" -> 21
    """
    if not account_name:
        return 0
    
    # Pattern to match numbers followed by % (with optional spaces)
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*%', account_name)
    if match:
        rate_str = match.group(1).replace(',', '.')
        return flt(rate_str)
    
    # Try to extract from account number patterns like 472021000 (21% embedded)
    # Common patterns: 47200XXXX for 0%, 47204XXXX for 4%, 47210XXXX for 10%, 47221XXXX for 21%
    account_number_match = re.search(r'472(\d{2})', account_name)
    if account_number_match:
        rate_code = account_number_match.group(1)
        if rate_code in ['21', '02']:
            return 21
        elif rate_code in ['10', '01']:
            return 10
        elif rate_code in ['04', '00']:
            if '4%' in account_name or 'AL 4' in account_name:
                return 4
            return 0
    
    account_number_match = re.search(r'477(\d{2})', account_name)
    if account_number_match:
        rate_code = account_number_match.group(1)
        if rate_code in ['21', '02']:
            return 21
        elif rate_code in ['10', '01']:
            return 10
        elif rate_code in ['04', '00']:
            if '4%' in account_name or 'AL 4' in account_name:
                return 4
            return 0
    
    return 0


def get_data(filters):
    """Fetch and compute data for Modelo 303 - IVA declaration."""
    company = filters.get("company")
    fiscal_year = filters.get("fiscal_year")
    quarter = filters.get("quarter", "")

    if not company or not fiscal_year:
        return []

    # Get date range
    date_range = get_fiscal_year_date_range(fiscal_year)
    if not date_range:
        return []
    
    start_date, end_date = date_range

    # Adjust dates based on quarter
    if quarter:
        start_date, end_date = get_quarter_dates(start_date, end_date, quarter)

    # Get IVA Devengado (Repercutido) from group 477
    iva_devengado = get_iva_by_group(company, start_date, end_date, "477", is_repercutido=True)
    
    # Get IVA Deducible (Soportado) from group 472
    iva_deducible = get_iva_by_group(company, start_date, end_date, "472", is_repercutido=False)

    # Build row data
    row = {
        "period": quarter or fiscal_year,
        
        # IVA Devengado
        "base_21_dev": round(iva_devengado.get(21, {}).get("base", 0), 2),
        "cuota_21_dev": round(iva_devengado.get(21, {}).get("cuota", 0), 2),
        "base_10_dev": round(iva_devengado.get(10, {}).get("base", 0), 2),
        "cuota_10_dev": round(iva_devengado.get(10, {}).get("cuota", 0), 2),
        "base_4_dev": round(iva_devengado.get(4, {}).get("base", 0), 2),
        "cuota_4_dev": round(iva_devengado.get(4, {}).get("cuota", 0), 2),
        
        # IVA Deducible
        "base_21_ded": round(iva_deducible.get(21, {}).get("base", 0), 2),
        "cuota_21_ded": round(iva_deducible.get(21, {}).get("cuota", 0), 2),
        "base_10_ded": round(iva_deducible.get(10, {}).get("base", 0), 2),
        "cuota_10_ded": round(iva_deducible.get(10, {}).get("cuota", 0), 2),
        "base_4_ded": round(iva_deducible.get(4, {}).get("base", 0), 2),
        "cuota_4_ded": round(iva_deducible.get(4, {}).get("cuota", 0), 2),
    }
    
    # Calculate totals
    row["total_devengado"] = round(
        row["cuota_21_dev"] + row["cuota_10_dev"] + row["cuota_4_dev"], 2
    )
    row["total_deducible"] = round(
        row["cuota_21_ded"] + row["cuota_10_ded"] + row["cuota_4_ded"], 2
    )
    row["diferencia"] = round(row["total_devengado"] - row["total_deducible"], 2)

    return [row]


def get_iva_by_group(company, start_date, end_date, account_group, is_repercutido=True):
    """
    Get IVA amounts grouped by rate from GL Entry.
    
    Args:
        company: Company name
        start_date: Period start date
        end_date: Period end date
        account_group: "472" for soportado, "477" for repercutido
        is_repercutido: True for 477 (credit - debit), False for 472 (debit - credit)
    
    Returns:
        Dictionary with rate as key and {base, cuota} as value
    """
    # Get all accounts in the group
    accounts = frappe.db.get_list(
        "Account",
        filters={
            "account_number": ["like", f"{account_group}%"],
            "company": company,
            "is_group": 0
        },
        fields=["name", "account_number"],
        pluck="name"
    )
    
    if not accounts:
        return {}
    
    # Get GL Entries for these accounts
    gl_entries = frappe.db.sql("""
        SELECT
            gle.account,
            gle.debit,
            gle.credit
        FROM `tabGL Entry` gle
        WHERE gle.account IN %(accounts)s
            AND gle.company = %(company)s
            AND gle.posting_date BETWEEN %(start_date)s AND %(end_date)s
            AND gle.is_cancelled = 0
            AND gle.docstatus < 2
    """, {
        "accounts": accounts,
        "company": company,
        "start_date": start_date,
        "end_date": end_date
    }, as_dict=True)
    
    # Group by rate
    rates_data = {}
    
    for entry in gl_entries:
        rate = get_rate_from_account(entry.account)
        
        if rate not in rates_data:
            rates_data[rate] = {"cuota": 0, "base": 0}
        
        # Calculate cuota (VAT amount)
        if is_repercutido:
            # IVA Repercutido (477): credit - debit
            cuota = flt(entry.credit) - flt(entry.debit)
        else:
            # IVA Soportado (472): debit - credit
            cuota = flt(entry.debit) - flt(entry.credit)
        
        rates_data[rate]["cuota"] += cuota
    
    # Calculate base for each rate
    for rate, data in rates_data.items():
        if rate > 0:
            data["base"] = data["cuota"] / (rate / 100)
        else:
            data["base"] = 0
    
    return rates_data


def get_fiscal_year_date_range(fiscal_year):
    """Get start and end dates for the fiscal year."""
    if not fiscal_year:
        return None
    
    if not frappe.db.exists("Fiscal Year", fiscal_year):
        return None
    
    fiscal_year_doc = frappe.get_doc("Fiscal Year", fiscal_year)
    return getdate(fiscal_year_doc.year_start_date), getdate(fiscal_year_doc.year_end_date)


def get_quarter_dates(start_date, end_date, quarter):
    """Get start and end dates for a specific quarter."""
    year = start_date.year

    if quarter == "1T":
        return getdate(f"{year}-01-01"), getdate(f"{year}-03-31")
    elif quarter == "2T":
        return getdate(f"{year}-04-01"), getdate(f"{year}-06-30")
    elif quarter == "3T":
        return getdate(f"{year}-07-01"), getdate(f"{year}-09-30")
    elif quarter == "4T":
        return getdate(f"{year}-10-01"), getdate(f"{year}-12-31")

    return start_date, end_date
