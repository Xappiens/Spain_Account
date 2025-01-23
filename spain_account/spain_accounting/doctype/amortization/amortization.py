# Copyright (c) 2025, Xappiens and contributors
# For license information, please see license.txt

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import frappe
from frappe.model.document import Document
from frappe.utils import today, flt, get_datetime
from frappe.utils.background_jobs import enqueue
from erpnext.accounts.general_ledger import make_gl_entries
from frappe import _dict


# Configuración del logger
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
LOGS_PATH = os.path.join(BASE_PATH, 'logs')

if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)

LOG_CONFIG = {
    'filename': os.path.join(LOGS_PATH, 'amortization.log'),
    'max_bytes': 50 * 1024 * 1024,  # 50 MB
    'backup_count': 3,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}


def setup_logger() -> logging.Logger:
    """Configura y devuelve el logger para este módulo."""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(
            LOG_CONFIG['filename'],
            maxBytes=LOG_CONFIG['max_bytes'],
            backupCount=LOG_CONFIG['backup_count']
        )
        formatter = logging.Formatter(LOG_CONFIG['format'])
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = setup_logger()


class Amortization(Document):
    
    def on_update(self):
        if not self.flags.ignore_calculate_amortization:
            self.flags.ignore_calculate_amortization = True
            self.calculate_amortization()
            frappe.db.commit()
    
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
                "remaining_amount": round(remaining_amount - annual_amount, 2),
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
        self.flags.dirty = True
        if not self.flags.from_update:
            self.save(ignore_permissions=True)


    def process_gl_create(self, year=None):
        self.reload()
        year_to_process = year if year else get_datetime(today()).year

        logger.info(f"Processing GL Entries for {self.name}, year {year_to_process}")

        if existing_gl_entries := frappe.db.exists("GL Entry", {
            "voucher_type": "Amortization", 
            "voucher_no": self.name,
            "fiscal_year": year_to_process,
        }):
            logger.info(f"GL Entries already exist for {self.name}, year {year_to_process}")
            return {"success": False, "message": f"Ya existen asientos para el año {year_to_process}"}

        if not (details := next((d for d in self.amortization_details if int(d.year) == int(year_to_process)), None)):
            logger.error(f"No amortization details found for {self.name}, year {year_to_process}")
            return {"success": False, "message": f"No hay detalles de amortización para el año {year_to_process}"}

        try:
            self.create_gl_entries(details)
            logger.info(f"GL Entry created successfully for {self.name}, year {year_to_process}")
            return {"success": True, "message": f"Asiento creado correctamente para el año {year_to_process}"}
        except Exception as e:
            logger.error(f"Error creating GL Entry for {self.name}, year {year_to_process}: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def create_gl_entries(self, details):
        """
        Crea entradas contables (GL Entries) para la amortización actual usando make_gl_entries.
        """
        company = frappe.get_doc("Company", self.company)
        cost_center = company.cost_center

        # Validar que se haya configurado un centro de costos
        if not cost_center:
            frappe.throw(f"Debe configurar un centro de costos en la compañía {self.company}")

        # Validar que las cuentas necesarias estén configuradas
        if not self.amortization_expense_account:
            frappe.throw("La cuenta de gastos de amortización no está configurada.")
        if not self.accumulated_amortization_account:
            frappe.throw("La cuenta de amortización acumulada no está configurada.")

        annual_amount = flt(details.annual_amount)
        year_end_date = f"{details.year}-12-31"

        # Validar que el monto anual sea mayor a cero
        if annual_amount <= 0:
            frappe.throw(f"El monto anual para el año {details.year} debe ser mayor a cero.")

        # Define las entradas para Débito y Crédito como frappe._dict
        gl_entries = [
            _dict({
                "posting_date": year_end_date,
                "transaction_date": year_end_date,
                "account": self.amortization_expense_account,
                "fiscal_year": details.year,
                "debit": annual_amount,
                "debit_in_account_currency": annual_amount,
                "credit": 0,
                "credit_in_account_currency": 0,
                "currency": company.default_currency or "EUR",
                "cost_center": cost_center,
                "voucher_type": "Amortization",
                "voucher_subtype": "Amortization Details",
                "voucher_no": self.name,
                "company": company.name,
                "remarks": f"Gasto de amortización para {self.name}, año {details.year}",
                "against": self.accumulated_amortization_account,  # Cuenta contrapartida
            }),
            _dict({
                "posting_date": year_end_date,
                "transaction_date": year_end_date,
                "account": self.accumulated_amortization_account,
                "fiscal_year": details.year,
                "debit": 0,
                "debit_in_account_currency": 0,
                "credit": annual_amount,
                "credit_in_account_currency": annual_amount,
                "currency": company.default_currency or "EUR",
                "cost_center": cost_center,
                "voucher_type": "Amortization",
                "voucher_subtype": "Amortization Details",
                "voucher_no": self.name,
                "company": company.name,
                "remarks": f"Amortización acumulada para {self.name}, año {details.year}",
                "against": self.amortization_expense_account,  # Cuenta contrapartida
            }),
        ]

        # Intentar crear las entradas en el libro mayor
        try:
            make_gl_entries(gl_entries, cancel=0, update_outstanding="No")
            logger.info(f"GL Entries created successfully for {self.name}, year: {details.year}")
            frappe.db.commit()  # Forzar la escritura en la base de datos
        except Exception as e:
            logger.error(f"Error creating GL Entries: {str(e)}")
            frappe.throw(f"Error al crear las GL Entries: {str(e)}")


@frappe.whitelist()
def get_filtered_accounts(doctype, txt, searchfield, start, page_len, filters):
    conditions = ["is_group = 0"]
    values = []
    
    # Filtro por número de cuenta (20% o 21%)
    conditions.append("(account_number LIKE %s OR account_number LIKE %s)")
    values.extend(["20%", "21%"])
    
    # Filtro por texto de búsqueda
    if txt:
        conditions.append("(name LIKE %s OR account_number LIKE %s OR account_name LIKE %s)")
        values.extend([f"%{txt}%", f"%{txt}%", f"%{txt}%"])
    
    if filters.get("company"):
        conditions.append("company = %s")
        values.append(filters["company"])
    
    query = f"""
        SELECT name, account_name
        FROM `tabAccount`
        WHERE {' AND '.join(conditions)}
        ORDER BY {searchfield} LIMIT %s, %s
    """
    values.extend([start, page_len])
    return frappe.db.sql(query, values)

@frappe.whitelist()
def get_derived_accounts(asset_account, company):
    """
    Deriva las cuentas `68` y `28` a partir del número de cuenta asociado a `asset_account`
    y busca las cuentas derivadas en `tabAccount`.
    """
    if not asset_account or not company:
        frappe.throw("Debe proporcionar una cuenta de activo y una empresa.")

    # Obtener el número de cuenta asociado al asset_account
    account_details = frappe.get_value(
        "Account",
        {"name": asset_account, "company": company},
        "account_number"
    )

    if not account_details:
        frappe.throw("La cuenta seleccionada no existe o no pertenece a la empresa especificada.")

    account_number = account_details

    # Función para derivar el número de cuenta
    def derive_account_number(original_account, new_prefix):
        """
        Deriva el número de cuenta reemplazando el primer dígito por el prefijo,
        compactando la parte intermedia y rellenando ceros para igualar la longitud.
        """
        zero_index = original_account.find("0", 1)  # Buscar el primer `0` después del primer dígito
        if zero_index == -1:
            frappe.throw("El número de cuenta no tiene un formato válido para la derivación.")

        part_before_zero = original_account[:zero_index]  # Parte antes del primer `0`
        termination = original_account[zero_index:].lstrip("0")  # Terminación sin ceros iniciales

        # Compactar la parte intermedia eliminando ceros
        compressed_middle = part_before_zero[1:].replace("0", "")

        # Calcular la longitud restante para rellenar con ceros
        needed_zeros = len(original_account) - len(new_prefix + compressed_middle + termination)

        # Construir el número derivado
        derived_number = f"{new_prefix}{compressed_middle}{'0' * needed_zeros}{termination}"
        return derived_number

    # Derivar los números de cuenta
    derived_68 = derive_account_number(account_number, "68")
    derived_28 = derive_account_number(account_number, "28")

    # Registrar en logs para depuración
    frappe.log_error(f"Derived 68: {derived_68}, Derived 28: {derived_28}")

    # Buscar las cuentas derivadas en tabAccount
    accounts = frappe.get_all(
        "Account",
        filters={
            "account_number": ["in", [derived_68, derived_28]],
            "company": company,
            "is_group": 0
        },
        fields=["name", "account_number"]
    )

    # Organizar los resultados
    result = {"68": None, "28": None}
    for account in accounts:
        if account["account_number"] == derived_68:
            result["68"] = account["name"]  # Devuelve el name de la cuenta derivada
        elif account["account_number"] == derived_28:
            result["28"] = account["name"]  # Devuelve el name de la cuenta derivada

    return result



@frappe.whitelist()
def process_amortizations():
   current_date = today()
   current_datetime = get_datetime(current_date)
   
   if not (current_datetime.month == 12 and current_datetime.day == 31):
       return

   current_year = current_datetime.year
   logger.info(f"Processing amortizations for year: {current_year}")

   amortization_details = frappe.db.sql(
       """
       SELECT parent, year
       FROM `tabAmortization Details`
       WHERE year = %s
       """,
       (current_year,),
       as_dict=True,
   )

   if not amortization_details:
       logger.info(f"No amortization details found for year {current_year}.")
       return

   for detail in amortization_details:
       try:
           doc = frappe.get_doc("Amortization", detail["parent"])
           doc.process_gl_create(year=current_year)
       except Exception as e:
           logger.error(f"Error processing amortization {detail['parent']}: {e}")
           continue

@frappe.whitelist()
def process_amortizations_in_background():
   enqueue(
       method="spain_account.spain_accounting.doctype.amortization.amortization.process_amortizations",
       queue="long",
       timeout=600
   )

@frappe.whitelist()
def process_gl_create(name, year=None):
   doc = frappe.get_doc("Amortization", name)
   return doc.process_gl_create(year=year)