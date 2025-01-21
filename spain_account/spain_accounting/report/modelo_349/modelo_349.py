import frappe
from frappe.utils import getdate, now , nowdate
from datetime import timedelta
from erpnext.accounts.utils import get_fiscal_year


def execute(filters=None):
    filters = prepare_filters(filters)
    columns, column_keys = get_columns()
    data = get_data(filters, column_keys)
    return columns, data

def prepare_filters(filters):
    filters = filters or {}
    filters.setdefault("company", frappe.defaults.get_defaults().get("company"))
    filters.setdefault("fiscal_year" , get_fiscal_year(nowdate(), as_dict=True).get("name"))
    if not any(filters.get(key) for key in ["quarter", "from_date", "to_date"]):
        filters["quarter"] = get_current_quarter()

    return filters

def get_columns():
    # Static columns
    columns = [
        {"label": "NIF del Declarante", "fieldname": "declarant_nif", "fieldtype": "Data", "width": 120},
        {"label": "Nombre del Declarante", "fieldname": "declarant_name", "fieldtype": "Data", "width": 140},
        {"label": "Año Fiscal", "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 103},
        {"label": "Período", "fieldname": "period", "fieldtype": "Data", "width": 90},
    ]


    # Fetch dynamic columns from Model Values
    dynamic_values = frappe.get_all(
        "Model Values",
        fields=["value_description", "idx"],
        filters={"parent": "Modelo 349"},
        order_by="idx asc"
    )

    column_keys = []  
    for row in dynamic_values:
        fieldname = frappe.scrub(row["value_description"])
        columns.append({
            "label": row["value_description"],
            "fieldname": fieldname,
            "fieldtype": "Currency",
            "width": 250,
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
        "period": filters.get("quarter"),
    }

    # Fetch and map data dynamically
    for original_name, fieldname in column_keys:
        query = frappe.db.get_value("Model Values", {"value_description": original_name}, "calculation_rule__query")
        row_data[fieldname] = execute_sql(query, start_date, end_date, company) if query else 0

    return [row_data]

def determine_date_range(filters):
    fiscal_year = filters.get("fiscal_year")
    quarter = filters.get("quarter")

    if fiscal_year:
        fiscal_start_date, fiscal_end_date = frappe.db.get_value(
            "Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"]
        )

        if quarter:
            return get_quarter_date_range(quarter, fiscal_start_date)

        return fiscal_start_date, fiscal_end_date

    if quarter:
        # Use the calendar year if no fiscal year is specified
        return get_quarter_date_range(quarter)

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

def get_current_quarter():
    month = getdate(now()).month
    return f"{(month - 1) // 3 + 1}Q"

def get_quarter_date_range(quarter, fiscal_start_date=None):
    if fiscal_start_date:
        fiscal_year_start = getdate(fiscal_start_date)
        fiscal_year = fiscal_year_start.year
        fiscal_month_start = fiscal_year_start.month

        # Adjust the quarter calculation based on the fiscal year's starting month
        quarters = {
            "1Q": (
                fiscal_year_start,
                fiscal_year_start.replace(
                    month=(fiscal_month_start + 2) % 12 + 1, day=1
                )
                - timedelta(days=1),
            ),
            "2Q": (
                fiscal_year_start.replace(
                    month=(fiscal_month_start + 3) % 12 + 1, day=1
                ),
                fiscal_year_start.replace(
                    month=(fiscal_month_start + 5) % 12 + 1, day=1
                )
                - timedelta(days=1),
            ),
            "3Q": (
                fiscal_year_start.replace(
                    month=(fiscal_month_start + 6) % 12 + 1, day=1
                ),
                fiscal_year_start.replace(
                    month=(fiscal_month_start + 8) % 12 + 1, day=1
                )
                - timedelta(days=1),
            ),
            "4Q": (
                fiscal_year_start.replace(
                    month=(fiscal_month_start + 9) % 12 + 1, day=1
                ),
                fiscal_year_start.replace(
                    year=fiscal_year + 1,
                    month=(fiscal_month_start + 11) % 12 + 1,
                    day=1,
                )
                - timedelta(days=1),
            ),
        }
        return quarters.get(quarter)

    # Default to calendar year if no fiscal start date is provided
    year = getdate(now()).year
    quarters = {
        "1Q": (f"{year}-01-01", f"{year}-03-31"),
        "2Q": (f"{year}-04-01", f"{year}-06-30"),
        "3Q": (f"{year}-07-01", f"{year}-09-30"),
        "4Q": (f"{year}-10-01", f"{year}-12-31"),
    }
    return quarters.get(quarter)



