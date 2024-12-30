# import frappe
# from erpnext.accounts.utils import get_fiscal_year, get_balance_on
# from frappe.utils import getdate, now, nowdate
# from datetime import timedelta

# def execute(filters=None):
#     filters = prepare_filters(filters)
#     columns, column_keys = get_columns()
#     data = get_data(filters, column_keys)
#     return columns, data

# def prepare_filters(filters):
#     filters = filters or {}
#     filters.setdefault("company", frappe.defaults.get_defaults().get("company"))
#     filters.setdefault("fiscal_year", get_fiscal_year(nowdate(), as_dict=True).get("name"))
#     filters.setdefault("quarter", filters.get("quarter") or get_current_quarter())
#     return filters

# def get_columns():
#     columns = [
#         {"label": "Name", "fieldname": "name", "fieldtype": "Data", "width": 350},
#         {"label": "Count", "fieldname": "count", "fieldtype": "Currency", "width": 150},
#     ]
    
#     dynamic_values = frappe.get_all(
#         "Model Values",
#         fields=["value_description", "calculation_rule__query"],
#         filters={"parent": "Modelo 390"},
#         order_by="idx asc"
#     )
    
#     column_keys = [(row["value_description"], row["calculation_rule__query"]) for row in dynamic_values]
#     return columns, column_keys

# def get_data(filters, column_keys):
#     start_date, end_date = determine_date_range(filters)
#     company = filters.get("company")
    
#     sales_accounts = get_tax_accounts("477", company)
#     purchase_accounts = get_tax_accounts("472", company)

#     row_data = []

#     # Process dynamic values
#     for value_description, calculation_query in column_keys:
#         row_data.append({
#             "name": value_description,
#             "count": execute_sql(calculation_query, start_date, end_date, company)
#         })

#     # Process sales and purchase tax accounts
#     row_data += process_tax_accounts(sales_accounts, start_date, end_date, get_sales_tax_template_for_account)
#     row_data += process_tax_accounts(purchase_accounts, start_date, end_date, get_purchase_tax_template_for_account)

#     return row_data

# def determine_date_range(filters):
#     fiscal_year = filters.get("fiscal_year")
#     quarter = filters.get("quarter")

#     if fiscal_year:
#         fiscal_start, fiscal_end = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"])
#         if quarter:
#             return get_quarter_date_range(quarter, fiscal_start)
#         return fiscal_start, fiscal_end

#     return get_quarter_date_range(quarter) if quarter else (None, None)

# def execute_sql(query, start_date, end_date, company):
#     result = frappe.db.sql(
#         query, {"start_date": start_date, "end_date": end_date, "company": company}, as_dict=True
#     )
#     return result[0].get("total", 0) if result else 0

# def get_current_quarter():
#     month = getdate(now()).month
#     return f"{(month - 1) // 3 + 1}Q"

# def get_quarter_date_range(quarter, fiscal_start_date=None):
#     fiscal_year_start = getdate(fiscal_start_date) if fiscal_start_date else getdate(f"{getdate(now()).year}-01-01")
#     quarters = [
#         (fiscal_year_start, fiscal_year_start + timedelta(days=89)),
#         (fiscal_year_start + timedelta(days=90), fiscal_year_start + timedelta(days=180)),
#         (fiscal_year_start + timedelta(days=181), fiscal_year_start + timedelta(days=272)),
#         (fiscal_year_start + timedelta(days=273), fiscal_year_start.replace(year=fiscal_year_start.year + 1) - timedelta(days=1)),
#     ]
#     return quarters[int(quarter[0]) - 1]

# def get_tax_accounts(account_number, company):
#     parent_account = frappe.db.get_value("Account", {"account_number": account_number, "company": company}, "name")
#     return frappe.get_all("Account", filters={"parent_account": parent_account}, fields=["name"])

# def process_tax_accounts(accounts, start_date, end_date, template_fetcher):
#     rows = []
#     for account in accounts:
#         template = template_fetcher(account.get("name"))
#         if template:
#             rows.append({
#                 "name": template[0]["name"],
#                 "count": abs(get_balance_on(account.get("name"), date=end_date, start_date=start_date))
#             })
#     return rows

# def get_sales_tax_template_for_account(account_name):
#     return frappe.db.sql("""
#         SELECT title AS name 
#         FROM `tabSales Taxes and Charges Template` t
#         WHERE EXISTS (
#             SELECT 1 FROM `tabSales Taxes and Charges` tax
#             WHERE tax.parent = t.name AND tax.account_head = %s
#         )
#     """, (account_name,), as_dict=True)

# def get_purchase_tax_template_for_account(account_name):
#     return frappe.db.sql("""
#         SELECT category_name AS name 
#         FROM `tabTax Withholding Category` t
#         WHERE EXISTS (
#             SELECT 1 FROM `tabTax Withholding Account` tax
#             WHERE tax.parent = t.name AND tax.account = %s
#         )
#     """, (account_name,), as_dict=True)
import frappe
from frappe.utils import getdate, now
from datetime import timedelta

def execute(filters=None):
    filters = prepare_filters(filters)
    columns, column_keys = get_columns()
    data = get_data(filters, column_keys)
    return columns, data

def prepare_filters(filters):
    filters = filters or {}
    filters.setdefault("company", frappe.defaults.get_defaults().get("company"))
    
    if not any(filters.get(key) for key in ["quarter", "from_date", "to_date"]):
        filters["quarter"] = get_current_quarter()

    return filters

def get_columns():
    # Static columns
    columns = [
        {"label": "Declarant NIF", "fieldname": "declarant_nif", "fieldtype": "Data", "width": 120},
        {"label": "Declarant Name", "fieldname": "declarant_name", "fieldtype": "Data", "width": 140},
        {"label": "Fiscal Year", "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 103},
        {"label": "Period", "fieldname": "period", "fieldtype": "Data", "width": 90},
    ]

    # Fetch dynamic columns from Model Values
    dynamic_values = frappe.get_all(
        "Model Values",
        fields=["value_description", "idx"],
        filters={"parent": "Modelo 390"},
        order_by="idx asc"
    )

    column_keys = []  
    for row in dynamic_values:  
        fieldname = frappe.scrub(row["value_description"])
        columns.append({
            "label": row["value_description"],
            "fieldname": fieldname,
            "fieldtype": "Currency",
            "width": 190,
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
