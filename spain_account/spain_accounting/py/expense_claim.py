import frappe
import erpnext

@frappe.whitelist()
def get_expense_claim_account_and_cost_center(expense_claim_type, company):
	cost_center = erpnext.get_default_cost_center(company)

	return {"cost_center": cost_center}



import frappe
from hrms.hr.doctype.expense_claim.expense_claim import ExpenseClaim

class ExpenseClaimOverride(ExpenseClaim):
    def set_expense_account(self, validate=False):
        # Custom logic here
        pass
