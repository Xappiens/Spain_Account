import frappe
from erpnext.accounts.utils import get_balance_on
from frappe.utils import getdate


def execute(filters=None):

    if not filters:
        filters = {}

    if not filters.get("quarter"):
        filters["quarter"] = get_current_quarter()

    columns = [
        {
            "label": "Declarant NIF",
            "fieldname": "declarant_nif",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": "Declarant Name",
            "fieldname": "declarant_name",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": "Fiscal Year",
            "fieldname": "fiscal_year",
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "width": 100,
        },
        {"label": "Period", "fieldname": "period", "fieldtype": "Data", "width": 80},
        {
            "label": "Total VAT Sales Amount Subject",
            "fieldname": "total_vat_sales_amount_subject",
            "fieldtype": "Currency",
            "width": 190,
            "align": "center",
        },
        {
            "label": "Total VAT Collected",
            "fieldname": "total_vat_collected",
            "fieldtype": "Currency",
            "width": 190,
            "align": "center",
        },
        {
            "label": "Total VAT Paid",
            "fieldname": "total_vat_paid",
            "fieldtype": "Currency",
            "width": 190,
            "align": "center",
        },
        {
            "label": "VAT Payable/Refundable",
            "fieldname": "vat_payable_refundable",
            "fieldtype": "Currency",
            "width": 190,
            "align": "center",
        },
    ]

    data = get_data(filters)

    return columns, data


def get_data(filters):
    quarter = filters["quarter"]
    fiscal_year = filters.get("fiscal_year")
    start_date = None
    end_date = None

    if fiscal_year:
        start_date = frappe.db.get_value("Fiscal Year", fiscal_year, "year_start_date")
        end_date = frappe.db.get_value("Fiscal Year", fiscal_year, "year_end_date")

        if not quarter:
            quarter = get_fiscal_year_quarter(start_date, end_date)

    if quarter:
        quarter_start_date, quarter_end_date = get_quarter_date_range(quarter, start_date, end_date)

        start_date, end_date = quarter_start_date, quarter_end_date

    model_values = frappe.get_all(
        "Model Values",
        fields=[
            "value_description as description",
            "value_type",
            "calculation_rule__query",
        ],
        filters={"parent": "Modelo 303" }
    )
    results = {
        "period": quarter,
        "fiscal_year":fiscal_year,
        "total_vat_sales_amount_subject": 0,
        "total_vat_collected": 0,
        "total_vat_paid": 0,
        "vat_payable_refundable": 0,
    }
    if model_values :
        for value in model_values:

            query_result = execute_sql(value["calculation_rule__query"])
            if value["description"] == "Total Sales Amount Subject to VAT" and  query_result:
                sales_invoice_names = [invoice[0] for invoice in query_result]
                total_vat_sales_amount_subject = frappe.get_all(
                    "Sales Invoice",
                    filters={
                        "name": ["in", sales_invoice_names],  
                        "posting_date": [
                            "between",
                            [start_date, end_date],
                        ], 
                    },
                    fields=["sum(grand_total) as total_vat_sales_amount_subject"],
                )
                results["total_vat_sales_amount_subject"] = (
                    total_vat_sales_amount_subject[0].get('total_vat_sales_amount_subject', 0)
                    if total_vat_sales_amount_subject[0].get('total_vat_sales_amount_subject', 0)
                    else 0
                )

            elif value["description"] == "Total VAT Collected on Sales" and  query_result:
                sales_invoice_names = [invoice[0] for invoice in query_result]
                sql_query = """SELECT 
                        SUM(stc.tax_amount) AS total_vat_collected
                        FROM `tabSales Taxes and Charges` AS stc
                        INNER JOIN 
                            `tabSales Invoice` AS si
                            ON stc.parent = si.name
                        WHERE si.name IN %(invoice_names)s
                        AND si.posting_date BETWEEN %(start_date)s AND %(end_date)s;"""
                value_count = execute_sql(
                    sql_query, sales_invoice_names, start_date, end_date
                )
                results["total_vat_collected"] = (
                    value_count[0].get("total_vat_collected")
                    if value_count[0].get("total_vat_collected")
                    else 0
                )

            elif value["description"] == "Total VAT Paid on Purchases" and  query_result:
                if query_result:
                    purchase_invoice_names = [invoice[0] for invoice in query_result]
                    sql_query = """SELECT 
                            SUM(ptc.tax_amount) AS total_vat_paid
                            FROM `tabPurchase Taxes and Charges` AS ptc
                            INNER JOIN 
                                `tabPurchase Invoice` AS pi
                                ON ptc.parent = pi.name
                            WHERE ptc.name IN %(invoice_names)s
                            AND pi.posting_date BETWEEN %(start_date)s AND %(end_date)s;"""
                    value_count = execute_sql(
                        sql_query, purchase_invoice_names, start_date, end_date
                    )
                results["total_vat_paid"] = (
                    value_count[0].get("total_vat_paid")
                    if value_count[0].get("total_vat_paid")
                    else 0
                )

        results["vat_payable_refundable"] = (
            results["total_vat_collected"] - results["total_vat_paid"]
        )

        return [results]


def execute_sql(sql_query, invoice=None, start_date=None, end_date=None):
    if start_date is None and end_date is None:
        result = frappe.db.sql(sql_query)
    else:
        result = frappe.db.sql(
            sql_query,
            {"invoice_names": invoice, "start_date": start_date, "end_date": end_date},
            as_dict=True,
        )

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


def get_quarter_date_range(quarter, fiscal_start_date, fiscal_end_date):
    """Return the date range for the given quarter within the fiscal year."""
    year = getdate(frappe.utils.now()).year


    if fiscal_start_date and fiscal_end_date:
        year = getdate(fiscal_start_date).year
    
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

def get_fiscal_year_quarter(fiscal_start_date, fiscal_end_date):
    """Determine the quarter based on fiscal year date range."""
    current_date = getdate(frappe.utils.now())

    if fiscal_start_date <= current_date <= fiscal_end_date:
        if fiscal_start_date <= current_date <= getdate(fiscal_start_date).replace(month=3, day=31):
            return "1Q"
        elif fiscal_start_date <= current_date <= getdate(fiscal_start_date).replace(month=6, day=30):
            return "2Q"
        elif fiscal_start_date <= current_date <= getdate(fiscal_start_date).replace(month=9, day=30):
            return "3Q"
        elif fiscal_start_date <= current_date <= getdate(fiscal_start_date).replace(month=12, day=31):
            return "4Q"
