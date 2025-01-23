frappe.ui.form.on("Amortization", {
    refresh: function(frm) {
        // Filtro dinámico para el campo de cuenta
        frm.set_query("asset_account", function() {
            return {
                query: "spain_account.spain_accounting.doctype.amortization.amortization.get_filtered_accounts",
                filters: {
                    company: frm.doc.company || null
                }
            };
        });

        frm.set_query("amortization_expense_account", function() {
            return {
                filters: {
                    account_number: ["like", "68%"],
                    company: frm.doc.company || null
                }
            };
        });

        frm.set_query("accumulated_amortization_account", function() {
            return {
                filters: {
                    account_number: ["like", "28%"],
                    company: frm.doc.company || null
                }
            };
        });

        frm.set_query("invoice", function() {
            return {
                filters: {
                    company: frm.doc.company || null
                }
            };
        });

        // Lógica para obtener cuentas derivadas desde el backend
        function fetch_derived_accounts(asset_account, company) {
            if (!asset_account || !company) return;

            frappe.call({
                method: "spain_account.spain_accounting.doctype.amortization.amortization.get_derived_accounts",
                args: {
                    asset_account: asset_account,
                    company: company
                },
                callback: function(response) {
                    if (response.message) {
                        const accounts = response.message;
                        if (accounts["68"]) {
                            frm.set_value("amortization_expense_account", accounts["68"]);
                        }
                        if (accounts["28"]) {
                            frm.set_value("accumulated_amortization_account", accounts["28"]);
                        }
                    }
                }
            });
        }

        // Detectar cambios en el campo asset_account
        frm.fields_dict.asset_account.df.onchange = function() {
            let asset_account = frm.doc.asset_account;
            fetch_derived_accounts(asset_account, frm.doc.company);

            if (!frm.doc.company && asset_account) {
                frappe.db.get_value("Account", asset_account, "company", function(value) {
                    if (value && value.company) {
                        frm.set_value("company", value.company);
                        fetch_derived_accounts(asset_account, value.company);
                    }
                });
            }
        };

        // Configurar onchange para el campo invoice
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
        };

        frm.fields_dict.price.df.onchange = function() {
            if ((!frm.doc.amortizable_value || frm.doc.amortizable_value == 0) && frm.doc.price) {
                frm.set_value("amortizable_value", frm.doc.price);
            }
        };


        // Agregar "Calcular Amortización" al submenú "Herramientas"
        frm.add_custom_button(__('Calcular Amortización'), function() {
            frm.call("calculate_amortization").then(() => {
                frappe.msgprint(__("Amortización calculada correctamente."));
                frm.refresh();
            });
        }, "Herramientas");

        // Agregar "Crear Asiento" al submenú "Herramientas"
        // Botón "Crear Asiento"
if (!frm.is_new() && frm.doc.asset_account && frm.doc.amortization_expense_account && frm.doc.accumulated_amortization_account) {
    frm.add_custom_button(__('Crear Asiento'), function() {
        frappe.prompt([
            {
                fieldname: "year",
                label: __("Año"),
                fieldtype: "Link",
                options: "Fiscal Year",
                reqd: 1
            }
        ],
        function(values) {
            frappe.call({
                method: "spain_account.spain_accounting.doctype.amortization.amortization.process_gl_create",
                args: {
                    name: frm.doc.name,
                    year: values.year
                },
                callback: function(r) {
                    if (r.message) {
                        if (r.message.success) {
                            frappe.msgprint({
                                title: __('Éxito'),
                                message: __(r.message.message),
                                indicator: 'green'
                            });
                        } else {
                            frappe.msgprint({
                                title: __('Error'),
                                message: __(r.message.message),
                                indicator: 'red'
                            });
                        }
                    }
                    frm.refresh();
                }
            });
        },
        __("Crear Asiento"),
        __("Crear")
        );
    }, "Herramientas");
}

            // Añadir el submenú "Ver"
        if (!frm.is_new()){
        frm.add_custom_button(__('Libro de Contabilidad'), function() {
            // Redirigir al General Ledger con parámetros pre-rellenados
            frappe.set_route("query-report", "General Ledger", {
                voucher_no: frm.doc.name,    // Pre-rellenar el Voucher No con el nombre del documento
                company: frm.doc.company    // Pre-rellenar la compañía con la del documento
                // No rellenamos las fechas, ya que queremos que el usuario las defina
            });
        }, "Ver");
    }
}
});
