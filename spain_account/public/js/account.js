frappe.ui.form.on("Account", {
    parent_account(frm) {
        set_account_number(frm);
    },
    is_group(frm) {
        set_account_number(frm);
    },
});

// * FUNCTION TO SET ACCOUNT NUMBER BASED ON PARENT ACCOUNT AND IS_GROUP 
function set_account_number(frm) {
    if (!frm.doc.custom_no_cuenta_personalizado) {
        
        // Use async/await to wait for the old parent account value
        frappe.db.get_value("Account", frm.doc.name, "parent_account").then(result => {
            const old_parent_account = result ? result.message.parent_account : null;

            frappe.db.get_list("Account", {
                filters: {
                    parent_account: frm.doc.parent_account
                },
                fields: ["account_number"],
                order_by: "account_number desc",
                limit: 1
            }).then(records => {

                // Check if parent account has changed
                if (frm.doc.parent_account !== old_parent_account) {
                    let new_account_number;

                    if (frm.doc.is_group) {
                        // Logic for generating account number for group
                        if (records && records.length > 0) {
                            new_account_number = parseInt(records[0].account_number) + 1;
                        } else {
                            const parent_account_number = parseInt(frm.doc.parent_account.split(" ")[0]);
                            new_account_number = parent_account_number * 10;
                        }
                    } else {
                        // Logic for generating account number for individual
                        if (records && records.length > 0) {
                            new_account_number = parseInt(records[0].account_number) + 1;
                        } else {
                            const parent_account_number = frm.doc.parent_account.split(" ")[0];
                            new_account_number = parent_account_number.padEnd(8, "0");
                        }
                    }

                    frm.set_value("account_number", new_account_number.toString());
                }
            });
        });
    }
}
