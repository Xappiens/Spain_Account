frappe.ui.form.on("Amortization", {
    refresh: function(frm) {
        // Filtro dinámico para el campo de cuenta
        frm.set_query("account", function() {
            return {
                query: "spain_account.spain_accounting.doctype.amortization.amortization.get_filtered_accounts",
                filters: {
                    company: frm.doc.company || null // Enviar la empresa si está seleccionada
                }
            };
        });
        // Detectar cambios en el campo account
        frm.fields_dict.account.df.onchange = function() {
            if (!frm.doc.company && frm.doc.account) {
                frappe.db.get_value("Account", frm.doc.account, "company", function(value) {
                    if (value && value.company) {
                        frm.set_value("company", value.company);
                    }
                });
            }
        };
        // Botón personalizado para calcular la amortización
        frm.add_custom_button(__('Calcular Amortización'), function() {
            frm.call("calculate_amortization").then(() => {
                frappe.msgprint(__("Amortización calculada correctamente."));
                frm.refresh(); // Refresca el formulario para mostrar los cambios
            });
        });
    }
});