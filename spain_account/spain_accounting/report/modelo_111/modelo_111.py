import frappe
from frappe.utils import getdate, nowdate, flt
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None):
    # Initialize filters
    filters = initialize_filters(filters)

    # Get columns
    columns = get_columns()

    # Get data based on filters
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
    """Define columns for Modelo 111."""
    columns = [
        {"label": "Nombre del Proveedor", "fieldname": "supplier_name", "fieldtype": "Data", "width": 200},
        {"label": "Identificador Fiscal", "fieldname": "tax_id", "fieldtype": "Data", "width": 120},
        {"label": "Código Postal", "fieldname": "postal_code", "fieldtype": "Data", "width": 100},
        {"label": "Total Retención", "fieldname": "total_retention", "fieldtype": "Currency", "width": 120},
        {"label": "Total Base", "fieldname": "total_base", "fieldtype": "Currency", "width": 120},
        {"label": "Clave", "fieldname": "key", "fieldtype": "Data", "width": 80},
        {"label": "Subclave", "fieldname": "subkey", "fieldtype": "Data", "width": 80},
    ]
    return columns


def get_data(filters):
    """Fetch and compute data for Modelo 111."""
    company = filters.get("company")
    fiscal_year = filters.get("fiscal_year")
    quarter = filters.get("quarter", "")
    
    # Get date range
    start_date, end_date = get_fiscal_year_date_range(fiscal_year)
    
    # Adjust dates based on quarter
    if quarter:
        start_date, end_date = get_quarter_dates(start_date, end_date, quarter)
    
    # Get ALL accounts from ALL Tax Withholding Categories for the specified company
    # These are all accounts in the "Accounts" child table
    withholding_accounts = frappe.get_all(
        "Tax Withholding Account",
        filters={"company": company},
        fields=["parent", "account"]
    )
    
    if not withholding_accounts:
        return []
    
    account_list = [acc.account for acc in withholding_accounts]
    
    # Create mapping: account -> category
    account_to_category = {acc.account: acc.parent for acc in withholding_accounts}
    
    # Get ALL categories that have accounts for this company
    category_names = list(set([acc.parent for acc in withholding_accounts]))
    
    # Get rates for ALL categories, considering date ranges
    # We need to get the rate that applies for each date
    category_rates_by_date = {}
    for category in category_names:
        rates = frappe.get_all(
            "Tax Withholding Rate",
            filters={"parent": category},
            fields=["tax_withholding_rate", "from_date", "to_date"],
            order_by="from_date asc"
        )
        if rates:
            category_rates_by_date[category] = rates
    
    # Filter categories that have rates of 15% or 7% (Modelo 111 only includes these)
    valid_categories = set()
    for category, rates in category_rates_by_date.items():
        for rate_info in rates:
            rate = flt(rate_info.get("tax_withholding_rate", 0))
            if rate in [15, 7]:
                valid_categories.add(category)
                break
    
    # Filter accounts to only those from valid categories (15% or 7%)
    valid_accounts = [
        acc for acc in withholding_accounts 
        if acc.parent in valid_categories
    ]
    
    if not valid_accounts:
        return []
    
    account_list = [acc.account for acc in valid_accounts]
    
    # Update account_to_category mapping to only include valid categories
    account_to_category = {acc.account: acc.parent for acc in valid_accounts}
    
    # Get GL Entries for withholding accounts
    gl_entries = frappe.db.sql("""
        SELECT 
            gle.account,
            gle.debit,
            gle.credit,
            gle.posting_date,
            gle.voucher_type,
            gle.voucher_no,
            COALESCE(
                CASE WHEN gle.party_type = 'Supplier' THEN gle.party ELSE NULL END,
                pinv.supplier,
                pe.party
            ) as supplier
        FROM `tabGL Entry` gle
        LEFT JOIN `tabPurchase Invoice` pinv 
            ON gle.voucher_type = 'Purchase Invoice' 
            AND gle.voucher_no = pinv.name
        LEFT JOIN `tabPayment Entry` pe
            ON gle.voucher_type = 'Payment Entry'
            AND gle.voucher_no = pe.name
            AND pe.party_type = 'Supplier'
        WHERE gle.account IN %(accounts)s
            AND gle.company = %(company)s
            AND gle.posting_date BETWEEN %(start_date)s AND %(end_date)s
            AND gle.is_cancelled = 0
            AND gle.docstatus < 2
    """, {
        "accounts": account_list,
        "company": company,
        "start_date": start_date,
        "end_date": end_date
    }, as_dict=True)
    
    # Group by supplier and category
    supplier_data = {}
    
    for entry in gl_entries:
        if not entry.supplier:
            continue
            
        # Calculate retention amount
        # For withholding accounts, retentions can be recorded as:
        # - Debits: when retention is applied/practiced
        # - Credits: when retention is recorded (common in liability accounts)
        # We need to consider the net amount: credit - debit (for liability accounts)
        # or debit - credit (for asset accounts)
        # Since these are withholding liability accounts, we use credit - debit
        retention_amount = flt(entry.credit) - flt(entry.debit)
        
        if retention_amount <= 0:
            continue
        
        category = account_to_category.get(entry.account)
        if not category:
            continue
        
        # Get the rate that applies for the posting date of this entry
        rates = category_rates_by_date.get(category, [])
        rate = 0
        
        posting_date = getdate(entry.posting_date)
        for rate_info in rates:
            from_date = getdate(rate_info.get("from_date")) if rate_info.get("from_date") else None
            to_date = getdate(rate_info.get("to_date")) if rate_info.get("to_date") else None
            
            if from_date and to_date:
                if from_date <= posting_date <= to_date:
                    rate = flt(rate_info.get("tax_withholding_rate", 0))
                    break
            elif from_date and posting_date >= from_date:
                rate = flt(rate_info.get("tax_withholding_rate", 0))
                break
        
        # Only process entries with 15% or 7% rates (Modelo 111 requirement)
        if rate not in [15, 7]:
            continue
        
        supplier = entry.supplier
        
        if supplier not in supplier_data:
            supplier_data[supplier] = {
                "supplier": supplier,
                "retention_15": 0,
                "retention_7": 0,
                "base_15": 0,
                "base_7": 0
            }
        
        if rate == 15:
            supplier_data[supplier]["retention_15"] += retention_amount
            supplier_data[supplier]["base_15"] += retention_amount / 0.15
        elif rate == 7:
            supplier_data[supplier]["retention_7"] += retention_amount
            supplier_data[supplier]["base_7"] += retention_amount / 0.07
    
    # Get supplier details
    suppliers_list = list(supplier_data.keys())
    if not suppliers_list:
        return []
    
    # Get supplier details including custom_cp
    supplier_details = frappe.get_all(
        "Supplier",
        filters={"name": ["in", suppliers_list]},
        fields=["name", "supplier_name", "tax_id", "custom_cp"]
    )
    
    supplier_dict = {s.name: s for s in supplier_details}
    
    # Get custom_cp from Supplier (first priority)
    supplier_pincodes = {}
    for supplier in supplier_details:
        custom_cp = supplier.get("custom_cp")
        if custom_cp:
            supplier_pincodes[supplier.name] = custom_cp
    
    # Get postal codes from primary addresses (as fallback)
    addresses = frappe.db.sql("""
        SELECT DISTINCT
            dl.link_name as supplier,
            addr.pincode as postal_code
        FROM `tabDynamic Link` dl
        INNER JOIN `tabAddress` addr ON dl.parent = addr.name
        WHERE dl.link_doctype = 'Supplier'
            AND dl.link_name IN %(suppliers)s
            AND addr.is_primary_address = 1
    """, {
        "suppliers": suppliers_list
    }, as_dict=True)
    
    address_dict = {a.supplier: a.postal_code for a in addresses}
    
    # Build result rows
    result = []
    
    for supplier, data in supplier_data.items():
        supplier_info = supplier_dict.get(supplier, {})
        
        # First try to get pincode from Supplier, if empty or None, get from primary address
        postal_code = supplier_pincodes.get(supplier) or ""
        if not postal_code:
            postal_code = address_dict.get(supplier, "")
        
        # Row for 15% retention
        if data["retention_15"] > 0:
            result.append({
                "supplier_name": supplier_info.get("supplier_name", supplier),
                "tax_id": supplier_info.get("tax_id", ""),
                "postal_code": postal_code,
                "total_retention": round(flt(data["retention_15"]), 2),
                "total_base": round(flt(data["base_15"]), 2),
                "key": "G",
                "subkey": "1"
            })
        
        # Row for 7% retention
        if data["retention_7"] > 0:
            result.append({
                "supplier_name": supplier_info.get("supplier_name", supplier),
                "tax_id": supplier_info.get("tax_id", ""),
                "postal_code": postal_code,
                "total_retention": round(flt(data["retention_7"]), 2),
                "total_base": round(flt(data["base_7"]), 2),
                "key": "G",
                "subkey": "3"
            })
    
    # Sort by supplier name and subkey
    result.sort(key=lambda x: (x["supplier_name"], x["subkey"]))
    
    return result


def get_fiscal_year_date_range(fiscal_year):
    """Get start and end dates for the fiscal year."""
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
