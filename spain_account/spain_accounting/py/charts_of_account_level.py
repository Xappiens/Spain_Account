import frappe

import frappe

@frappe.whitelist()
def get_account_hierarchy():
    # Fetch all top-level parent accounts
    parent_accounts = frappe.db.get_list(
        "Account", 
        filters={"is_group": 1,"parent_account": ""},
        fields=["account_name","name", "company", "is_group", "account_number", "account_type", "parent_account","account_currency","root_type", "report_type"]
    )

    account_hierarchy = []
    # account_hierarchy.append({
    #                 "parent_accounts": parent_accounts
    #             })

    # return account_hierarchy 


    for account in parent_accounts:
        print(account["name"])
        
        # Fetch child accounts for the current parent account
        children = frappe.db.get_list(
            "Account", 
            filters={"parent_account": account["name"]},
            fields=["account_name","name", "company", "is_group", "account_number", "account_type", "parent_account","account_currency","root_type", "report_type"]
        )
    #     account_hierarchy.append({
    #             "children": children
    #     })
    # return account_hierarchy 

        for child in children:
            # Fetch accounts where parent_account equals the current child's name
            sub_child = frappe.db.get_list(
                "Account", 
                filters={"parent_account": child["name"]},
                fields=["account_name","name", "company", "is_group", "account_number", "account_type", "parent_account","account_currency","root_type", "report_type"]
            )
            account_hierarchy.append({
                "sub_child": sub_child
            })
        return account_hierarchy
            

        #     for sub_account in sub_child:
        #         sub_accounts =  frappe.db.get_list(
        #         "Account", 
        #         filters={"company": "ERP Next Latinoamérica, S. Ep.", "parent_account": sub_account["name"]},
        #         fields=["account_name","name", "company", "is_group", "account_number", "account_type", "parent_account","account_currency","root_type", "report_type"]
            
        #     )

               
            


   
         


