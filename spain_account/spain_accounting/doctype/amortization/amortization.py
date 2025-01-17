# Copyright (c) 2025, Xappiens and contributors
# For license information, please see license.txt
from datetime import datetime
import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime

class Amortization(Document):
    
    def on_update(self):
        self.calculate_amortization()
    
    @frappe.whitelist()
    def calculate_amortization(self):
        if not self.amortizable_value or not self.percentage or not self.start_date:
            frappe.throw("Debe ingresar los campos obligatorios")
        
        self.amortization_details = []  # Limpiar detalles previos
        
        # Calcular el saldo total a amortizar
        total_amortizable = self.amortizable_value  
        accumulated_amount = 0  # Monto acumulado

        # Convertir fechas a objetos datetime
        start_date = get_datetime(self.start_date)
        end_date = get_datetime(self.end_date) if self.end_date else None

        current_year = start_date.year
        remaining_amount = total_amortizable  # Saldo pendiente
        annual_max_amortization = total_amortizable * (self.percentage / 100)  # Monto máximo por año

        while remaining_amount > 0:
            # Determinar el rango de fechas del año actual
            year_start = datetime(current_year, 1, 1)
            year_end = datetime(current_year, 12, 31)
            
            # Ajustar si la amortización comienza a mitad de año
            if current_year == start_date.year:
                year_start = start_date
            
            # Ajustar si hay una fecha de finalización
            if end_date and end_date.year == current_year:
                year_end = end_date
            
            # Calcular días activos en el año
            days_in_year = (datetime(current_year, 12, 31) - datetime(current_year, 1, 1)).days + 1
            days_active = (year_end - year_start).days + 1
            
            # Calcular amortización para este año en base a los días activos
            annual_amount = (annual_max_amortization / days_in_year) * days_active
            annual_amount = min(annual_amount, remaining_amount)  # No exceder el saldo pendiente
            
            # Calcular porcentaje amortizado en este año
            annual_percentage = (annual_amount / total_amortizable) * 100
            
            # Registrar la amortización del año actual
            self.append("amortization_details", {
                "year": current_year,
                "annual_amount": round(annual_amount, 2),
                "accumulated_amount": round(accumulated_amount + annual_amount, 2),
                "percentage": round(annual_percentage, 2)  # Nuevo campo agregado
            })
            
            # Actualizar valores
            accumulated_amount += annual_amount
            remaining_amount -= annual_amount
            
            # Detener si alcanzamos la fecha de finalización
            if end_date and current_year >= end_date.year:
                break
            
            # Pasar al siguiente año
            current_year += 1

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