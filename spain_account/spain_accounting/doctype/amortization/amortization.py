# Copyright (c) 2025, Xappiens and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_datetime, getdate, add_days, add_months, add_years
class Amortization(Document):
	
	def on_update(self):
		self.calculate_amortization()
	@frappe.whitelist()
	def calculate_amortization(self):
		if not self.price or not self.percentage or not self.purchase_date:
			frappe.throw("Debe ingresar los campos obligatorios")
		self.amortization_details = []
		# Calculo de la amortizacion
		annual_amount = (self.price * self.percentage) / 100
		accumulated_amount = self.initial_amortization or 0
		year = get_datetime(self.purchase_date).year
		if self.initial_amortization:
			self.append("amortization_details", {
				"year": year,
				"annual_amount": self.initial_amortization,
				"accumulated_amount": accumulated_amount
			})
			year += 1
		# Generar las filas de amortizacion
		while accumulated_amount < self.price:
			remaining_amount = self.price - accumulated_amount
			amortized_on_year = min(annual_amount, remaining_amount)  # Ajustar el último año si es menor que el monto anual
			self.append("amortization_details", {
				"year": year,
				"annual_amount": amortized_on_year,  # Monto amortizado este año
				"accumulated_amount": accumulated_amount + amortized_on_year  # Monto acumulado actualizado
			})
			accumulated_amount += amortized_on_year
			year += 1
@frappe.whitelist()
def get_filtered_accounts(doctype, txt, searchfield, start, page_len, filters):
    """
    Devuelve las cuentas que:
    - No sean grupo (is_group = 0)
    - Su account_number comience con '20' o '21'
    - Opcionalmente filtradas por empresa
    """
    conditions = ["is_group = 0"]
    values = []
    # Filtro por número de cuenta
    conditions.append("(account_number LIKE %s OR account_number LIKE %s)")
    values.extend(["20%", "21%"])
    # Si hay empresa, añadir al filtro
    if filters.get("company"):
        conditions.append("company = %s")
        values.append(filters["company"])
    query = f"""
        SELECT name, account_name
        FROM `tabAccount`
        WHERE {' AND '.join(conditions)}
        ORDER BY {searchfield} LIMIT %s, %s
    """
    values.extend([start, page_len])  # Agrega los límites para paginación
    return frappe.db.sql(query, values)