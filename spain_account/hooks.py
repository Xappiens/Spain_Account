app_name = "spain_account"
app_title = "Spain Accounting"
app_publisher = "Xappiens"
app_description = "This app is designed to seamlessly integrate with ERPNext, enabling businesses to effortlessly establish and manage the Spanish chart of accounts. Comply with local accounting standards (Plan General de Contabilidad) and streamline your financial processes with this essential tool. Simplify the setup of your financial structure, ensuring accurate and compliant reporting according to Spanish regulations. Perfect for businesses operating in Spain, this extension brings precision and ease to your ERPNext system, making accounting management more efficient and reliable."
app_email = "xappiens@xappiens.com"
app_license = "mit"

# Apps
# ------------------

# hooks.py en tu app 'spain_account'

# Sobrescribir los métodos get_chart y get_charts_for_country en ERPNext
# override_whitelisted_methods = {
#     "erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts.get_chart": "spain_account.spain_accounting.chart_of_accounts_loader.get_chart",
#     "erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts.get_charts_for_country": "spain_account.spain_accounting.chart_of_accounts_loader.get_charts_for_country"
# }


# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "spain_account",
# 		"logo": "/assets/spain_account/logo.png",
# 		"title": "Spain Accounting",
# 		"route": "/spain_account",
# 		"has_permission": "spain_account.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/spain_account/css/spain_account.css"
# app_include_js = "/assets/spain_account/js/spain_account.js"

# include js, css files in header of web template
# web_include_css = "/assets/spain_account/css/spain_account.css"
# web_include_js = "/assets/spain_account/js/spain_account.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "spain_account/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

setup_wizard_requires = "assets/spain_account/js/setup_wizard.js"
# setup_wizard_stages = "spain_account.spain_accounting.py.setup_wizard.get_setup_stages"
setup_wizard_complete = "spain_account.spain_accounting.py.setup_wizard.setup_demo"

# include js in doctype views

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

doctype_js = {
    "Account": "public/js/account.js",
    "Expense Claim": "public/js/expense_claim.js",
}
# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "spain_account/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "spain_account.utils.jinja_methods",
# 	"filters": "spain_account.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "spain_account.install.before_install"
# after_install = "spain_account.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "spain_account.uninstall.before_uninstall"
# after_uninstall = "spain_account.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "spain_account.utils.before_app_install"
# after_app_install = "spain_account.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "spain_account.utils.before_app_uninstall"
# after_app_uninstall = "spain_account.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "spain_account.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

override_doctype_class = {
    "Company": "spain_account.spain_accounting.py.company.CompanyOverride",
    "Expense Claim": "spain_account.spain_accounting.py.expense_claim.ExpenseClaimOverride"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }


doc_events = {
    # "Purchase Invoice": {
    #     "validate": "spain_account.spain_accounting.py.purchase_invoice.modify_tds_tax_row"
    # },
    "Company": {
        "before_insert": "spain_account.spain_accounting.py.company.create_account_enqueue",
        
    },
    "Employee": {
        "after_insert": "spain_account.spain_accounting.py.employee.create_employee_account"
    },
    
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"spain_account.tasks.all"
# 	],
# 	"daily": [
# 		"spain_account.tasks.daily"
# 	],
# 	"hourly": [
# 		"spain_account.tasks.hourly"
# 	],
# 	"weekly": [
# 		"spain_account.tasks.weekly"
# 	],
# 	"monthly": [
# 		"spain_account.tasks.monthly"
# 	],
# }

scheduler_events = {
    "daily": [
        "spain_account.spain_accounting.doctype.amortization.amortization.process_amortizations_in_background"
    ]
}
# Testing
# -------

# before_tests = "spain_account.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "spain_account.event.get_events"
# }
override_whitelisted_methods = {
    "hrms.hr.doctype.expense_claim.expense_claim.get_expense_claim_account_and_cost_center": "spain_account.spain_accounting.py.expense_claim.get_expense_claim_account_and_cost_center"
}


#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "spain_account.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["spain_account.utils.before_request"]
# after_request = ["spain_account.utils.after_request"]

# Job Events
# ----------
# before_job = ["spain_account.utils.before_job"]
# after_job = ["spain_account.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"spain_account.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


fixtures = [
    {
        "doctype": "Hacienda Model",
        "filters": [
            [
                "name",
                "in",
                ["Modelo 111", "Modelo 303", "Modelo 347" , "Modleo 390", "modleo 190", "Modleo 115", "Modelo 180", "Modelo 123", "Modelo 349"],
            ]
        ],
    },
    {
        "doctype": "Tipo de Amortizacion",
    }
]
