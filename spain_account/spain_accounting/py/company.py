import frappe
from erpnext.setup.doctype.company.company import Company

class CompanyOverride(Company):
    def create_default_cost_center(self):
        custom_create_default_cost_center(self)
    def create_default_accounts(self):
        custom_create_default_accounts(self)
    def set_default_accounts(self):
        pass

def custom_create_default_cost_center(self):

    cc_list = [
        {
            "cost_center_name": self.name,
            "company": self.name,
            "is_group": 1,
            "parent_cost_center": None,
        },
        {
            "cost_center_name": "Main",
            "company": self.name,
            "is_group": 0,
            "parent_cost_center": self.name + " - " + self.abbr,
        },
    ]
    for cc in cc_list:
        cc.update({"doctype": "Cost Center"})
        cc_doc = frappe.get_doc(cc)
        cc_doc.flags.ignore_permissions = True

        if cc.get("cost_center_name") == self.name:
            cc_doc.flags.ignore_mandatory = True
        cc_doc.insert()
    
    # ? COMMENT THESE DEFAULT ACCOUNT
    # self.db_set("cost_center", "Main" + " - " + self.abbr)
    # self.db_set("round_off_cost_center", "Main" + " - " + self.abbr)
    # self.db_set("depreciation_cost_center", "Main" + " - " + self.abbr)


def custom_create_default_accounts(self):
		from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import create_charts

		frappe.local.flags.ignore_root_company_validation = True
		create_charts(self.name, self.chart_of_accounts, self.existing_company)

        # ? COMMENT THESE DEFAULT ACCOUNT
		# self.db_set(
		# 	"default_receivable_account",
		# 	frappe.db.get_value(
		# 		"Account", {"company": self.name, "account_type": "Receivable", "is_group": 0}
		# 	),  
		# )

		# self.db_set(
		# 	"default_payable_account",
		# 	frappe.db.get_value("Account", {"company": self.name, "account_type": "Payable", "is_group": 0}),
		# )



def create_account_enqueue(self, method):
    """
    Enqueue the account creation process if the company is set to create
    its chart of accounts based on a standard template.
    """
    if self.create_chart_of_accounts_based_on == "Standard Template":
        print("Creating account enqueue")
        frappe.enqueue(
            "spain_account.spain_accounting.py.charts_of_account_level.create_accounts",
            company=self.company_name,
            enqueue_after_commit=True,
            at_front=True,
        )