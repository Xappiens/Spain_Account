import frappe
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals

# MODIFY THE CHARGE_TYPE FOR TDS-RELATED TAX ROWS TO 'ON NET TOTAL' AFTER THE INVOICE IS SAVED
def modify_tds_tax_row(doc, method):

    if doc.apply_tds :
        for tax_row in doc.taxes:
                if tax_row.charge_type == "Actual":  
                    tax_row.charge_type = "On Net Total"  
                    tax_row.save()  
    
        # RE-CALCULATE TAXES AND TOTALS AFTER MODIFYING THE CHARGE_TYPE
        calculate_taxes_and_totals(doc)
        frappe.db.commit()
