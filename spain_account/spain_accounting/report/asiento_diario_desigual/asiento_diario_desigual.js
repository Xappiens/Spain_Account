// Copyright (c) 2025, Xappiens and contributors
// For license information, please see license.txt

frappe.query_reports["Asiento Diario Desigual"] = {
    "filters": [
        {
            fieldname: "journal_entry",
            label: __("ID"),
            fieldtype: "Link",
			options:"Journal Entry",
            default: "",
            placeholder: __("Buscar por ID")
        },
        {
            fieldname: "title",
            label: __("Título"),
            fieldtype: "Data",
            default: "",
            placeholder: __("Buscar por Título")
        },
        {
            fieldname: "voucher_type",
            label: __("Tipo de Asiento"),
            fieldtype: "Select",
            options: [
                { "label": "Journal Entry", "value": "Journal Entry" },
                { "label": "Inter Company Journal Entry", "value": "Inter Company Journal Entry" },
                { "label": "Bank Entry", "value": "Bank Entry" },
                { "label": "Cash Entry", "value": "Cash Entry" },
                { "label": "Credit Card Entry", "value": "Credit Card Entry" },
                { "label": "Debit Note", "value": "Debit Note" },
                { "label": "Credit Note", "value": "Credit Note" },
                { "label": "Contra Entry", "value": "Contra Entry" },
                { "label": "Excise Entry", "value": "Excise Entry" },
                { "label": "Write Off Entry", "value": "Write Off Entry" },
                { "label": "Opening Entry", "value": "Opening Entry" },
                { "label": "Depreciation Entry", "value": "Depreciation Entry" },
                { "label": "Exchange Rate Revaluation", "value": "Exchange Rate Revaluation" },
                { "label": "Exchange Gain Or Loss", "value": "Exchange Gain Or Loss" },
                { "label": "Deferred Revenue", "value": "Deferred Revenue" },
                { "label": "Deferred Expense", "value": "Deferred Expense" }
            ],
            default: "",
            placeholder: __("Seleccionar Tipo de Asiento")
        },
        {
            fieldname: "company",
            label: __("Compañía"),
            fieldtype: "Link",
            options: "Company",
            default: "",
            placeholder: __("Seleccionar Compañía")
        },
        {
            fieldname: "from_date",
            label: __("Desde la Fecha"),
            fieldtype: "Date",
            default: "",
            placeholder: __("Seleccionar Desde la Fecha")
        },
        {
            fieldname: "to_date",
            label: __("Hasta la Fecha"),
            fieldtype: "Date",
            default: "",
            placeholder: __("Seleccionar Hasta la Fecha")
        }
    ],
	
	
};
