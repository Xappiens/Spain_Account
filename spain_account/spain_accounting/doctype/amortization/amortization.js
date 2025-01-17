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
        frm.set_query("invoice", function() {
            return {
                filters: {
                    company: frm.doc.company || null // Enviar la empresa si está seleccionada
                }
            };
        });
        frm.fields_dict.invoice.df.onchange = function() {
            if (!frm.doc.company && frm.doc.invoice) {
                frappe.db.get_value("Purchase Invoice", frm.doc.invoice, "company", function(value) {
                    if (value && value.company) {
                        frm.set_value("company", value.company);
                    }
                });
            }
            if (!frm.doc.purchase_date && frm.doc.invoice) {
                frappe.db.get_value("Purchase Invoice", frm.doc.invoice, "posting_date", function(value) {
                    if (value && value.posting_date) {
                        frm.set_value("purchase_date", value.posting_date);
                    }
                });
            }
            if (!frm.doc.price && frm.doc.invoice) {
                frappe.db.get_value("Purchase Invoice", frm.doc.invoice, "net_total", function(value) {
                    if (value && value.net_total) {
                        frm.set_value("price", value.net_total);
                    }
                });
            }
        }

        frm.fields_dict.price.df.onchange = function() {
            if (!frm.doc.amortizable_value && frm.doc.price) {
                frm.set_value("amortizable_value", frm.doc.price);
            }
        }
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