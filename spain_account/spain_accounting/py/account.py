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

        if doc.is_group:
            if records and len(records) > 0:
                new_account_number = int(records[0]["account_number"]) + 1
            else:
                parent_account_number = int(doc.parent_account.split(" ")[0])
                new_account_number = parent_account_number * 10
        else:
            if records and len(records) > 0:
                new_account_number = int(records[0]["account_number"]) + 1
            else:
                parent_account_number = doc.parent_account.split(" ")[0]
                new_account_number = parent_account_number.ljust(8, "0")

        doc.account_number = str(new_account_number)
