import frappe
from hrms.hr.doctype.expense_claim.expense_claim import ExpenseClaim
from frappe import _

# Override when an Expense Claim is submitted
def custom_on_submit(self):
    if self.approval_status == "Draft":
        frappe.throw(_("Approval Status must be 'Approved' or 'Rejected'"))
    self.update_task_and_project()

# Override before an Expense Claim is submitted
def custom_before_submit(self):
    pass

# Override when an Expense Claim is canceled
def custom_on_cancel(self):
    self.update_task_and_project()
    self.ignore_linked_doctypes = ("GL Entry", "Stock Ledger Entry", "Payment Ledger Entry")
    self.publish_update()
    
# Override default Expense Claim methods with custom methods
ExpenseClaim.on_submit = custom_on_submit
ExpenseClaim.before_submit = custom_before_submit
ExpenseClaim.on_cancel = custom_on_cancel
