import frappe
from frappe.utils import  nowdate
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None):
    filters = prepare_filters(filters)
    columns, column_keys = get_columns()
    data = get_data(filters, column_keys)
    return columns, data

def prepare_filters(filters):
    filters = filters or {}
    filters.setdefault("company", frappe.defaults.get_defaults().get("company"))
    filters.setdefault("fiscal_year",get_fiscal_year(nowdate(), as_dict=True).get("name"))

    return filters

def get_columns():
    # Static columns
    columns = [
        {"label": "NIF del Declarante", "fieldname": "declarant_nif", "fieldtype": "Data", "width": 120},
        {"label": "Nombre del Declarante", "fieldname": "declarant_name", "fieldtype": "Data", "width": 140},
        {"label": "Año Fiscal", "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 150, "align": "center"},
    ]


    # Fetch dynamic columns from Model Values
    dynamic_values = frappe.get_all(
        "Model Values",
        fields=["value_description","value_type", "idx"],
        filters={"parent": "Modelo 347"},
        order_by="idx asc"
    )

    column_keys = []  
    for row in dynamic_values:
        fieldname = frappe.scrub(row["value_description"])
        fieldtype = "Int" if row["value_type"] == "Integer (count)" else "Currency" 
        columns.append({
            "label": row["value_description"],
            "fieldname": fieldname,
            "fieldtype": fieldtype,
            "width": 200,
            "align": "center"
        })
        column_keys.append((row["value_description"], fieldname))

    return columns, column_keys

def get_data(filters, column_keys):
    start_date, end_date = determine_date_range(filters)
    company = filters.get("company")

    # Base row data
    row_data = {
        "fiscal_year": filters.get("fiscal_year"),
    }

    # Fetch and map data dynamically
    for original_name, fieldname in column_keys:
        query = frappe.db.get_value("Model Values", {"value_description": original_name}, "calculation_rule__query")
        row_data[fieldname] = execute_sql(query, start_date, end_date, company) if query else 0

    return [row_data]

def determine_date_range(filters):
    fiscal_year = filters.get("fiscal_year")

    if fiscal_year:
        return frappe.db.get_value(
            "Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"]
        )

    return None, None

def execute_sql(query, start_date, end_date, company):
    result = frappe.db.sql(
        query,
        {"start_date": start_date, "end_date": end_date, "company": company},
        as_dict=True,
    )
    if result:
        return result[0].get("total", 0) if result[0].get("total") else 0
    else:
        return 0
