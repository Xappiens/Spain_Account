import frappe


def create_level_1_accounts(level_1):
    frappe.db.sql("TRUNCATE TABLE `tabAccount`")
    frappe.db.commit()
    success = True
    for parent in level_1:
        try:
          doc = frappe.new_doc("Account")
          doc.account_name = parent["account_name"]
          doc.account_number = parent['account_number']
          doc.is_group = parent["is_group"]
          doc.company = parent['company']
          doc.parent_account = parent['parent_account']
          doc.account_type = parent['account_type']
          doc.root_type = parent['root_type']
          doc.account_currency = parent['account_currency']
          doc.report_type = parent['report_type']
          doc.insert(ignore_mandatory=True)
        except Exception as e:
          frappe.log_error("Error: While Auto Create Level 1 Account", f"Error: {e}\naccount_name: {parent['account_name']}\nlevel_1")
          success = False
    frappe.db.commit()
    return success

@frappe.whitelist()
def create_accounts():
    try:
      company = frappe.db.get_list("Company", fields=['company_name'], pluck='company_name')[0]
      currency = frappe.db.get_list("Company", fields=['default_currency'], pluck='default_currency')[0]
      abbr = frappe.db.get_list("Company", fields=['abbr'], pluck='abbr')[0]

      level_1: [
          {
            "account_name": "Basic financing",
            "is_group": 1,
            "company" : company
            "account_number": "1",
            "account_type": "",
            "parent_account": null,
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Balance Sheet"
          },
          {
            "account_name": "Sales andIncome",
            "is_group": 1,
            "company" : company
            "account_number": "7",
            "account_type": "",
            "parent_account": null,
            "account_currency": "EUR",
            "root_type": "Income",
            "report_type": "Profit and Loss"
            "account_currency": currency,

          },
          {
            "account_name": "Non-current assets",
            "is_group": 1,
            "account_number": "2",
            "account_type": "",
            "parent_account": null,
            "account_currency": "EUR",
            "root_type": "Asset",
            "report_type": "Balance Sheet"
            "company" : company
            "account_currency": currency,


          },
          {
            "account_name": "Stocks",
            "is_group": 1,
            "account_number": "3",
            "account_type": "",
            "parent_account": null,
            "account_currency": "EUR",
            "root_type": "Asset",
            "report_type": "Balance Sheet"
            "company" : company
            "account_currency": currency,


          },
          {
            "account_name": "Creditors and debtors for commercial operations",
            "is_group": 1,
            "account_number": "4",
            "account_type": "",
            "parent_account": null,
            "account_currency": "EUR",
            "root_type": "Liability",
            "report_type": "Balance Sheet"
            "company" : company
            "account_currency": currency,


          },
          {
            "account_name": "Financial accounts",
            "is_group": 1,
            "account_number": "5",
            "account_type": "",
            "parent_account": null,
            "account_currency": "EUR",
            "root_type": "Asset",
            "report_type": "Balance Sheet"
            "company" : company
            "account_currency": currency,


          },
          {
            "account_name": "Purchases andExpenses",
            "is_group": 1,
            "account_number": "6",
            "account_type": "",
            "parent_account": null,
            "account_currency": "EUR",
            "root_type": "Expense",
            "report_type": "Profit and Loss"
            "company" : company
            "account_currency": currency,


          },
          {
            "account_name": "Expenses charged to net worth",
            "is_group": 1,
            "account_number": "8",
            "account_type": "",
            "parent_account": null,
            "account_currency": "EUR",
            "root_type": "Expense",
            "report_type": "Profit and Loss"
            "company" : company
            "account_currency": currency,


          },
          {
            "account_name": "Income attributed to net worth",
            "is_group": 1,
            "account_number": "9",
            "account_type": "",
            "parent_account": null,
            "account_currency": "EUR",
            "root_type": "Income",
            "report_type": "Profit and Loss"
            "company" : company
            "account_currency": currency,


          }
        ]