import frappe

@frappe.whitelist()
def after_setup(spain_accounts=None):
    print("function is running")
    # print("Received spain_accounts:", spain_accounts)  # Debugging line
    # # if spain_accounts == '1':
    # #     job = frappe.enqueue("spain_account.spain_accounting.py.charts_of_account_level.create_accounts")
    # #     if job:
    # #         print("Job enqueued successfully. Job ID:", job)
    # #     else:
    # #         print("Failed to enqueue job.")