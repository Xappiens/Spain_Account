// Copyright (c) 2024, Xappiens and contributors
// For license information, please see license.txt

frappe.query_reports["Modelo 303"] = {
	"filters": [
		{
            fieldname: "quarter",
            label: __("Quarter"),
            fieldtype: "Select",
            options: ["" ,"1Q", "2Q", "3Q", "4Q"],
        },
        {
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year", 
			
			default: frappe.defaults.get_default('fiscal_year')
		}
	]
};
