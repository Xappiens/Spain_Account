# Copyright (c) 2024, Xappiens and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, fmt_money, get_url, flt
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
import json
import unicodedata
import random
import math


# =============================================================================
# FUNCIONES DE FORMATEO PARA ARCHIVO AEAT (TXT)
# =============================================================================

def remove_accents_and_upper(text):
    """
    Convierte a mayúsculas y elimina vocales acentuadas.
    Requerido por el formato AEAT (ISO-8859-1).
    
    IMPORTANTE según manual AEAT:
    - Ñ se MANTIENE (ASCII 209 / 0xD1 en ISO-8859-1)
    - Ç se MANTIENE (ASCII 199 / 0xC7 en ISO-8859-1)
    - Solo las vocales acentuadas se convierten (á→A, é→E, etc.)
    """
    if not text:
        return ""
    text = text.upper()
    
    # Preservar Ñ y Ç antes de normalizar
    text = text.replace('ñ', 'Ñ')
    text = text.replace('ç', 'Ç')
    
    # Mapa de reemplazo para vocales acentuadas
    accent_map = {
        'Á': 'A', 'À': 'A', 'Ä': 'A', 'Â': 'A', 'Ã': 'A',
        'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E',
        'Í': 'I', 'Ì': 'I', 'Ï': 'I', 'Î': 'I',
        'Ó': 'O', 'Ò': 'O', 'Ö': 'O', 'Ô': 'O', 'Õ': 'O',
        'Ú': 'U', 'Ù': 'U', 'Ü': 'U', 'Û': 'U',
    }
    
    for accented, plain in accent_map.items():
        text = text.replace(accented, plain)
    
    # Eliminar cualquier otro carácter que no sea ISO-8859-1 válido
    # pero manteniendo Ñ y Ç
    result = []
    for char in text:
        try:
            char.encode('iso-8859-1')
            result.append(char)
        except UnicodeEncodeError:
            pass
    
    return ''.join(result)


def to_alfa(cadena, start, end):
    """
    Devuelve una cadena alineada a la izquierda y rellenada con espacios hasta ocupar
    el ancho (end - start + 1).
    """
    ancho = (end - start) + 1
    txt = remove_accents_and_upper(cadena or "")
    if len(txt) > ancho:
        txt = txt[:ancho]
    return txt.ljust(ancho, ' ')


def to_num(numero, start, end, decimals=0):
    """
    Devuelve una cadena numérica alineada a la derecha y rellenada con ceros a la izquierda,
    para ocupar el ancho (end - start + 1).
    """
    ancho = (end - start) + 1
    if numero is None or not str(numero).strip():
        numero = 0
    try:
        num_abs = abs(float(numero))
    except Exception:
        num_abs = 0.0
    parte_entera = int(num_abs)
    parte_decimal = int(round((num_abs - parte_entera) * (10**decimals)))
    ent_str = str(parte_entera)
    dec_str = str(parte_decimal).rjust(decimals, '0') if decimals > 0 else ""
    num_str = ent_str + dec_str
    return num_str.rjust(ancho, '0')


def format_nif_for_aeat(nif):
    """
    Ajusta un NIF/CIF/NIE a 9 caracteres, rellenando a la izquierda con ceros.
    """
    nif = (nif or "").strip().upper().replace('-', '').replace(' ', '')
    return nif.rjust(9, '0')[:9]


def safe_float(value):
    """Convierte un valor a float de forma segura, retornando 0 si falla."""
    try:
        f = float(value)
        if math.isnan(f):
            return 0.0
        return f
    except Exception:
        return 0.0


# =============================================================================
# FUNCIONES DE CONSTRUCCIÓN DE REGISTROS AEAT
# =============================================================================

def build_registro_tipo1(ejercicio, nif_declarante, nombre_declarante,
                         telefono_contacto, persona_contacto="",
                         num_ident_decl="3470000000001",
                         decl_complementaria=False, decl_sustitutiva=False,
                         num_ident_anterior="",
                         num_total_personas=0, importe_total_anual=0.0,
                         num_total_inmuebles=0, importe_total_arrend=0.0,
                         nif_representante_legal=""):
    """
    Construye el registro de tipo 1 (declarante) de 500 posiciones.
    Formato según especificaciones de la AEAT para el Modelo 347.
    
    POSICIONES (base 1 según manual AEAT, convertidas a índices base 0 en Python):
    1: Tipo registro
    2-4: Modelo (347)
    5-8: Ejercicio
    9-17: NIF declarante
    18-57: Apellidos/nombre o razón social
    58: Tipo soporte (T=telemático)
    59-67: Teléfono contacto
    68-107: Persona con quien relacionarse
    108-120: Número identificativo declaración
    121: Declaración complementaria
    122: Declaración sustitutiva
    123-135: Número identificativo anterior
    136-144: Número total de personas
    145: Signo importe total
    146-160: Importe total anual
    161-169: Número total inmuebles
    170: Signo importe arrendamiento
    171-185: Importe total arrendamiento
    186-500: Blancos
    """
    line = [" "] * 500
    
    # Pos 1: Tipo registro
    line[0] = '1'
    # Pos 2-4: Modelo
    line[1:4] = list("347")
    # Pos 5-8: Ejercicio (4 dígitos)
    line[4:8] = list(str(ejercicio).zfill(4)[:4])
    # Pos 9-17: NIF declarante (9 caracteres)
    line[8:17] = list(format_nif_for_aeat(nif_declarante))
    # Pos 18-57: Nombre declarante (40 caracteres)
    line[17:57] = list(to_alfa(nombre_declarante, 0, 39))
    # Pos 58: Tipo soporte
    line[57] = 'T'
    # Pos 59-67: Teléfono (9 dígitos)
    tel_str = "".join(c for c in (telefono_contacto or "") if c.isdigit())
    tel_str = tel_str[:9].rjust(9, '0') if tel_str else "000000000"
    line[58:67] = list(tel_str)
    # Pos 68-107: Persona contacto (40 caracteres)
    line[67:107] = list(to_alfa(persona_contacto, 0, 39))
    # Pos 108-120: Número identificativo declaración (13 dígitos)
    line[107:120] = list(str(num_ident_decl).zfill(13)[:13])
    # Pos 121: Declaración complementaria
    line[120] = 'C' if decl_complementaria else ' '
    # Pos 122: Declaración sustitutiva
    line[121] = 'S' if decl_sustitutiva else ' '
    # Pos 123-135: Número identificativo anterior (13 dígitos)
    line[122:135] = list(str(num_ident_anterior or 0).zfill(13)[:13])
    # Pos 136-144: Número total personas (9 dígitos)
    line[135:144] = list(str(int(num_total_personas)).zfill(9)[:9])
    # Pos 145: Signo importe total
    line[144] = 'N' if importe_total_anual < 0 else ' '
    # Pos 146-160: Importe total anual (13 enteros + 2 decimales = 15 dígitos)
    line[145:160] = list(to_num(abs(importe_total_anual), 0, 14, decimals=2))
    # Pos 161-169: Número total inmuebles (9 dígitos)
    line[160:169] = list(str(int(num_total_inmuebles)).zfill(9)[:9])
    # Pos 170: Signo importe arrendamiento
    line[169] = 'N' if importe_total_arrend < 0 else ' '
    # Pos 171-185: Importe total arrendamiento (15 dígitos)
    line[170:185] = list(to_num(abs(importe_total_arrend), 0, 14, decimals=2))
    # Pos 186-500: Blancos (ya inicializados)
    
    return "".join(line)


def build_registro_tipo2(ejercicio, nif_declarante, tercero_info):
    """
    Construye el registro de tipo 2 (declarado) de 500 posiciones.
    Formato según especificaciones de la AEAT para el Modelo 347.
    
    POSICIONES (base 1 según manual AEAT):
    1: Tipo registro (2)
    2-4: Modelo (347)
    5-8: Ejercicio
    9-17: NIF declarante
    18-26: NIF declarado
    27-35: NIF representante legal
    36-75: Apellidos/nombre o razón social declarado (40 chars)
    76: Tipo hoja (D=Declarado)
    77-78: Código provincia
    79-80: Código país
    81: Blanco
    82: Clave operación (A=compras, B=ventas)
    83: Signo importe anual
    84-98: Importe anual (15 dígitos: 13+2)
    99: Operación seguro
    100: Arrendamiento local negocio
    101-115: Importe percibido en metálico
    116: Signo importe transmisiones inmuebles IVA
    117-131: Importe transmisiones inmuebles IVA
    132-135: Ejercicio cobro metálico
    136: Signo T1
    137-151: Importe T1
    152: Signo transmisiones T1
    153-167: Importe transmisiones T1
    168: Signo T2
    169-183: Importe T2
    184: Signo transmisiones T2
    185-199: Importe transmisiones T2
    200: Signo T3
    201-215: Importe T3
    216: Signo transmisiones T3
    217-231: Importe transmisiones T3
    232: Signo T4
    233-247: Importe T4
    248: Signo transmisiones T4
    249-263: Importe transmisiones T4
    264-265: Código país operador intracomunitario
    266-280: NIF operador intracomunitario
    281: Operaciones régimen especial caja IVA
    282: Operación inversión sujeto pasivo
    283: Operaciones depósito distinto aduanero
    284: Signo importe caja IVA
    285-299: Importe caja IVA
    300-500: Blancos
    """
    line = [" "] * 500
    
    # Pos 1: Tipo registro
    line[0] = '2'
    # Pos 2-4: Modelo
    line[1:4] = list("347")
    # Pos 5-8: Ejercicio
    line[4:8] = list(str(ejercicio).zfill(4)[:4])
    # Pos 9-17: NIF declarante
    line[8:17] = list(format_nif_for_aeat(nif_declarante))
    # Pos 18-26: NIF declarado
    line[17:26] = list(format_nif_for_aeat(tercero_info.get("nif", "")))
    # Pos 27-35: NIF representante legal (blancos)
    line[26:35] = list(" " * 9)
    # Pos 36-75: Nombre declarado (40 caracteres)
    line[35:75] = list(to_alfa(tercero_info.get("nombre", ""), 0, 39))
    # Pos 76: Tipo hoja
    line[75] = 'D'
    # Pos 77-78: Código provincia (2 dígitos)
    cp = tercero_info.get("cp") or ""
    cp = "".join(c for c in cp if c.isdigit())[:2]
    line[76:78] = list(cp.zfill(2)[:2] if cp else "  ")
    # Pos 79-80: Código país
    pais = tercero_info.get("pais") or ""
    if pais.lower() in ('es', ""):
        pais = ""
    line[78:80] = list(pais.upper().ljust(2)[:2] if pais else "  ")
    # Pos 81: Blanco
    line[80] = ' '
    # Pos 82: Clave operación
    party_type = tercero_info.get("party_type") or ""
    clave = "A" if party_type == "Supplier" else "B"
    line[81] = clave
    # Pos 83: Signo importe anual
    imp_anual = safe_float(tercero_info.get("importe_anual", 0))
    line[82] = 'N' if imp_anual < 0 else ' '
    # Pos 84-98: Importe anual (15 dígitos)
    line[83:98] = list(to_num(abs(imp_anual), 0, 14, decimals=2))
    # Pos 99: Operación seguro
    line[98] = tercero_info.get("aseguradora", " ")
    # Pos 100: Arrendamiento local negocio
    line[99] = tercero_info.get("arrendamiento_local", " ")
    # Pos 101-115: Importe percibido en metálico
    line[100:115] = list(to_num(0, 0, 14, decimals=2))
    # Pos 116: Signo transmisiones inmuebles IVA
    line[115] = ' '
    # Pos 117-131: Importe transmisiones inmuebles IVA
    line[116:131] = list(to_num(0, 0, 14, decimals=2))
    # Pos 132-135: Ejercicio cobro metálico
    line[131:135] = list("0000")
    
    # TRIMESTRE 1
    # Pos 136: Signo T1
    imp_1t = safe_float(tercero_info.get("importe_1t", 0))
    line[135] = 'N' if imp_1t < 0 else ' '
    # Pos 137-151: Importe T1
    line[136:151] = list(to_num(abs(imp_1t), 0, 14, decimals=2))
    # Pos 152: Signo transmisiones T1
    line[151] = ' '
    # Pos 153-167: Importe transmisiones T1
    line[152:167] = list(to_num(0, 0, 14, decimals=2))
    
    # TRIMESTRE 2
    # Pos 168: Signo T2
    imp_2t = safe_float(tercero_info.get("importe_2t", 0))
    line[167] = 'N' if imp_2t < 0 else ' '
    # Pos 169-183: Importe T2
    line[168:183] = list(to_num(abs(imp_2t), 0, 14, decimals=2))
    # Pos 184: Signo transmisiones T2
    line[183] = ' '
    # Pos 185-199: Importe transmisiones T2
    line[184:199] = list(to_num(0, 0, 14, decimals=2))
    
    # TRIMESTRE 3
    # Pos 200: Signo T3
    imp_3t = safe_float(tercero_info.get("importe_3t", 0))
    line[199] = 'N' if imp_3t < 0 else ' '
    # Pos 201-215: Importe T3
    line[200:215] = list(to_num(abs(imp_3t), 0, 14, decimals=2))
    # Pos 216: Signo transmisiones T3
    line[215] = ' '
    # Pos 217-231: Importe transmisiones T3
    line[216:231] = list(to_num(0, 0, 14, decimals=2))
    
    # TRIMESTRE 4
    # Pos 232: Signo T4
    imp_4t = safe_float(tercero_info.get("importe_4t", 0))
    line[231] = 'N' if imp_4t < 0 else ' '
    # Pos 233-247: Importe T4
    line[232:247] = list(to_num(abs(imp_4t), 0, 14, decimals=2))
    # Pos 248: Signo transmisiones T4
    line[247] = ' '
    # Pos 249-263: Importe transmisiones T4
    line[248:263] = list(to_num(0, 0, 14, decimals=2))
    
    # Pos 264-265: Código país operador intracomunitario
    line[263:265] = list(pais.upper().ljust(2)[:2] if pais else "  ")
    # Pos 266-280: NIF operador intracomunitario (15 caracteres)
    nif_extranjero = tercero_info.get("nif", "") if pais else ""
    line[265:280] = list(to_alfa(nif_extranjero, 0, 14))
    # Pos 281: Operaciones régimen especial caja IVA
    line[280] = ' '
    # Pos 282: Operación inversión sujeto pasivo
    inv_suj_pas = tercero_info.get("inv_suj_pas", " ")
    if isinstance(inv_suj_pas, tuple):
        inv_suj_pas = inv_suj_pas[0] if inv_suj_pas else " "
    line[281] = inv_suj_pas if inv_suj_pas else " "
    # Pos 283: Operaciones depósito distinto aduanero
    line[282] = ' '
    # Pos 284: Signo importe caja IVA
    line[283] = ' '
    # Pos 285-299: Importe caja IVA
    line[284:299] = list(to_num(0, 0, 14, decimals=2))
    # Pos 300-305: Número de convocatoria BDNS (6 dígitos)
    # Solo se cumplimenta cuando clave de operación = "E" (subvenciones)
    # En cualquier otro caso se rellena a ceros
    line[299:305] = list("000000")
    # Pos 306-500: Blancos (ya inicializados)
    
    return "".join(line)


def build_registro_inmueble(ejercicio, nif_declarante, arr):
    """
    Construye el registro de Tipo 2: REGISTRO DE INMUEBLE de 500 posiciones,
    según el manual de la AEAT para el Modelo 347.
    """
    registro = [" "] * 500
    registro[0] = '2'
    registro[1:4] = list("347")
    registro[4:8] = list(to_num(ejercicio, 0, 3))
    registro[8:17] = list(format_nif_for_aeat(nif_declarante))
    
    client = arr.get("client")
    nif_arr = frappe.get_value("Customer", client, "tax_id") or ""
    registro[17:26] = list(format_nif_for_aeat(nif_arr))
    registro[26:35] = list(" " * 9)
    
    nombre_arr = frappe.get_value("Customer", client, "customer_name") or ""
    registro[35:75] = list(to_alfa(nombre_arr, 0, 39))
    registro[75] = 'I'
    registro[76:98] = list(" " * 22)
    
    importe = arr.get("annual_amount", 0)
    registro[98] = "N" if importe < 0 else " "
    importe_abs = abs(importe)
    parte_entera = int(importe_abs)
    parte_decimal = int(round((importe_abs - parte_entera) * 100))
    registro[99:112] = list(str(parte_entera).zfill(13))
    registro[112:114] = list(str(parte_decimal).zfill(2))
    
    situacion = arr.get("situation", 1)
    registro[114] = str(situacion)
    registro[115:140] = list(to_alfa(arr.get("catastro") or "", 0, 24))
    
    for i in range(140, 333):
        registro[i] = " "
    
    registro[140:145] = list(to_alfa(arr.get("via") or "", 0, 4))
    registro[145:195] = list(to_alfa(arr.get("address") or "", 0, 49))
    registro[195:198] = list(to_alfa(arr.get("num_type") or "NUM", 0, 2))
    registro[198:203] = list(to_alfa(arr.get("num_home") or "", 0, 4))
    registro[203:206] = list(to_alfa(arr.get("calif_num") or "", 0, 2))
    registro[206:209] = list(to_alfa(arr.get("bloq") or "", 0, 2))
    registro[209:212] = list(to_alfa(arr.get("portal") or "", 0, 2))
    registro[212:215] = list(to_alfa(arr.get("stair") or "", 0, 2))
    registro[215:218] = list(to_alfa(arr.get("floor") or "", 0, 2))
    registro[218:221] = list(to_alfa(arr.get("door") or "", 0, 2))
    registro[221:261] = list(to_alfa("", 0, 39))
    registro[261:291] = list(to_alfa("", 0, 29))
    registro[291:321] = list(to_alfa(arr.get("municipio") or "", 0, 29))
    registro[321:326] = list(to_alfa(arr.get("cod_mun") or "", 0, 4))
    
    cod_prov_value = (arr.get("cod_prov") or "").strip()
    if not cod_prov_value:
        cod_prov_value = 0
    registro[326:328] = list(to_num(cod_prov_value, 0, 1))
    registro[328:333] = list(to_alfa(arr.get("cp") or "", 0, 4))
    
    return "".join(registro)


def get_party_contact_for_aeat(party, doctype):
    """Obtiene los datos de contacto del tercero desde Address para AEAT."""
    result = frappe.db.sql("""
        SELECT 
            LEFT(ad.pincode, 2) as cp, 
            ad.email_id as email, 
            ad.phone
        FROM `tabAddress` ad
        INNER JOIN `tabDynamic Link` dl ON dl.parent = ad.name
        WHERE dl.link_doctype = %(doctype)s
          AND dl.link_name = %(party)s
        LIMIT 1
    """, {
        "doctype": doctype,
        "party": party
    }, as_dict=True)
    
    if result:
        return result[0].get("cp", ""), result[0].get("email", ""), result[0].get("phone", "")
    return "", "", ""


def get_phone_from_address(link_doctype, link_name):
    """Obtiene el teléfono del primer Address vinculado."""
    result = frappe.db.sql("""
        SELECT ad.phone FROM `tabAddress` ad
        INNER JOIN `tabDynamic Link` dl ON dl.parent = ad.name
        WHERE dl.link_doctype = %s AND dl.link_name = %s
        LIMIT 1
    """, (link_doctype, link_name), as_dict=True)
    if result and result[0].get("phone"):
        return result[0].get("phone")
    return ""


# =============================================================================
# FUNCIÓN PRINCIPAL DE EXPORTACIÓN A TXT PARA AEAT
# =============================================================================

@frappe.whitelist()
def export_modelo_347_txt(filters):
    """
    Genera un archivo .txt para el Modelo 347 compatible con la AEAT.
    
    Args:
        filters: Filtros del reporte (company, fiscal_year, party_type, etc.)
                 Puede incluir datos adicionales del representante legal:
                 - nombre_representante
                 - dni_representante
                 - tlf_contacto
    
    Returns:
        URL del archivo TXT guardado en File
    """
    from spain_account.spain_accounting.report.modelo_347.modelo_347 import execute
    
    if isinstance(filters, str):
        filters = frappe._dict(json.loads(filters))
    
    columns, data = execute(filters)
    
    if not data:
        frappe.throw(_("No hay datos para exportar. Verifique los filtros del reporte."))
    
    company_nif = frappe.get_value("Company", filters.company, "tax_id") or ""
    company_name = frappe.get_value("Company", filters.company, "company_name") or ""
    
    rep_nif = filters.get("dni_representante") or ""
    rep_nombre = filters.get("nombre_representante") or ""
    rep_tlf = filters.get("tlf_contacto") or ""
    
    if not rep_tlf:
        rep_tlf = get_phone_from_address("Company", filters.company)
    
    total_personas = len(data)
    total_importe = sum([flt(d.get("total", 0)) for d in data])
    num_ident_decl = str(3470000000000 + random.randint(1, 9999999990))
    
    num_total_inmuebles = 0
    importe_total_arrend = 0.0
    arrendamientos = []
    
    fiscal_year_doc = frappe.get_doc("Fiscal Year", filters.fiscal_year)
    year = getdate(fiscal_year_doc.year_start_date).year
    
    if frappe.db.exists("DocType", "Arrendamientos"):
        arrendamientos = frappe.get_all(
            "Arrendamientos",
            filters={"year": year},
            fields=["client", "annual_amount", "situation", "catastro", "via",
                    "address", "num_type", "num_home", "calif_num", "bloq",
                    "portal", "stair", "floor", "door", "municipio", "cod_mun",
                    "cod_prov", "cp"]
        )
        
        parties_in_report = [d.get("party_name") for d in data]
        arrendamientos_filtrados = [arr for arr in arrendamientos if arr.get("client") in parties_in_report]
        num_total_inmuebles = len(arrendamientos_filtrados)
        importe_total_arrend = sum([flt(arr.get("annual_amount", 0.0)) for arr in arrendamientos_filtrados])
    
    registro_tipo1 = build_registro_tipo1(
        ejercicio=year,
        nif_declarante=company_nif,
        nombre_declarante=company_name,
        telefono_contacto=rep_tlf,
        persona_contacto=rep_nombre,
        num_ident_decl=num_ident_decl,
        decl_complementaria=False,
        decl_sustitutiva=False,
        num_ident_anterior="",
        num_total_personas=total_personas,
        importe_total_anual=total_importe,
        num_total_inmuebles=num_total_inmuebles,
        importe_total_arrend=importe_total_arrend,
        nif_representante_legal=rep_nif
    )
    
    lines = [registro_tipo1]
    
    for row in data:
        party_name = row.get("party_name", "")
        party_type_code = row.get("party_type_code", "")
        
        cp = row.get("provincia", "")
        
        codigo_pais = ""
        aseguradora = " "
        inv_suj_pas = " "
        arrendamiento_local = " "
        
        if party_name:
            if party_type_code == "Supplier":
                supplier_doc = frappe.get_doc("Supplier", party_name) if frappe.db.exists("Supplier", party_name) else None
                if supplier_doc:
                    supplier_group = supplier_doc.get("supplier_group", "")
                    aseguradora = "X" if supplier_group == "Aseguradora" else " "
                    inv_suj_pas = "X" if supplier_group == "Inversion Suj. Pasivo" else " "
                    if supplier_doc.country:
                        codigo_pais = frappe.db.get_value("Country", supplier_doc.country, "code") or ""
            else:
                customer_doc = frappe.get_doc("Customer", party_name) if frappe.db.exists("Customer", party_name) else None
                if customer_doc:
                    custom_pais = customer_doc.get("custom_pais", "")
                    if custom_pais:
                        codigo_pais = frappe.db.get_value("Country", custom_pais, "code") or ""
        
        if frappe.db.exists("DocType", "Arrendamientos"):
            arr_records = frappe.get_all(
                "Arrendamientos",
                filters={"client": party_name, "year": year},
                fields=["annual_amount"],
                limit=1
            )
            if arr_records:
                arr_amount = round(float(arr_records[0].annual_amount), 2)
                total_347 = round(float(row.get("total", 0)), 2)
                arrendamiento_local = "X" if total_347 == arr_amount else " "
        
        tercero = {
            "nif": row.get("nif") or "",
            "nombre": party_name,
            "cp": cp,
            "pais": codigo_pais,
            "aseguradora": aseguradora,
            "inv_suj_pas": inv_suj_pas,
            "arrendamiento_local": arrendamiento_local,
            "importe_anual": row.get("total", 0),
            "importe_1t": row.get("t1", 0),
            "importe_2t": row.get("t2", 0),
            "importe_3t": row.get("t3", 0),
            "importe_4t": row.get("t4", 0),
            "party_type": party_type_code
        }
        
        registro_tipo2 = build_registro_tipo2(
            ejercicio=year,
            nif_declarante=company_nif,
            tercero_info=tercero
        )
        lines.append(registro_tipo2)
    
    if arrendamientos:
        parties_in_report = [d.get("party_name") for d in data]
        for arr in arrendamientos:
            if arr.get("client") in parties_in_report:
                registro_inmueble = build_registro_inmueble(year, company_nif, arr)
                lines.append(registro_inmueble)
    
    txt_content = "\n".join(lines)
    
    # Guardar el archivo con codificación ASCII/ISO-8859-1 para compatibilidad con AEAT
    import os
    file_name = f"Modelo_347_{year}.txt"
    site_path = frappe.utils.get_site_path("private", "files")
    
    # Asegurar que el directorio existe
    if not os.path.exists(site_path):
        os.makedirs(site_path)
    
    # Generar nombre único para el archivo
    from frappe.utils import random_string
    unique_file_name = f"Modelo_347_{year}_{random_string(6)}.txt"
    file_path = os.path.join(site_path, unique_file_name)
    
    # Escribir el archivo en ISO-8859-1 (Latin-1) según especificaciones AEAT
    # Esto permite Ñ (0xD1) y Ç (0xC7) correctamente
    with open(file_path, 'w', encoding='iso-8859-1', errors='replace') as f:
        f.write(txt_content)
    
    # Crear registro en File doctype
    txt_file = frappe.get_doc({
        "doctype": "File",
        "file_name": unique_file_name,
        "is_private": 1,
        "file_url": f"/private/files/{unique_file_name}"
    })
    txt_file.insert(ignore_permissions=True)
    
    return txt_file.file_url


# =============================================================================
# FUNCIONES DE ENVÍO DE EMAIL (EXISTENTES)
# =============================================================================


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
