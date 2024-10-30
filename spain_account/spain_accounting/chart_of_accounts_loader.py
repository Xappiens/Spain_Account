# import json
# import os
# import frappe

# def get_chart(chart_template, existing_company=None):
#     chart = {}
#     if existing_company:
#         return get_account_tree_from_existing_company(existing_company)

#     # Agregar opción personalizada para España
#     elif chart_template == "Estandar Contabilidad España":
#         # Ruta del archivo JSON en la App 'spain_account'
#         path = os.path.join(
#             frappe.get_app_path("spain_account"), "charts", "es_spain_chart_of_accounts_numbers.json"
#         )
#         with open(path) as f:
#             chart = json.loads(f.read()).get("tree")
#         return chart

#     # Opciones estándar existentes
#     elif chart_template == "Standard":
#         from erpnext.accounts.doctype.account.chart_of_accounts.verified import (
#             standard_chart_of_accounts,
#         )
#         return standard_chart_of_accounts.get()

#     elif chart_template == "Standard with Numbers":
#         from erpnext.accounts.doctype.account.chart_of_accounts.verified import (
#             standard_chart_of_accounts_with_account_number,
#         )
#         return standard_chart_of_accounts_with_account_number.get()

#     else:
#         folders = ("verified",)
#         if frappe.local.flags.allow_unverified_charts:
#             folders = ("verified", "unverified")
#         for folder in folders:
#             path = os.path.join(os.path.dirname(__file__), folder)
#             for fname in os.listdir(path):
#                 fname = frappe.as_unicode(fname)
#                 if fname.endswith(".json"):
#                     with open(os.path.join(path, fname)) as f:
#                         chart = f.read()
#                         if chart and json.loads(chart).get("name") == chart_template:
#                             return json.loads(chart).get("tree")

# @frappe.whitelist()
# def get_charts_for_country(country, with_standard=False):
#     charts = []

#     def _get_chart_name(content):
#         if content:
#             content = json.loads(content)
#             if (
#                 content and content.get("disabled", "No") == "No"
#             ) or frappe.local.flags.allow_unverified_charts:
#                 charts.append(content["name"])

#     country_code = frappe.get_cached_value("Country", country, "code")
    
#     # Si el país es España, agregar el nuevo estándar personalizado
#     if country_code == "ES":
#         charts.append("Estandar España Contabilidad")

#     if country_code:
#         folders = ("verified",)
#         if frappe.local.flags.allow_unverified_charts:
#             folders = ("verified", "unverified")

#         for folder in folders:
#             path = os.path.join(os.path.dirname(__file__), folder)
#             if not os.path.exists(path):
#                 continue

#             for fname in os.listdir(path):
#                 fname = frappe.as_unicode(fname)
#                 if (fname.startswith(country_code) or fname.startswith(country)) and fname.endswith(".json"):
#                     with open(os.path.join(path, fname)) as f:
#                         _get_chart_name(f.read())

#     # Agregar las opciones estándar si no se encuentra solo un catálogo
#     if len(charts) != 1 or with_standard:
#         charts += ["Standard", "Standard with Numbers"]

#     return charts
