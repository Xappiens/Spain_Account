import frappe


def after_setup(args=""):
    frappe.enqueue("spain_account.spain_accounting.py.charts_of_account_level.create_accounts")
