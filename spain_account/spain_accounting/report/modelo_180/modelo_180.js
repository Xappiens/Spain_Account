// Copyright (c) 2024, Xappiens and contributors
// For license information, please see license.txt

frappe.query_reports["Modelo 180"] = {
	"filters": [
        {
			fieldname: "company",
			label: __("Compañía"),
			fieldtype: "Link",
			options: "Company", 
			default: frappe.defaults.get_default('company')
		},
		{
			fieldname: "fiscal_year",
			label: __("Año Fiscal"),
			fieldtype: "Link",
			options: "Fiscal Year", 
			default: frappe.defaults.get_default('fiscal_year')
		}
	]
};
