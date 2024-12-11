frappe.ui.form.on("Account", {
    parent_account(frm) {
        set_account_number(frm);
    },
    is_group(frm) {
        set_account_number(frm);
    }
});

// * FUNCTION TO SET ACCOUNT NUMBER BASED ON PARENT ACCOUNT AND IS_GROUP 
function set_account_number(frm) {
    if (!frm.doc.custom_no_cuenta_personalizado) {

        frappe.db.get_list("Account", {
            filters: {
                parent_account: frm.doc.parent_account
            },
            fields: ["account_number"],
            order_by: "account_number desc",
            limit: 1
        }).then(records => {
            let new_account_number;

            if (frm.doc.is_group) {

                if (records && records.length > 0) {

                    new_account_number = parseInt(records[0].account_number) + 1;
                } else {

                    const parent_account_number = parseInt(frm.doc.parent_account.split(" ")[0]);
                    new_account_number = parent_account_number * 10;
                }
            } else {
                if (records && records.length > 0) {

                    new_account_number = parseInt(records[0].account_number) + 1;
                } else {

                    const parent_account_number = frm.doc.parent_account.split(" ")[0];
                    new_account_number = parent_account_number.padEnd(8, "0");
                }
            }

            frm.set_value("account_number", new_account_number.toString());
        });
    }
}
