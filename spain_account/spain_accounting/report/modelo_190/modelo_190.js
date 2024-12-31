// Copyright (c) 2024, Xappiens and contributors
// For license information, please see license.txt

frappe.query_reports["Modelo 190"] = {
	"filters": [
        {
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company", 
			default: frappe.defaults.get_default('company')
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