frappe.ui.form.on('Expense Claim', {
    refresh: function (frm) {
        frm.remove_custom_button("Payment", "Create");
	},

    company: function (frm) {
        erpnext.accounts.dimensions.update_dimension(frm, frm.doctype);
        var expenses = frm.doc.expenses || [];
        for (var i = 0; i < expenses.length; i++) {
            var expense = expenses[i];
            if (!expense.expense_type) {
                continue;
            }
            frappe.call({
                method: "hrms.hr.doctype.expense_claim.expense_claim.get_expense_claim_account_and_cost_center",
                args: {
                    expense_claim_type: expense.expense_type,
                    company: frm.doc.company,
                },
                callback: function (r) {
                    if (r.message) {
                        expense.cost_center = r.message.cost_center;
                    }
                },
            });
        }
    },
});

frappe.ui.form.on("Expense Claim Detail", {
	expense_type: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (!frm.doc.company) {
			d.expense_type = "";
			frappe.msgprint(__("Please set the Company"));
			this.frm.refresh_fields();
			return;
		}
		if (!d.expense_type) {
			return;
		}
		return frappe.call({
			method: "hrms.hr.doctype.expense_claim.expense_claim.get_expense_claim_account_and_cost_center",
			args: {
				expense_claim_type: d.expense_type,
				company: frm.doc.company,
			},
			callback: function (r) {
				if (r.message) {
					d.cost_center = r.message.cost_center;
				}
			},
		});
	},
});