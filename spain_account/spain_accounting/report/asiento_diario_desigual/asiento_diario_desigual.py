import frappe
from frappe import _

def get_uneven_journal_entries(filters=None):
    query = """
        SELECT je.name AS journal_entry, 
               je.posting_date, 
               je.total_debit, 
               je.total_credit, 
               je.docstatus AS status, 
               je.title, 
               je.voucher_type, 
               je.company, 
               je.cheque_no,
               CASE 
                   WHEN je.docstatus = 0 THEN 'Draft'
                   WHEN je.docstatus = 1 THEN 'Submitted'
                   WHEN je.docstatus = 2 THEN 'Cancelled'
               END AS status_label
        FROM `tabJournal Entry` je
        WHERE je.total_debit != je.total_credit
    """

    # Apply filters if provided
    if filters:
        if filters.get("from_date"):
            query += " AND je.posting_date >= '{0}'".format(filters.get("from_date"))
        if filters.get("to_date"):
            query += " AND je.posting_date <= '{0}'".format(filters.get("to_date"))
        if filters.get("journal_entry"):
            query += " AND je.name LIKE '%{0}%'".format(filters.get("journal_entry"))
        if filters.get("title"):
            query += " AND je.title LIKE '%{0}%'".format(filters.get("title"))
        if filters.get("voucher_type"):
            query += " AND je.voucher_type LIKE '%{0}%'".format(filters.get("voucher_type"))
        if filters.get("company"):
            query += " AND je.company LIKE '%{0}%'".format(filters.get("company"))

    result = frappe.db.sql(query, as_dict=True)

    return result

def execute(filters=None):
    data = get_uneven_journal_entries(filters)

    # Define columns to be shown in the report
    columns = [
        {
            "fieldname": "journal_entry",
            "label": _("ID"),
            "fieldtype": "Link",
            "options": "Journal Entry",
            "width": 120
        },
        {
            "fieldname": "posting_date",
            "label": _("Fecha de Registro"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "status_label",
            "label": _("Estado"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "title",
            "label": _("Título"),
            "fieldtype": "Data",
            "width": 140
        },
        {
            "fieldname": "voucher_type",
            "label": _("Tipo de Asiento"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "company",
            "label": _("Compañía"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 120
        },
        {
            "fieldname": "cheque_no",
            "label": _("Número de Referencia"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "total_debit",
            "label": _("Total Débito"),
            "fieldtype": "Currency",
            "width": 170
        },
        {
            "fieldname": "total_credit",
            "label": _("Total Crédito"),
            "fieldtype": "Currency",
            "width": 170
        }
    ]

    # Add the totals row
    total_debit = sum(row['total_debit'] for row in data)
    total_credit = sum(row['total_credit'] for row in data)
    
    # Add the totals as the last row
    data.append({
        "journal_entry": _("Total"),
        "posting_date": "",
        "status_label": "",  
        "title": "",
        "voucher_type": "",
        "company": "",
        "cheque_no": "",
        "total_debit": total_debit,
        "total_credit": total_credit,
    })

    return columns, data
