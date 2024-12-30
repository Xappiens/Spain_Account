import frappe

def create_employee_account(self, method):
    try:
        # Fetch parent account based on account_number
        parent_account = frappe.db.get_value("Account", {"account_number": "640", "company": self.company}, "name")
        
        if not parent_account:
            frappe.throw("Parent account with account_number 640 not found.")
        
        # Get the latest account number under the same parent account
        records = frappe.db.get_list("Account", 
            filters={"parent_account": parent_account, "company": self.company},
            fields=["account_number"],
            order_by="account_number desc",
            limit=1
        )
        
        # Set the base account number
        parent_account_number = "640"
        new_account_number = parent_account_number.ljust(8, "0")  # Default account number
        
        if records:
            # Increment the latest account number
            last_account_number = records[0].get("account_number", parent_account_number)
            try:
                new_account_number = str(int(last_account_number) + 1).zfill(8)
            except ValueError:
                frappe.throw(f"Invalid account number format found: {last_account_number}")

        # Create a new Account document for the employee
        account = frappe.get_doc(
            dict(
                doctype="Account",
                is_group=0,  
                account_name=self.employee_name,  
                account_type="Payable",
                parent_account=parent_account,  
                company=self.company,  
                account_currency=self.salary_currency,
                custom_es_cuenta_de_empleado=1,
                custom_empleado=self.name,
                account_number=new_account_number
            )
        )

        account.insert()  # Use insert instead of save() to avoid overwriting if document exists

    except frappe.exceptions.ValidationError as ve:
        raise ve  # Re-raise validation exceptions for more granular error handling
    except Exception as e:
        frappe.throw(f"Error while creating employee account: {str(e)}")
