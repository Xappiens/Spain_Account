// Copyright (c) 2024, Xappiens and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hacienda Model", {
    refresh: function(frm) {
        // Add a custom button called "Generate Report"
        frm.add_custom_button(__('Generate Report'), function() {
            // Call the function to generate the report
            frappe.call({
                method: "your_app.your_module.doctype.hacienda_model.hacienda_model.generate_report",
                args: {
                    model_name: frm.doc.name,
                },
                callback: function(response) {
                    if (response.message) {
                        frappe.msgprint(__('Report generated successfully.'));
                        // Optionally, you can redirect to the report page
                        frappe.set_route("query-report", "Modelo Report");
                    }
                },
                error: function(err) {
                    frappe.msgprint(__('Failed to generate the report. Please check the console for errors.'));
                    console.error(err);
                },
            });
        })
    },
});
