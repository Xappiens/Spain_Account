frappe.query_reports["Modelo 190"] = {
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