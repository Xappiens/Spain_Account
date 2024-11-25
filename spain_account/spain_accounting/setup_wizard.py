

# # Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# # License: GNU General Public License v3. See license.txt

# import frappe
# from frappe import _
# from erpnext.setup.demo import setup_demo_data
# from erpnext.setup.setup_wizard.operations import install_fixtures as fixtures
# from frappe.utils import get_first_day, get_last_day


# def get_setup_stages(args=None):
#     if frappe.db.sql("select name from tabCompany"):
#         stages = [
#             {
#                 "status": _("Wrapping up"),
#                 "fail_msg": _("Failed to login"),
#                 "tasks": [{"fn": fin, "args": args, "fail_msg": _("Failed to login")}],
#             }
#         ]
#     else:
#         stages = [
#             {
#                 "status": _("Installing presets"),
#                 "fail_msg": _("Failed to install presets"),
#                 "tasks": [{"fn": stage_fixtures, "args": args, "fail_msg": _("Failed to install presets")}],
#             },
#             {
#                 "status": _("Setting up company"),
#                 "fail_msg": _("Failed to setup company"),
#                 "tasks": [{"fn": setup_company, "args": args, "fail_msg": _("Failed to setup company")}],
#             },
#             {
#                 "status": _("Setting defaults"),
#                 "fail_msg": "Failed to set defaults",
#                 "tasks": [
#                     {"fn": setup_defaults, "args": args, "fail_msg": _("Failed to setup defaults")},
#                     {
#                         "fn": create_accounts,
#                         "args": args,
#                         "fail_msg": _("Failed to setup periods")
#                     }
#                 ],
#             },
#             {
#                 "status": _("Wrapping up"),
#                 "fail_msg": _("Failed to login"),
#                 "tasks": [{"fn": fin, "args": args, "fail_msg": _("Failed to login")}],
#             },
#         ]

#     return stages

# def stage_fixtures(args):
#     fixtures.install(args.get("country"))

# def setup_company(args):
#     fixtures.install_company(args)

# @frappe.whitelist()
# def create_accounts(args):
#     company = args.get("spain_accounts")
#     accounting_period = args.get("accounting_period")
#     calendar_start_date = frappe.utils.getdate(f"{frappe.utils.now_datetime().year}-01-01")
#     calendar_end_date = frappe.utils.getdate(f"{frappe.utils.now_datetime().year}-12-31")

#     if accounting_period == "Monthly":
#         current_start = calendar_start_date
#         for i in range(12):
#             current_end = get_last_day(current_start)
            
#             month_name = current_start.strftime('%B')
#             create_accounting_period(company, f"Accounting Period - {month_name}", current_start, current_end)
#             current_start = frappe.utils.add_months(current_start, 1)

#     elif accounting_period == "Yearly":
#         create_accounting_period(company, "Accounting Period - Yearly", calendar_start_date, calendar_end_date)

#     return True

# def create_accounting_period(company, period_name, start_date, end_date):
#     doc = frappe.get_doc({
#         "doctype": "Accounting Period",
#         "company": company,
#         "start_date": start_date,
#         "end_date": end_date,
#         "period_name": period_name
#     })

#     closed_documents = get_doctypes_for_closing()

#     for doctype in closed_documents:
#         child_row = doc.append("closed_documents", {})
#         child_row.document_type = doctype["document_type"]
#         child_row.closed = doctype["closed"]

#     doc.insert()
#     frappe.db.commit()

# @frappe.whitelist()
# def get_doctypes_for_closing():
# 	docs_for_closing = []
# 	doctypes = frappe.get_hooks("period_closing_doctypes")
# 	closed_doctypes = [{"document_type": doctype, "closed": 1} for doctype in doctypes]
# 	for closed_doctype in closed_doctypes:
# 		docs_for_closing.append(closed_doctype)
# 	return docs_for_closing

# def setup_defaults(args):
#     fixtures.install_defaults(frappe._dict(args))

# def fin(args):
#     frappe.local.message_log = []
#     login_as_first_user(args)

# def setup_demo(args):
#     if args.get("setup_demo"):
#         frappe.enqueue(setup_demo_data, enqueue_after_commit=True, at_front=True)

# def login_as_first_user(args):
#     if args.get("email") and hasattr(frappe.local, "login_manager"):
#         frappe.local.login_manager.login_as(args.get("email"))

# # Only for programmatic use
# def setup_complete(args=None):
#     stage_fixtures(args)
#     setup_company(args)
#     setup_defaults(args)
#     fin(args)
