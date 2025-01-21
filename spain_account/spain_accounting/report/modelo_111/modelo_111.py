import frappe
from erpnext.accounts.utils import get_balance_on
from frappe.utils import getdate, nowdate
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None):
    # Initialize filters
    filters = initialize_filters(filters)

    # Get columns dynamically
    columns = get_columns()

    # Get data based on filters and columns
    data = get_data(filters, columns)

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
    """Define static and dynamic columns."""
    # Static columns
    base_columns =[
    {"label": "NIF del Declarante", "fieldname": "declarant_nif", "fieldtype": "Data", "width": 100},
    {"label": "Nombre del Declarante", "fieldname": "declarant_name", "fieldtype": "Data", "width": 100},
    {"label": "Sección", "fieldname": "section", "fieldtype": "Data", "width": 100},
    {"label": "NIF del Destinatario", "fieldname": "recipient_nif", "fieldtype": "Data", "width": 100},
    {"label": "Nombre del Destinatario", "fieldname": "recipient_name", "fieldtype": "Data", "width": 100},
    {"label": "Monto Bruto de Pago", "fieldname": "gross_payment_amount", "fieldtype": "Currency", "width": 100},
    {"label": "Código del Tipo de Pago", "fieldname": "payment_type_code", "fieldtype": "Data", "width": 100},
    {"label": "Año Fiscal", "fieldname": "fiscal_year", "fieldtype": "Data", "width": 100}
]


    # Dynamic columns fetched from Model Values
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
            filters={"parent": "Modelo 111"},
            order_by="idx asc",
        )
    ]

    return base_columns + dynamic_columns


def get_data(filters, columns):
    """Fetch and compute data dynamically."""
    company, fiscal_year = filters["company"], filters["fiscal_year"]
    start_date, end_date = get_fiscal_year_date_range(fiscal_year)

    # Initialize results
    results = {"fiscal_year": fiscal_year}

    # Dynamic fields with their SQL queries
    dynamic_fields = {
        frappe.scrub(value["value_description"]): value["calculation_rule__query"]
        for value in frappe.get_all(
            "Model Values",
            fields=["value_description", "calculation_rule__query"],
            filters={"parent": "Modelo 111"},
        )
    }

    # Process dynamic fields
    for fieldname, query in dynamic_fields.items():
        accounts = execute_sql(query, company)

        # Calculate total amount and account count
        total_amount = sum(get_balance_on(account[0], date=end_date, start_date=start_date) for account in accounts)
        total_accounts = sum(1 for account in accounts if abs(get_balance_on(account[0], date=end_date, start_date=start_date)) > 0)

        # Assign results
        if "amount" in fieldname:
            results[fieldname] = abs(total_amount)
        else:
            results[fieldname] = total_accounts

    return [results]


def execute_sql(sql_query, company=None):
    """Execute SQL query with the company parameter."""
    return frappe.db.sql(sql_query, {"company": company}) or []


def get_fiscal_year_date_range(fiscal_year):
    """Get start and end dates for the fiscal year."""
    fiscal_year_doc = frappe.get_doc("Fiscal Year", fiscal_year)
    return getdate(fiscal_year_doc.year_start_date), getdate(fiscal_year_doc.year_end_date)
