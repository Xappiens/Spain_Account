import frappe
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals

# MODIFY THE CHARGE_TYPE FOR TDS-RELATED TAX ROWS TO 'ON NET TOTAL' AFTER THE INVOICE IS SAVED
def modify_tds_tax_row(doc, method):

    if doc.apply_tds :
        tax_withholding_category = frappe.db.get_value("Tax Withholding Rate", {"parent":doc.tax_withholding_category},"tax_withholding_rate")
        for tax_row in doc.taxes:
            if tax_row.is_tax_withholding_account:
                tax_row.rate = tax_withholding_category
                if tax_row.charge_type == "Actual":  
                    tax_row.charge_type = "On Net Total"  
                tax_row.save()  
        
        # RE-CALCULATE TAXES AND TOTALS AFTER MODIFYING THE CHARGE_TYPE
        calculate_taxes_and_totals(doc)
        frappe.db.commit()
        doc.reload()
