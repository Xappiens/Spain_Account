# Copyright (c) 2024, Xappiens and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, fmt_money, get_url
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
import json


@frappe.whitelist()
def send_modelo_347_emails(company, fiscal_year, party_type=None, test_email=None):
    """
    Envía el certificado del Modelo 347 a cada cliente/proveedor.
    
    Args:
        company: Nombre de la empresa
        fiscal_year: Año fiscal
        party_type: 'Customer', 'Supplier' o None para ambos
        test_email: Si se proporciona, envía todos los correos a esta dirección (modo prueba)
    
    Returns:
        dict con estadísticas de envío
    """
    from spain_account.spain_accounting.report.modelo_347.modelo_347 import execute
    
    filters = {
        "company": company,
        "fiscal_year": fiscal_year,
        "party_type": party_type or ""
    }
    
    columns, data = execute(filters)
    
    if not data:
        return {
            "success": False,
            "message": _("No hay datos para enviar"),
            "sent": 0,
            "failed": 0,
            "skipped": 0
        }
    
    # Obtener datos de la empresa
    company_doc = frappe.get_doc("Company", company)
    company_logo = company_doc.company_logo
    company_address = get_company_address(company)
    
    # Obtener año del fiscal year
    fiscal_year_doc = frappe.get_doc("Fiscal Year", fiscal_year)
    year = getdate(fiscal_year_doc.year_start_date).year
    
    sent = 0
    failed = 0
    skipped = 0
    errors = []
    
    for row in data:
        party_name = row.get("party_name", "")
        party_type_code = row.get("party_type_code", "")
        email = row.get("email", "")
        
        # Usar email de prueba si está en modo test
        recipient_email = test_email if test_email else email
        
        if not recipient_email:
            skipped += 1
            continue
        
        try:
            # Generar PDF
            pdf_content = generate_modelo_347_pdf(
                company=company,
                company_logo=company_logo,
                company_address=company_address,
                year=year,
                party_name=party_name,
                party_type=party_type_code,
                nif=row.get("nif", ""),
                provincia=row.get("provincia", ""),
                t1=row.get("t1", 0),
                t2=row.get("t2", 0),
                t3=row.get("t3", 0),
                t4=row.get("t4", 0),
                total=row.get("total", 0),
                clave=row.get("clave_operacion", "")
            )
            
            # Enviar email
            subject = _("Certificado Modelo 347 - Ejercicio {0} - {1}").format(year, company)
            
            message = get_email_template(
                company=company,
                year=year,
                party_name=party_name,
                party_type=party_type_code,
                total=row.get("total", 0)
            )
            
            filename = f"Modelo_347_{year}_{party_name.replace(' ', '_')[:30]}.pdf"
            
            frappe.sendmail(
                recipients=[recipient_email],
                subject=subject,
                message=message,
                attachments=[{
                    "fname": filename,
                    "fcontent": pdf_content
                }],
                now=True
            )
            
            sent += 1
            
            # Si es modo test, solo enviar uno
            if test_email:
                break
                
        except Exception as e:
            failed += 1
            errors.append({
                "party": party_name,
                "email": recipient_email,
                "error": str(e)
            })
            frappe.log_error(
                message=f"Error enviando Modelo 347 a {party_name}: {str(e)}",
                title="Error Modelo 347 Email"
            )
    
    return {
        "success": True,
        "message": _("Proceso completado"),
        "sent": sent,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
        "test_mode": bool(test_email)
    }


@frappe.whitelist()
def preview_modelo_347_pdf(company, fiscal_year, party_data):
    """
    Genera un PDF de vista previa para un tercero específico.
    
    Args:
        company: Nombre de la empresa
        fiscal_year: Año fiscal
        party_data: JSON con los datos del tercero
    
    Returns:
        PDF en base64
    """
    import base64
    
    if isinstance(party_data, str):
        party_data = json.loads(party_data)
    
    # Obtener datos de la empresa
    company_doc = frappe.get_doc("Company", company)
    company_logo = company_doc.company_logo
    company_address = get_company_address(company)
    
    # Obtener año del fiscal year
    fiscal_year_doc = frappe.get_doc("Fiscal Year", fiscal_year)
    year = getdate(fiscal_year_doc.year_start_date).year
    
    pdf_content = generate_modelo_347_pdf(
        company=company,
        company_logo=company_logo,
        company_address=company_address,
        year=year,
        party_name=party_data.get("party_name", ""),
        party_type=party_data.get("party_type_code", ""),
        nif=party_data.get("nif", ""),
        provincia=party_data.get("provincia", ""),
        t1=party_data.get("t1", 0),
        t2=party_data.get("t2", 0),
        t3=party_data.get("t3", 0),
        t4=party_data.get("t4", 0),
        total=party_data.get("total", 0),
        clave=party_data.get("clave_operacion", "")
    )
    
    return base64.b64encode(pdf_content).decode("utf-8")


def generate_modelo_347_pdf(company, company_logo, company_address, year, 
                            party_name, party_type, nif, provincia,
                            t1, t2, t3, t4, total, clave):
    """Genera el PDF del certificado del Modelo 347."""
    
    # Determinar tipo de operación
    if party_type == "Supplier":
        tipo_tercero = "PROVEEDOR"
        tipo_operacion = "Adquisiciones de bienes y servicios"
        clave_desc = "A - Adquisiciones"
    else:
        tipo_tercero = "CLIENTE"
        tipo_operacion = "Entregas de bienes y prestaciones de servicios"
        clave_desc = "B - Entregas"
    
    # Formatear importes
    def format_amount(amount):
        return fmt_money(amount, currency="EUR", precision=2)
    
    # Logo URL
    logo_url = ""
    if company_logo:
        logo_url = get_url() + company_logo
    
    # Generar HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm;
            }}
            
            body {{
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.5;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                border-bottom: 3px solid #003366;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            
            .logo {{
                max-width: 200px;
                max-height: 80px;
            }}
            
            .company-info {{
                text-align: right;
                font-size: 10pt;
                color: #666;
            }}
            
            .company-name {{
                font-size: 14pt;
                font-weight: bold;
                color: #003366;
                margin-bottom: 5px;
            }}
            
            .title {{
                text-align: center;
                margin: 30px 0;
            }}
            
            .title h1 {{
                font-size: 18pt;
                color: #003366;
                margin: 0;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            
            .title h2 {{
                font-size: 14pt;
                color: #666;
                margin: 10px 0 0 0;
                font-weight: normal;
            }}
            
            .subtitle {{
                font-size: 12pt;
                color: #003366;
                margin-top: 5px;
            }}
            
            .section {{
                margin: 25px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #003366;
            }}
            
            .section-title {{
                font-size: 12pt;
                font-weight: bold;
                color: #003366;
                margin-bottom: 15px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .data-row {{
                display: flex;
                margin: 8px 0;
            }}
            
            .data-label {{
                width: 180px;
                font-weight: 600;
                color: #555;
            }}
            
            .data-value {{
                flex: 1;
                color: #333;
            }}
            
            .amounts-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            
            .amounts-table th {{
                background: #003366;
                color: white;
                padding: 12px 15px;
                text-align: center;
                font-weight: 600;
                font-size: 10pt;
            }}
            
            .amounts-table td {{
                padding: 12px 15px;
                text-align: right;
                border-bottom: 1px solid #ddd;
                font-size: 11pt;
            }}
            
            .amounts-table tr:nth-child(even) {{
                background: #f8f9fa;
            }}
            
            .amounts-table .total-row {{
                background: #e8f4f8 !important;
                font-weight: bold;
            }}
            
            .amounts-table .total-row td {{
                border-top: 2px solid #003366;
                font-size: 12pt;
                color: #003366;
            }}
            
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 9pt;
                color: #888;
                text-align: center;
            }}
            
            .legal-notice {{
                margin-top: 30px;
                padding: 15px;
                background: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 5px;
                font-size: 9pt;
                color: #856404;
            }}
            
            .signature-area {{
                margin-top: 50px;
                display: flex;
                justify-content: space-between;
            }}
            
            .signature-box {{
                width: 45%;
                text-align: center;
            }}
            
            .signature-line {{
                border-top: 1px solid #333;
                margin-top: 60px;
                padding-top: 10px;
                font-size: 10pt;
            }}
            
            .highlight {{
                background: #003366;
                color: white;
                padding: 3px 8px;
                border-radius: 3px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                {"<img src='" + logo_url + "' class='logo' />" if logo_url else "<div style='width:200px;'></div>"}
            </div>
            <div class="company-info">
                <div class="company-name">{company}</div>
                <div>{company_address}</div>
            </div>
        </div>
        
        <div class="title">
            <h1>Certificado Modelo 347</h1>
            <h2>Declaración Anual de Operaciones con Terceras Personas</h2>
            <div class="subtitle">Ejercicio Fiscal <span class="highlight">{year}</span></div>
        </div>
        
        <div class="section">
            <div class="section-title">Datos del {tipo_tercero}</div>
            <div class="data-row">
                <div class="data-label">Nombre / Razón Social:</div>
                <div class="data-value"><strong>{party_name}</strong></div>
            </div>
            <div class="data-row">
                <div class="data-label">NIF/CIF:</div>
                <div class="data-value">{nif or "No disponible"}</div>
            </div>
            <div class="data-row">
                <div class="data-label">Código Provincia:</div>
                <div class="data-value">{provincia or "No disponible"}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Datos de la Operación</div>
            <div class="data-row">
                <div class="data-label">Tipo de Operación:</div>
                <div class="data-value">{tipo_operacion}</div>
            </div>
            <div class="data-row">
                <div class="data-label">Clave de Operación:</div>
                <div class="data-value"><span class="highlight">{clave}</span> - {clave_desc.split(" - ")[1]}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Desglose de Importes (IVA Incluido)</div>
            <table class="amounts-table">
                <thead>
                    <tr>
                        <th style="text-align: left;">Período</th>
                        <th>Importe</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="text-align: left;">1er Trimestre (Enero - Marzo)</td>
                        <td>{format_amount(t1)}</td>
                    </tr>
                    <tr>
                        <td style="text-align: left;">2º Trimestre (Abril - Junio)</td>
                        <td>{format_amount(t2)}</td>
                    </tr>
                    <tr>
                        <td style="text-align: left;">3er Trimestre (Julio - Septiembre)</td>
                        <td>{format_amount(t3)}</td>
                    </tr>
                    <tr>
                        <td style="text-align: left;">4º Trimestre (Octubre - Diciembre)</td>
                        <td>{format_amount(t4)}</td>
                    </tr>
                    <tr class="total-row">
                        <td style="text-align: left;"><strong>TOTAL ANUAL</strong></td>
                        <td><strong>{format_amount(total)}</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="legal-notice">
            <strong>AVISO IMPORTANTE:</strong> Este documento es un certificado informativo de las operaciones 
            realizadas durante el ejercicio {year} que serán incluidas en la Declaración Anual de Operaciones 
            con Terceras Personas (Modelo 347) ante la Agencia Tributaria. Le rogamos que compruebe los datos 
            y, en caso de discrepancia, se ponga en contacto con nosotros a la mayor brevedad posible.
        </div>
        
        <div class="signature-area">
            <div class="signature-box">
                <div class="signature-line">
                    Firma y sello de la empresa
                </div>
            </div>
            <div class="signature-box">
                <div class="signature-line">
                    Fecha: {nowdate()}
                </div>
            </div>
        </div>
        
        <div class="footer">
            Documento generado automáticamente por el sistema ERP de {company}<br>
            Este documento tiene carácter meramente informativo
        </div>
    </body>
    </html>
    """
    
    return get_pdf(html)


def get_company_address(company):
    """Obtiene la dirección formateada de la empresa."""
    address = frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
        "parent"
    )
    
    if address:
        addr = frappe.get_doc("Address", address)
        parts = []
        if addr.address_line1:
            parts.append(addr.address_line1)
        if addr.city:
            parts.append(addr.city)
        if addr.pincode:
            parts.append(addr.pincode)
        return ", ".join(parts)
    
    return ""


def get_email_template(company, year, party_name, party_type, total):
    """Genera el contenido del email."""
    
    if party_type == "Supplier":
        tipo = "proveedor"
        relacion = "le hemos realizado compras"
    else:
        tipo = "cliente"
        relacion = "nos ha realizado compras"
    
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #003366; color: white; padding: 20px; text-align: center;">
            <h2 style="margin: 0;">Certificado Modelo 347</h2>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Ejercicio {year}</p>
        </div>
        
        <div style="padding: 30px; background: #f9f9f9;">
            <p>Estimado/a <strong>{party_name}</strong>,</p>
            
            <p>De acuerdo con la normativa fiscal vigente, le comunicamos que durante el 
            ejercicio <strong>{year}</strong>, como {tipo} de <strong>{company}</strong>, 
            {relacion} por un importe total de <strong>{fmt_money(total, currency='EUR', precision=2)}</strong> 
            (IVA incluido).</p>
            
            <p>Adjunto a este correo encontrará el certificado detallado con el desglose 
            trimestral de las operaciones, que serán incluidas en nuestra Declaración Anual 
            de Operaciones con Terceras Personas (Modelo 347).</p>
            
            <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>IMPORTANTE:</strong> Le rogamos que revise la información y, en caso 
                de detectar alguna discrepancia, se ponga en contacto con nosotros antes del 
                <strong>28 de febrero</strong> para poder realizar las correcciones oportunas.
            </div>
            
            <p>Quedamos a su disposición para cualquier aclaración.</p>
            
            <p>Atentamente,<br>
            <strong>{company}</strong></p>
        </div>
        
        <div style="background: #eee; padding: 15px; text-align: center; font-size: 12px; color: #666;">
            Este es un correo automático generado por el sistema ERP.<br>
            Por favor, no responda directamente a este mensaje.
        </div>
    </div>
    """


@frappe.whitelist()
def get_email_stats(company, fiscal_year, party_type=None):
    """
    Obtiene estadísticas de los emails a enviar.
    
    Returns:
        dict con conteo de terceros con/sin email
    """
    from spain_account.spain_accounting.report.modelo_347.modelo_347 import execute
    
    filters = {
        "company": company,
        "fiscal_year": fiscal_year,
        "party_type": party_type or ""
    }
    
    columns, data = execute(filters)
    
    with_email = 0
    without_email = 0
    customers = 0
    suppliers = 0
    
    for row in data:
        if row.get("email"):
            with_email += 1
        else:
            without_email += 1
        
        if row.get("party_type_code") == "Customer":
            customers += 1
        else:
            suppliers += 1
    
    return {
        "total": len(data),
        "with_email": with_email,
        "without_email": without_email,
        "customers": customers,
        "suppliers": suppliers
    }
