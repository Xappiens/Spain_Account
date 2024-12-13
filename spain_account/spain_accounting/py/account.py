import frappe

# FUNCTION TO SET ACCOUNT NUMBER BASED ON PARENT ACCOUNT AND IS_GROUP
def set_account_number(doc, method):
    if not doc.custom_no_cuenta_personalizado:

        records = frappe.db.get_list("Account", 
            filters={
                "parent_account": doc.parent_account
            },
            fields=["account_number"],
            order_by="account_number desc",
            limit=1
        )
        new_account_number = None
        if records and len(records) > 0:
            new_account_number = int(records[0]["account_number"]) + 1
        doc.account_number = str(new_account_number)
