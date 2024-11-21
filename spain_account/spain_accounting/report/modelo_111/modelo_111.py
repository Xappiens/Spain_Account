import frappe
from erpnext.accounts.utils import get_balance_on
from frappe.utils import getdate

def execute(filters=None):

    if not filters:
        filters = {}

    if not filters.get('quarter'):
        filters['quarter'] = get_current_quarter() 
        

    columns = [
        {"label": "Declarant NIF", "fieldname": "declarant_nif", "fieldtype": "Data", "width": 100},
        {"label": "Declarant Name", "fieldname": "declarant_name", "fieldtype": "Data", "width": 100},
        {"label": "Section", "fieldname": "section", "fieldtype": "Data", "width": 100},
        {"label": "Recipient NIF", "fieldname": "recipient_nif", "fieldtype": "Data", "width": 100},
        {"label": "Recipient Name", "fieldname": "recipient_name", "fieldtype": "Data", "width": 100},
        {"label": "Gross Payment Amount", "fieldname": "gross_payment_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Payment Type Code", "fieldname": "payment_type_code", "fieldtype": "Data", "width": 100},
        {"label": "Period", "fieldname": "period", "fieldtype": "Data", "width": 80},
        {"label": "Suppliers With IRPF Withholding", "fieldname": "total_number_of_suppliers_with_irpf_withholding", "fieldtype": "Data", "width": 150, "align": "center"},
        {"label": "Employees with IRPF Withholding", "fieldname": "total_number_of_employees_with_irpf_withholding", "fieldtype": "Data", "width": 150, "align": "center"},
        {"label": "Total Withheld from Suppliers", "fieldname": "total_irpf_amount_withheld_from_suppliers", "fieldtype": "Currency", "width": 150, "align": "center"},
        {"label": "Total Withheld from Employees", "fieldname": "total_irpf_amount_withheld_from_employees", "fieldtype": "Currency", "width": 150, "align": "center"},
    ]
    

    data = get_data(filters)

    return columns, data


def get_data(filters):
    quarter = filters['quarter']
    start_date, end_date = get_quarter_date_range(quarter)

    model_values = frappe.get_all(
        "Model Values",
        fields=["value_description as description", "value_type", "calculation_rule__query"],
        filters={"parent": "Modelo 111"},
    )
    results = {
        "period": quarter,
        "total_number_of_suppliers_with_irpf_withholding": 0,
        "total_number_of_employees_with_irpf_withholding": 0,
        "total_irpf_amount_withheld_from_suppliers": 0,
        "total_irpf_amount_withheld_from_employees": 0,
    }

    for value in model_values:
        accounts = execute_sql(value["calculation_rule__query"])
        
        total_amount = 0
        total_account = 0
        if accounts:
            for d in accounts:
                    balance = get_balance_on(d[0], date=end_date, start_date=start_date)
                    total_amount += balance
                    if abs(balance) > 0:
                        total_account += 1
        if value["description"] == "Total number of suppliers with IRPF withholding":
            results["total_number_of_suppliers_with_irpf_withholding"] = total_account if total_account else 0
        
        if value["description"] == "Total number of employees with IRPF withholding":
            results["total_number_of_employees_with_irpf_withholding"] = total_account if total_account else 0
        
        if value["description"] == "Total IRPF amount withheld from suppliers":
            results["total_irpf_amount_withheld_from_suppliers"] = abs(total_amount)

        if value["description"] == "Total IRPF amount withheld from employees":
            results["total_irpf_amount_withheld_from_employees"] = abs(total_amount)

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
