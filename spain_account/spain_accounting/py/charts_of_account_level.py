import frappe
def create_level_1_accounts(level_1):
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

def create_level_2_accounts(level_2):
    success = True
    for parent in level_2:
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
          doc.insert(ignore_permissions=True, ignore_mandatory=True)
        except Exception as e:
            frappe.log_error("Error: While Auto Create Level 2 Account", f"Error: {e}\naccount_name: {parent['account_name']}\nlevel_2")
            success = False
    frappe.db.commit()
    return success

# def create_level_3_accounts(level_3):
#     success = True
#     for parent in level_3:
#         try:
#           doc = frappe.new_doc("Account")
#           doc.account_name = parent["account_name"]
#           doc.account_number = parent['account_number']
#           doc.is_group = parent["is_group"]
#           doc.company = parent['company']
#           doc.parent_account = parent['parent_account']
#           doc.account_type = parent['account_type']
#           doc.root_type = parent['root_type']
#           doc.account_currency = parent['account_currency']
#           doc.report_type = parent['report_type']
#           doc.insert(ignore_permissions=True, ignore_mandatory=True)
#         except Exception as e:
#             frappe.log_error("Error: While Auto Create Level 3 Account", f"Error: {e}\naccount_name: {parent['account_name']}\nlevel_3")
#             success = False
#     frappe.db.commit()
#     return success
  
  
# def create_level_4_accounts(level_4):
#     success = True
#     for parent in level_4:
#         try:
#           doc = frappe.new_doc("Account")
#           doc.account_name = parent["account_name"]
#           doc.account_number = parent['account_number']
#           doc.is_group = parent["is_group"]
#           doc.company = parent['company']
#           doc.parent_account = parent['parent_account']
#           doc.account_type = parent['account_type']
#           doc.root_type = parent['root_type']
#           doc.account_currency = parent['account_currency']
#           doc.report_type = parent['report_type']
#           doc.insert(ignore_permissions=True, ignore_mandatory=True)
#         except Exception as e:
#             frappe.log_error("Error: While Auto Create Level 4 Account", f"Error: {e}\naccount_name: {parent['account_name']}\nlevel_4")
#             success = False
#     frappe.db.commit()
#     return success



@frappe.whitelist()
def create_accounts():
  print("Function is Running")
  try:
      company = frappe.db.get_list("Company", fields=['company_name'], pluck='company_name')[0]
      currency = frappe.db.get_list("Company", fields=['default_currency'], pluck='default_currency')[0]
      abbr = frappe.db.get_list("Company", fields=['abbr'], pluck='abbr')[0]

      level_1 = [
        {
          "account_name": "Basic financing",
          "is_group": 1,
          "company":company,
          "account_currency":currency,
          "account_number": "1",
          "account_type": "",
          "parent_account": "",
          "root_type": "Asset",
          "report_type": "Balance Sheet"
        },
        {
          "account_name": "Sales andIncome",
          "is_group": 1,
          "account_number": "7",
          "account_type": "",
          "parent_account": "",
          "root_type": "Income",
          "company":company,
          "account_currency":currency,
          "report_type": "Profit and Loss"
        },
        {
          "account_name": "Non-current assets",
          "is_group": 1,
          "account_number": "2",
          "account_type": "",
          "parent_account": "",
          "root_type": "Asset",
          "company":company,
          "account_currency":currency,
          "report_type": "Balance Sheet"
        },
        {
          "account_name": "Stocks",
          "is_group": 1,
          "account_number": "3",
          "account_type": "",
          "parent_account": "",
          "root_type": "Asset",
          "company":company,
          "account_currency":currency,
          "report_type": "Balance Sheet"
        },
        {
          "account_name": "Creditors and debtors for commercial operations",
          "is_group": 1,
          "account_number": "4",
          "account_type": "",
          "parent_account": "",
          "root_type": "Liability",
          "company":company,
          "account_currency":currency,
          "report_type": "Balance Sheet"
        },
        {
          "account_name": "Financial accounts",
          "is_group": 1,
          "account_number": "5",
          "account_type": "",
          "parent_account": "",
          "root_type": "Asset",
          "company":company,
          "account_currency":currency,
          "report_type": "Balance Sheet"
        },
        {
          "account_name": "Purchases andExpenses",
          "is_group": 1,
          "account_number": "6",
          "account_type": "",
          "parent_account": "",
          "root_type": "Expense",
          "company":company,
          "account_currency":currency,
          "report_type": "Profit and Loss"
        },
        {
          "account_name": "Expenses charged to net worth",
          "is_group": 1,
          "account_number": "8",
          "account_type": "",
          "parent_account": "",
          "company":company,
          "account_currency":currency,
          "root_type": "Expense",
          "report_type": "Profit and Loss"
        },
        {
          "account_name": "Income attributed to net worth",
          "is_group": 1,
          "account_number": "9",
          "account_type": "",
          "parent_account": "",
          "company":company,
          "account_currency":currency,
          "root_type": "Income",
          "report_type": "Profit and Loss"
        }         
      ]

      level_2 = [
        {
            "account_name": "CAPITAL",
            "company": company,
            "is_group": 1,
            "account_number": 10,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "RESERVES AND OTHER HERITAGE INSTRUMENTS",
            "company": company,
            "is_group": 1,
            "account_number": 11,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "RESULTS PENDING APPLICATION",
            "company": company,
            "is_group": 1,
            "account_number": 12,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "GRANTS, DONATIONS AND ADJUSTMENTS FOR CHANGES IN VALUE",
            "company": company,
            "is_group": 1,
            "account_number": 13,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "PROVISIONS",
            "company": company,
            "is_group": 1,
            "account_number": 14,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "LONG-TERM DEBTS WITH SPECIAL CHARACTERISTICS",
            "company": company,
            "is_group": 1,
            "account_number": 15,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "LONG-TERM DEBTS WITH RELATED PARTIES",
            "company": company,
            "is_group": 1,
            "account_number": 16,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "LONG-TERM DEBTS FOR LOANS RECEIVED, BORROWING AND OTHER CONCEPTS",
            "company": company,
            "is_group": 1,
            "account_number": 17,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "LIABILITIES FOR SURETY, GUARANTEES AND OTHER LONG-TERM CONCEPTS",
            "company": company,
            "is_group": 1,
            "account_number": 18,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "TRANSITIONAL FINANCING SITUATIONS",
            "company": company,
            "is_group": 1,
            "account_number": 19,
            "account_type": "",
            "parent_account": f"1 - Basic financing - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "INTANGIBLE IMMOBILIZATIONS",
            "company": company,
            "is_group": 1,
            "account_number": 20,
            "account_type": "",
            "parent_account": f"2 - Non-current assets - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "MATERIAL IMMOBILIZATIONS",
            "company": company,
            "is_group": 1,
            "account_number": 21,
            "account_type": "",
            "parent_account": f"2 - Non-current assets - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "REAL ESTATE INVESTMENTS",
            "company": company,
            "is_group": 1,
            "account_number": 22,
            "account_type": "",
            "parent_account": f"2 - Non-current assets - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "MATERIAL IMMOBILIZATIONS IN PROGRESS",
            "company": company,
            "is_group": 1,
            "account_number": 23,
            "account_type": "",
            "parent_account": f"2 - Non-current assets - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "LONG-TERM FINANCIAL INVESTMENTS IN RELATED PARTIES",
            "company": company,
            "is_group": 1,
            "account_number": 24,
            "account_type": "",
            "parent_account": f"2 - Non-current assets - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "OTHER LONG-TERM FINANCIAL INVESTMENTS",
            "company": company,
            "is_group": 1,
            "account_number": 25,
            "account_type": "",
            "parent_account": f"2 - Non-current assets - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "LONG-TERM SURETIES AND DEPOSITS",
            "company": company,
            "is_group": 1,
            "account_number": 26,
            "account_type": "",
            "parent_account": f"2 - Non-current assets - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "ACCUMULATED AMORTIZATION OF FIXED ASSETS",
            "company": company,
            "is_group": 1,
            "account_number": 28,
            "account_type": "",
            "parent_account": f"2 - Non-current assets - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "IMPAIRMENT OF NON-CURRENT ASSETS",
            "company": company,
            "is_group": 1,
            "account_number": 29,
            "account_type": "",
            "parent_account": f"2 - Non-current assets - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "COMMERCIALS",
            "company": company,
            "is_group": 1,
            "account_number": 30,
            "account_type": "",
            "parent_account": f"3 - Stocks - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "RAW MATERIALS",
            "company": company,
            "is_group": 1,
            "account_number": 31,
            "account_type": "",
            "parent_account": f"3 - Stocks - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "OTHER SUPPLIES",
            "company": company,
            "is_group": 1,
            "account_number": 32,
            "account_type": "",
            "parent_account": f"3 - Stocks - {abbr}",
            "account_currency": currency,
            "root_type": "Liability",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "PRODUCTS IN PROGRESS",
            "company": company,
            "is_group": 1,
            "account_number": 33,
            "account_type": "",
            "parent_account": f"3 - Stocks - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "SEMI-FINISHED PRODUCTS",
            "company": company,
            "is_group": 1,
            "account_number": 34,
            "account_type": "",
            "parent_account": f"3 - Stocks - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "FINISHED PRODUCTS",
            "company": company,
            "is_group": 1,
            "account_number": 35,
            "account_type": "",
            "parent_account": f"3 - Stocks - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "BY-PRODUCTS, WASTE AND RECOVERED MATERIALS",
            "company": company,
            "is_group": 1,
            "account_number": 36,
            "account_type": "",
            "parent_account": f"3 - Stocks - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "DETERIORATION OF VALUE OF STOCK",
            "company": company,
            "is_group": 1,
            "account_number": 39,
            "account_type": "",
            "parent_account": f"3 - Stocks - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "SUPPLIERS",
            "company": company,
            "is_group": 1,
            "account_number": 40,
            "account_type": "",
            "parent_account": f"4 - Creditors and debtors for commercial operations - {abbr}",
            "account_currency": currency,
            "root_type": "Liability",
            "report_type": "Balance Sheet"
        },
        {
            "account_name": "MISCELLANEOUS CREDITORS",
            "company": company,
            "is_group": 1,
            "account_number": 41,
            "account_type": "",
            "parent_account": f"4 - Creditors and debtors for commercial operations - {abbr}",
            "account_currency": currency,
            "root_type": "Liability",
            "report_type": "Balance Sheet"
        },
        {
            "account_name": "CUSTOMERS",
            "company": company,
            "is_group": 1,
            "account_number": 43,
            "account_type": "",
            "parent_account": f"4 - Creditors and debtors for commercial operations - {abbr}",
            "account_currency": currency,
            "root_type": "Liability",
            "report_type": "Balance Sheet"
        },
        {
            "account_name": "MISCELLANEOUS DEBTORS",
            "company": company,
            "is_group": 1,
            "account_number": 44,
            "account_type": "",
            "parent_account": f"4 - Creditors and debtors for commercial operations - {abbr}",
            "account_currency": currency,
            "root_type": "Liability",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "PERSONNEL",
            "company": company,
            "is_group": 1,
            "account_number": 46,
            "account_type": "",
            "parent_account": f"4 - Creditors and debtors for commercial operations - {abbr}",
            "account_currency": currency,
            "root_type": "Liability",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "PUBLIC ADMINISTRATIONS",
            "company": company,
            "is_group": 1,
            "account_number": 47,
            "account_type": "",
            "parent_account": f"4 - Creditors and debtors for commercial operations - {abbr}",
            "account_currency": currency,
            "root_type": "Liability",
            "report_type": "Balance Sheet"
        },
        {
            "account_name": "PERIODIFICATION ADJUSTMENTS",
            "company": company,
            "is_group": 1,
            "account_number": 48,
            "account_type": "",
            "parent_account": f"4 - Creditors and debtors for commercial operations - {abbr}",
            "account_currency": currency,
            "root_type": "Liability",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "IMPAIRMENT OF TRADE CREDITS AND SHORT-TERM PROVISIONS",
            "company": company,
            "is_group": 1,
            "account_number": 49,
            "account_type": "",
            "parent_account": f"4 - Creditors and debtors for commercial operations - {abbr}",
            "account_currency": currency,
            "root_type": "Liability",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "LOANS, DEBTS WITH SPECIAL CHARACTERISTICS AND OTHER SIMILAR SHORT-TERM ISSUES",
            "company": company,
            "is_group": 1,
            "account_number": 50,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "SHORT-TERM DEBTS WITH RELATED PARTIES",
            "company": company,
            "is_group": 1,
            "account_number": 51,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "SHORT-TERM DEBTS FOR LOANS RECEIVED AND OTHER CONCEPTS",
            "company": company,
            "is_group": 1,
            "account_number": 52,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "SHORT-TERM FINANCIAL INVESTMENTS IN RELATED PARTIES",
            "company": company,
            "is_group": 1,
            "account_number": 53,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "OTHER SHORT-TERM FINANCIAL INVESTMENTS",
            "company": company,
            "is_group": 1,
            "account_number": 54,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "OTHER NON-BANK ACCOUNTS",
            "company": company,
            "is_group": 1,
            "account_number": 55,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "SURETIES AND DEPOSITS RECEIVED AND CONSTITUTED IN THE SHORT TERM AND ADJUSTMENTS BY PERIODIFICATION",
            "company": company,
            "is_group": 1,
            "account_number": 56,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "TREASURY",
            "company": company,
            "is_group": 1,
            "account_number": 57,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "NON-CURRENT ASSETS HELD FOR SALE AND ASSOCIATED ASSETS AND LIABILITIES",
            "company": company,
            "is_group": 1,
            "account_number": 58,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "IMPAIRMENT OF SHORT-TERM FINANCIAL INVESTMENTS AND NON-CURRENT ASSETS HELD FOR SALE",
            "company": company,
            "is_group": 1,
            "account_number": 59,
            "account_type": "",
            "parent_account": f"5 - Financial accounts - {abbr}",
            "account_currency": currency,
            "root_type": "Asset",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "SHOPPING",
            "company": company,
            "is_group": 1,
            "account_number": 60,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "STOCK VARIATION",
            "company": company,
            "is_group": 1,
            "account_number": 61,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "EXTERNAL SERVICES",
            "company": company,
            "is_group": 1,
            "account_number": 62,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "TRIBUTES",
            "company": company,
            "is_group": 1,
            "account_number": 63,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "PERSONNELExpenseS",
            "company": company,
            "is_group": 1,
            "account_number": 64,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "OTHER MANAGEMENTExpenseS",
            "company": company,
            "is_group": 1,
            "account_number": 65,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "FINANCIALExpenseS",
            "company": company,
            "is_group": 1,
            "account_number": 66,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "LOSSES FROM NON-CURRENT ASSETS AND EXCEPTIONALExpenseS",
            "company": company,
            "is_group": 1,
            "account_number": 67,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "PROVISIONS FOR AMORTIZATION",
            "company": company,
            "is_group": 1,
            "account_number": 68,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "IMPAIRMENT LOSSES AND OTHER PROVISIONS",
            "company": company,
            "is_group": 1,
            "account_number": 69,
            "account_type": "",
            "parent_account": f"6 - Purchases andExpenses - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "SALES OF MERCHANDISE, OWN PRODUCTION, SERVICES, ETC",
            "company": company,
            "is_group": 1,
            "account_number": 70,
            "account_type": "",
            "parent_account": f"7 - Sales andIncome - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "STOCK VARIATION",
            "company": company,
            "is_group": 1,
            "account_number": 71,
            "account_type": "",
            "parent_account": f"7 - Sales andIncome - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "WORK CARRIED OUT FOR THE COMPANY",
            "company": company,
            "is_group": 1,
            "account_number": 73,
            "account_type": "",
            "parent_account": f"7 - Sales andIncome - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "GRANTS, DONATIONS AND LEGACIES",
            "company": company,
            "is_group": 1,
            "account_number": 74,
            "account_type": "",
            "parent_account": f"7 - Sales andIncome - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "OTHER MANAGEMENTIncome",
            "company": company,
            "is_group": 1,
            "account_number": 75,
            "account_type": "",
            "parent_account": f"7 - Sales andIncome - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "FINANCIALIncome",
            "company": company,
            "is_group": 1,
            "account_number": 76,
            "account_type": "",
            "parent_account": f"7 - Sales andIncome - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "PROFITS FROM NON-CURRENT ASSETS AND EXCEPTIONALIncome",
            "company": company,
            "is_group": 1,
            "account_number": 77,
            "account_type": "",
            "parent_account": f"7 - Sales andIncome - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "EXCESSES AND APPLICATIONS OF PROVISIONS AND IMPAIRMENT LOSSES",
            "company": company,
            "is_group": 1,
            "account_number": 79,
            "account_type": "",
            "parent_account": f"7 - Sales andIncome - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "FINANCIALExpenseS FOR VALUATION OF ASSETS AND LIABILITIES",
            "company": company,
            "is_group": 1,
            "account_number": 80,
            "account_type": "",
            "parent_account": f"8 - Expenses charged to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "ExpenseS IN COVERAGE OPERATIONS",
            "company": company,
            "is_group": 1,
            "account_number": 81,
            "account_type": "",
            "parent_account": f"8 - Expenses charged to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "ExpenseS FOR CONVERSION DIFFERENCES",
            "company": company,
            "is_group": 1,
            "account_number": 82,
            "account_type": "",
            "parent_account": f"8 - Expenses charged to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "Income TAX",
            "company": company,
            "is_group": 1,
            "account_number": 83,
            "account_type": "",
            "parent_account": f"8 - Expenses charged to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "TRANSFERS OF GRANTS, DONATIONS AND LEGACIES",
            "company": company,
            "is_group": 1,
            "account_number": 84,
            "account_type": "",
            "parent_account": f"8 - Expenses charged to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "ACTUARIAL LOSSExpenseS AND ADJUSTMENTS TO ASSETS FOR LONG-TERM DEFINED BENEFIT COMPENSATION",
            "company": company,
            "is_group": 1,
            "account_number": 85,
            "account_type": "",
            "parent_account": f"8 - Expenses charged to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "ExpenseS FOR NON-CURRENT ASSETS FOR SALE",
            "company": company,
            "is_group": 1,
            "account_number": 86,
            "account_type": "",
            "parent_account": f"8 - Expenses charged to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "ExpenseS OF EQUITY IN GROUP OR ASSOCIATED COMPANIES WITH PREVIOUS POSITIVE VALUATION ADJUSTMENTS",
            "company": company,
            "is_group": 1,
            "account_number": 89,
            "account_type": "",
            "parent_account": f"8 - Expenses charged to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Expense",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "FINANCIALIncome BY VALUATION OF ASSETS AND LIABILITIES",
            "company": company,
            "is_group": 1,
            "account_number": 90,
            "account_type": "",
            "parent_account": f"9 - Income attributed to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "Income FROM HEDGE OPERATIONS",
            "company": company,
            "is_group": 1,
            "account_number": 91,
            "account_type": "",
            "parent_account": f"9 - Income attributed to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "Income FROM CONVERSION DIFFERENCES",
            "company": company,
            "is_group": 1,
            "account_number": 92,
            "account_type": "",
            "parent_account": f"9 - Income attributed to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "Income FROM SUBSIDIES, DONATIONS AND LEGACIES",
            "company": company,
            "is_group": 1,
            "account_number": 94,
            "account_type": "",
            "parent_account": f"9 - Income attributed to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "Income FROM ACTUARIAL GAINS AND ADJUSTMENTS TO ASSETS FOR LONG-TERM DEFINED BENEFIT COMPENSATION",
            "company": company,
            "is_group": 1,
            "account_number": 95,
            "account_type": "",
            "parent_account": f"9 - Income attributed to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "Income FROM NON-CURRENT ASSETS FOR SALE",
            "company": company,
            "is_group": 1,
            "account_number": 96,
            "account_type": "",
            "parent_account": f"9 - Income attributed to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
        {
            "account_name": "Income FROM SHARES IN GROUP OR ASSOCIATED COMPANIES WITH PREVIOUS NEGATIVE VALUATION ADJUSTMENTS",
            "company": company,
            "is_group": 1,
            "account_number": 99,
            "account_type": "",
            "parent_account": f"9 - Income attributed to net worth - {abbr}",
            "account_currency": currency,
            "root_type": "Income",
            "report_type": "Profit and Loss"
        },
      ]


      frappe.db.sql("TRUNCATE TABLE `tabAccount`")
      frappe.db.commit()
      if create_level_1_accounts(level_1):
        create_level_2_accounts(level_2)
      
  except Exception as e:
        frappe.log_error("Error: While auto create accounts after setup", f"Error: {e}")