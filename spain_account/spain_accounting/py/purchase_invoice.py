import frappe
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals

# MODIFY THE CHARGE_TYPE FOR TDS-RELATED TAX ROWS TO 'ON NET TOTAL' ON VALIDATE
# def modify_tds_tax_row(doc, method):

#    if doc.apply_tds:
#         # Fetch the tax withholding rate based on the selected category
#         tax_withholding_rate = frappe.db.get_value(
#             "Tax Withholding Rate",
#             {"parent": doc.tax_withholding_category},
#             "tax_withholding_rate"
#         )

#         for tax_row in doc.taxes:
#             # Identify TDS tax rows
#             if tax_row.is_tax_withholding_account:
#                 tax_row.rate = tax_withholding_rate

#                 # Change charge type if it is 'Actual'
#                 if tax_row.charge_type == "Actual":
#                     tax_row.charge_type = "On Net Total"

#         # Recalculate taxes and totals after making changes
#         calculate_taxes_and_totals(doc)
