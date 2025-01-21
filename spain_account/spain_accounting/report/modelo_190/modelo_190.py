# import frappe
# from erpnext.accounts.utils import get_balance_on
# from frappe.utils import getdate

# def execute(filters=None):

#     if not filters:
#         filters = {}
    
#     if not filters.get("company"):
#         filters["company"] = frappe.defaults.get_defaults().get("company")

#     if not filters.get('quarter'):
#         filters['quarter'] = get_current_quarter() 
        

#     columns = [
#         {"label": "Declarant NIF", "fieldname": "declarant_nif", "fieldtype": "Data", "width": 100},
#         {"label": "Declarant Name", "fieldname": "declarant_name", "fieldtype": "Data", "width": 100},
#         {"label": "Section", "fieldname": "section", "fieldtype": "Data", "width": 100},
#         {"label": "Recipient NIF", "fieldname": "recipient_nif", "fieldtype": "Data", "width": 100},
#         {"label": "Recipient Name", "fieldname": "recipient_name", "fieldtype": "Data", "width": 100},
#         {"label": "Gross Payment Amount", "fieldname": "gross_payment_amount", "fieldtype": "Currency", "width": 100},
#         {"label": "Payment Type Code", "fieldname": "payment_type_code", "fieldtype": "Data", "width": 100},
#         {"label": "Period", "fieldname": "period", "fieldtype": "Data", "width": 80},
#         {"label": "Suppliers With IRPF Withholding", "fieldname": "total_number_of_suppliers_with_irpf_withholding", "fieldtype": "Data", "width": 150, "align": "center"},
#         {"label": "Employees with IRPF Withholding", "fieldname": "total_number_of_employees_with_irpf_withholding", "fieldtype": "Data", "width": 150, "align": "center"},
#         {"label": "Total Withheld from Suppliers", "fieldname": "total_irpf_amount_withheld_from_suppliers", "fieldtype": "Currency", "width": 150, "align": "center"},
#         {"label": "Total Withheld from Employees", "fieldname": "total_irpf_amount_withheld_from_employees", "fieldtype": "Currency", "width": 150, "align": "center"},
#     ]
    

#     data = get_data(filters)

#     return columns, data


# def get_data(filters):
#     company = filters.get("company")
#     quarter = filters['quarter']
#     start_date, end_date = get_quarter_date_range(quarter)

#     model_values = frappe.get_all(
#         "Model Values",
#         fields=["value_description as description", "value_type", "calculation_rule__query"],
#         filters={"parent": "Modelo 190"},
#     )
#     results = {
#         "period": quarter,
#         "total_number_of_suppliers_with_irpf_withholding": 0,
#         "total_number_of_employees_with_irpf_withholding": 0,
#         "total_irpf_amount_withheld_from_suppliers": 0,
#         "total_irpf_amount_withheld_from_employees": 0,
#     }

#     for value in model_values:
#         accounts = execute_sql(value["calculation_rule__query"],company)
        
#         total_amount = 0
#         total_account = 0
#         if accounts:
#             for d in accounts:
#                     balance = get_balance_on(d[0], date=end_date, start_date=start_date)
#                     total_amount += balance
#                     if abs(balance) > 0:
#                         total_account += 1
#         if value["description"] == "Total number of suppliers with IRPF withholding":
#             results["total_number_of_suppliers_with_irpf_withholding"] = total_account if total_account else 0
        
#         if value["description"] == "Total number of employees with IRPF withholding":
#             results["total_number_of_employees_with_irpf_withholding"] = total_account if total_account else 0
        
#         if value["description"] == "Total IRPF amount withheld from suppliers":
#             results["total_irpf_amount_withheld_from_suppliers"] = abs(total_amount)

#         if value["description"] == "Total IRPF amount withheld from employees":
#             results["total_irpf_amount_withheld_from_employees"] = abs(total_amount)

#     return [results] 


# def execute_sql(sql_query, company=None):

#     result = frappe.db.sql(sql_query,{"company": company})
#     return result if result else 0


# def get_current_quarter():

#     month = getdate(frappe.utils.now()).month
#     if month in [1, 2, 3]:
#         return "1Q"
#     elif month in [4, 5, 6]:
#         return "2Q"
#     elif month in [7, 8, 9]:
#         return "3Q"
#     else:
#         return "4Q"


# def get_quarter_date_range(quarter):

#     year = getdate(frappe.utils.now()).year
#     if quarter == "1Q":
#         return f"{year}-01-01", f"{year}-03-31"
#     elif quarter == "2Q":
#         return f"{year}-04-01", f"{year}-06-30"
#     elif quarter == "3Q":
#         return f"{year}-07-01", f"{year}-09-30"
#     elif quarter == "4Q":
#         return f"{year}-10-01", f"{year}-12-31"
#     else:
#         return f"{year}-01-01", f"{year}-12-31"
import frappe
from erpnext.accounts.utils import get_balance_on
from frappe.utils import getdate, nowdate
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None):
    filters = initialize_filters(filters)

    columns = get_columns()
    data = get_data(filters, columns)

    return columns, data


def initialize_filters(filters):
    if not filters:
        filters = {}

    defaults = frappe.defaults.get_defaults()
    filters.setdefault("company", defaults.get("company"))
    filters.setdefault("fiscal_year", get_fiscal_year(nowdate(), as_dict=True).get("name"))

    return filters


def get_columns():
    base_columns = [
    {"label": "NIF del Declarante", "fieldname": "declarant_nif", "fieldtype": "Data", "width": 100},
    {"label": "Nombre del Declarante", "fieldname": "declarant_name", "fieldtype": "Data", "width": 100},
    {"label": "Sección", "fieldname": "section", "fieldtype": "Data", "width": 100},
    {"label": "NIF del Receptor", "fieldname": "recipient_nif", "fieldtype": "Data", "width": 100},
    {"label": "Nombre del Receptor", "fieldname": "recipient_name", "fieldtype": "Data", "width": 100},
    {"label": "Monto Bruto de Pago", "fieldname": "gross_payment_amount", "fieldtype": "Currency", "width": 100},
    {"label": "Código de Tipo de Pago", "fieldname": "payment_type_code", "fieldtype": "Data", "width": 100},
    {"label": "Año Fiscal", "fieldname": "fiscal_year", "fieldtype": "Data", "width": 100},
    ]


    # Fetch dynamic columns
    dynamic_columns = [
        {
            "label": value["value_description"],
            "fieldname": frappe.scrub(value["value_description"]),
            "fieldtype": "Currency" if value["value_type"] == "Monetary Amount" else "Int",
            "width": 150,
            "align": "center" if value["value_type"] == "Monetary Amount" else "left",
        }
        for value in frappe.get_all(
            "Model Values",
            fields=["value_description", "value_type"],
            filters={"parent": "Modelo 190"},
            order_by="idx asc",
        )
    ]

    return base_columns + dynamic_columns


def get_data(filters, columns):
    company, fiscal_year = filters["company"], filters["fiscal_year"]
    start_date, end_date = get_fiscal_year_date_range(fiscal_year)

    # Base results
    results = {"fiscal_year": fiscal_year}

    # Fetch dynamic fields
    dynamic_fields = {
        frappe.scrub(value["value_description"]): value["calculation_rule__query"]
        for value in frappe.get_all(
            "Model Values",
            fields=["value_description", "calculation_rule__query"],
            filters={"parent": "Modelo 190"},
        )
    }

    for fieldname, query in dynamic_fields.items():
        accounts = execute_sql(query, company)
        total_amount = sum(get_balance_on(account[0], date=end_date, start_date=start_date) for account in accounts)
        total_accounts = sum(1 for account in accounts if abs(get_balance_on(account[0], date=end_date, start_date=start_date)) > 0)

        # Assign values
        results[fieldname] = abs(total_amount) if "amount" in fieldname else total_accounts

    return [results]


def execute_sql(sql_query, company=None):
    return frappe.db.sql(sql_query, {"company": company}) or []


def get_fiscal_year_date_range(fiscal_year):
    fiscal_year_doc = frappe.get_doc("Fiscal Year", fiscal_year)
    return getdate(fiscal_year_doc.year_start_date), getdate(fiscal_year_doc.year_end_date)

