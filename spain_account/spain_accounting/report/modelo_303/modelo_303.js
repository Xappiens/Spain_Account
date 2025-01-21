// Copyright (c) 2024, Xappiens and contributors
// For license information, please see license.txt

frappe.query_reports["Modelo 303"] = {
	"filters": [
        {
			fieldname: "company",
			label: __("Compañía"),
			fieldtype: "Link",
			options: "Company", 
			default: frappe.defaults.get_default('company')
		},
		{
            fieldname: "quarter",
            label: __("Trimestre"),
            fieldtype: "Select",
            options: ["" ,"1T", "2T", "3T", "4T"],
        },
        {
			fieldname: "fiscal_year",
			label: __("Año Fiscal"),
			fieldtype: "Link",
			options: "Fiscal Year", 
			default: frappe.defaults.get_default('fiscal_year')
		},
        {
            fieldname: "from_date",
            label: __("Fecha de Inicio"),
            fieldtype: "Date",
        },
        {
            fieldname: "to_date",
            label: __("Fecha de Fin"),
            fieldtype: "Date",
        }
	]
};
