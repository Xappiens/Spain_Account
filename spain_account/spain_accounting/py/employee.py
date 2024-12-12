import frappe 

def create_employee_account(self, method):
    try:
        # Fetch parent account based on account_number
        parent_account = frappe.db.get_value("Account", {"account_number": "640", "company": self.company}, "name")
        
        # Create a new Account document for the employee
        account = frappe.get_doc(
            dict(
                doctype="Account",
                is_group=0,  
                account_name=self.employee_name,  
                account_type="Expense Account",
                parent_account=parent_account,  
                company=self.company,  
                account_currency=self.salary_currency,
                custom_es_cuenta_de_empleado=1,
                custom_empleado = self.name    

            )
        )
        
        # Save the account
        account.save()
        
    except Exception as e:
        frappe.throw(f"Error while creating employee account: {str(e)}") 
