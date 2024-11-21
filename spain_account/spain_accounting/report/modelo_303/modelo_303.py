import frappe
from erpnext.accounts.utils import get_balance_on
from frappe.utils import getdate

def execute(filters=None):

    if not filters:
        filters = {}

    if not filters.get('quarter'):
        filters['quarter'] = get_current_quarter() 
        

    columns = [
        {"label": "Declarant NIF", "fieldname": "declarant_nif", "fieldtype": "Data", "width": 120},
        {"label": "Declarant Name", "fieldname": "declarant_name", "fieldtype": "Data", "width": 140},
		{"label": "Fiscal Year", "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 100},
        {"label": "Period", "fieldname": "period", "fieldtype": "Data", "width": 80},
        {"label": "Total VAT Sales Amount Subject", "fieldname": "total_vat_sales_amount_subject", "fieldtype": "Currency", "width": 190, "align": "center"},
        {"label": "Total VAT Collected", "fieldname": "total_vat_collected", "fieldtype": "Currency", "width": 190, "align": "center"},
        {"label": "Total VAT Paid", "fieldname": "total_vat_paid", "fieldtype": "Currency", "width": 190, "align": "center"},
        {"label": "VAT Payable/Refundable", "fieldname": "vat_payable_refundable", "fieldtype": "Currency", "width": 190, "align": "center"},
    ]
    

    data = get_data(filters)

    return columns, data


def get_data(filters):
    quarter = filters['quarter']
    start_date, end_date = get_quarter_date_range(quarter)

    model_values = frappe.get_all(
        "Model Values",
        fields=["value_description as description", "value_type", "calculation_rule__query",],
        filters={"parent": "Modelo 303"},
    )
    results = {
        "period": quarter,
        "fiscal_year" : frappe.get_value("Hacienda Model", "Modelo 303", "fiscal_year"),
        "total_vat_sales_amount_subject": 0,
        "total_vat_collected": 0,
        "total_vat_paid": 0,
        "vat_payable_refundable": 0,
    }

    for value in model_values:
		
        value_count = execute_sql(value["calculation_rule__query"])
        print("Calculation", value_count)
        if value["description"] == "Total Sales Amount Subject to VAT":
            results["total_vat_sales_amount_subject"] = value_count[0][0] 
        
        if value["description"] == "Total VAT Collected on Sales":
            results["total_vat_collected"] =  value_count[0][0]  
        
        if value["description"] == "Total VAT Paid on Purchases":
            results["total_vat_paid"] =   value_count[0][0]  

        if value["description"] == "Net VAT Payable (VAT Collected - VAT Paid)":
            results["vat_payable_refundable"] =   value_count[0][0]  

    return [results] 


def execute_sql(sql_query):

    result = frappe.db.sql(sql_query)
    return result if result else 0


def get_current_quarter():

    month = getdate(frappe.utils.now()).month
    if month in [1, 2, 3]:
        return "1Q"
    elif month in [4, 5, 6]:
        return "2Q"
    elif month in [7, 8, 9]:
        return "3Q"
    else:
        return "4Q"


def get_quarter_date_range(quarter):

    year = getdate(frappe.utils.now()).year
    if quarter == "1Q":
        return f"{year}-01-01", f"{year}-03-31"
    elif quarter == "2Q":
        return f"{year}-04-01", f"{year}-06-30"
    elif quarter == "3Q":
        return f"{year}-07-01", f"{year}-09-30"
    elif quarter == "4Q":
        return f"{year}-10-01", f"{year}-12-31"
    else:
        return f"{year}-01-01", f"{year}-12-31"
