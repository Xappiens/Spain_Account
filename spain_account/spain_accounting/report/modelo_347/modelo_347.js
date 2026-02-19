// Copyright (c) 2024, Xappiens and contributors
// For license information, please see license.txt

frappe.query_reports["Modelo 347"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Empresa"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "fiscal_year",
			label: __("Año Fiscal"),
			fieldtype: "Link",
			options: "Fiscal Year",
			reqd: 1,
			on_change: function() {
				let fiscal_year = frappe.query_report.get_filter_value("fiscal_year");
				if (fiscal_year) {
					frappe.query_report.refresh();
				}
			}
		},
		{
			fieldname: "party_type",
			label: __("Tipo de Tercero"),
			fieldtype: "Select",
			options: "\nCustomer\nSupplier",
			default: "",
			get_data: function(txt) {
				return [
					{ value: "", label: __("Todos") },
					{ value: "Customer", label: __("Cliente") },
					{ value: "Supplier", label: __("Proveedor") }
				];
			}
		}
	],

	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Resaltar totales altos
		if (column.fieldname === "total" && data && data.total >= 6000) {
			value = `<span style="font-weight: bold;">${value}</span>`;
		}
		
		// Colorear tipo de tercero
		if (column.fieldname === "party_type" && data) {
			if (data.party_type_code === "Supplier") {
				value = `<span style="color: var(--orange-600);">${value}</span>`;
			} else if (data.party_type_code === "Customer") {
				value = `<span style="color: var(--blue-600);">${value}</span>`;
			}
		}
		
		// Colorear clave de operación
		if (column.fieldname === "clave_operacion" && data) {
			let color = data.clave_operacion === "A" ? "var(--orange-600)" : "var(--blue-600)";
			value = `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
		}
		
		return value;
	},

	onload: function(report) {
		// Establecer año fiscal anterior por defecto (el 347 se presenta sobre el año anterior)
		set_previous_fiscal_year(report);
		
		// Añadir botones de navegación de año
		report.page.add_inner_button(__("◀ Año Anterior"), function() {
			navigate_year(report, -1);
		});
		
		report.page.add_inner_button(__("Año Siguiente ▶"), function() {
			navigate_year(report, 1);
		});
		
		// Añadir menú de acciones para envío de emails
		report.page.add_menu_item(__("📧 Enviar Correo de Prueba"), function() {
			show_test_email_dialog(report);
		});
		
		report.page.add_menu_item(__("📨 Enviar a Todos los Terceros"), function() {
			show_send_all_dialog(report);
		});
		
		report.page.add_menu_item(__("📄 Vista Previa PDF"), function() {
			show_pdf_preview(report);
		});
		
		report.page.add_menu_item(__("📊 Ver Estadísticas de Envío"), function() {
			show_email_stats(report);
		});
		
		// Añadir información del modelo 347
		report.page.add_inner_message(
			__("Modelo 347: Declaración anual de operaciones con terceras personas. Umbral: 3.005,06€ (IVA incluido). Presentación: Febrero.")
		);
	},

	get_datatable_options(options) {
		return Object.assign(options, {
			checkboxColumn: true,
			events: {
				onCheckRow: function() {
					// Calcular totales de filas seleccionadas
					let checked_rows = frappe.query_report.datatable.rowmanager.getCheckedRows();
					if (checked_rows.length > 0) {
						calculate_selected_totals(checked_rows);
					}
				}
			}
		});
	}
};

function set_previous_fiscal_year(report) {
	// Calcular el año anterior al actual
	let previous_year = new Date().getFullYear() - 1;
	
	// Buscar el fiscal year correspondiente al año anterior
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Fiscal Year",
			filters: [
				["year_start_date", ">=", `${previous_year}-01-01`],
				["year_end_date", "<=", `${previous_year}-12-31`]
			],
			fields: ["name"],
			limit_page_length: 1
		},
		async: false,
		callback: function(response) {
			if (response.message && response.message.length > 0) {
				report.set_filter_value("fiscal_year", response.message[0].name);
			} else {
				// Intentar buscar por nombre que contenga el año
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Fiscal Year",
						filters: [["name", "like", `%${previous_year}%`]],
						fields: ["name"],
						limit_page_length: 1
					},
					async: false,
					callback: function(r) {
						if (r.message && r.message.length > 0) {
							report.set_filter_value("fiscal_year", r.message[0].name);
						}
					}
				});
			}
		}
	});
}

function navigate_year(report, direction) {
	let current_year = report.get_filter_value("fiscal_year");
	if (!current_year) return;
	
	// Obtener el año numérico del fiscal year actual
	frappe.db.get_value("Fiscal Year", current_year, "year").then(r => {
		if (r && r.message && r.message.year) {
			let target_year = parseInt(r.message.year) + direction;
			
			// Buscar el fiscal year correspondiente
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "Fiscal Year",
					filters: { year: target_year },
					fields: ["name"]
				},
				async: false,
				callback: function(response) {
					if (response.message && response.message.length > 0) {
						report.set_filter_value("fiscal_year", response.message[0].name);
					} else {
						frappe.msgprint(__("No existe el año fiscal {0}", [target_year]));
					}
				}
			});
		}
	});
}

function calculate_selected_totals(checked_rows) {
	let data = frappe.query_report.data;
	let total_t1 = 0, total_t2 = 0, total_t3 = 0, total_t4 = 0, total_anual = 0;
	
	checked_rows.forEach(row_idx => {
		let row = data[row_idx];
		if (row) {
			total_t1 += flt(row.t1);
			total_t2 += flt(row.t2);
			total_t3 += flt(row.t3);
			total_t4 += flt(row.t4);
			total_anual += flt(row.total);
		}
	});
	
	frappe.show_alert({
		message: __("Seleccionados: {0} registros | Total: {1}", [
			checked_rows.length,
			format_currency(total_anual, frappe.defaults.get_default("currency"))
		]),
		indicator: "blue"
	}, 5);
}

// ==================== FUNCIONES DE ENVÍO DE EMAIL ====================

function show_test_email_dialog(report) {
	let company = report.get_filter_value("company");
	let fiscal_year = report.get_filter_value("fiscal_year");
	let party_type = report.get_filter_value("party_type");
	
	if (!company || !fiscal_year) {
		frappe.msgprint(__("Por favor, seleccione una empresa y un año fiscal"));
		return;
	}
	
	let dialog = new frappe.ui.Dialog({
		title: __("Enviar Correo de Prueba"),
		fields: [
			{
				fieldname: "info",
				fieldtype: "HTML",
				options: `<div class="alert alert-info">
					<strong>Modo Prueba:</strong> Se enviará UN correo de prueba con el certificado 
					del primer tercero del reporte a la dirección que indique.
				</div>`
			},
			{
				fieldname: "test_email",
				fieldtype: "Data",
				label: __("Email de Prueba"),
				reqd: 1,
				default: frappe.session.user,
				options: "Email"
			},
			{
				fieldname: "party_type_filter",
				fieldtype: "Select",
				label: __("Tipo de Tercero"),
				options: "Todos\nCliente\nProveedor",
				default: party_type === "Customer" ? "Cliente" : (party_type === "Supplier" ? "Proveedor" : "Todos")
			}
		],
		primary_action_label: __("Enviar Prueba"),
		primary_action: function(values) {
			dialog.hide();
			
			let party_type_value = "";
			if (values.party_type_filter === "Cliente") party_type_value = "Customer";
			else if (values.party_type_filter === "Proveedor") party_type_value = "Supplier";
			
			frappe.call({
				method: "spain_account.spain_accounting.report.modelo_347.modelo_347_utils.send_modelo_347_emails",
				args: {
					company: company,
					fiscal_year: fiscal_year,
					party_type: party_type_value,
					test_email: values.test_email
				},
				freeze: true,
				freeze_message: __("Enviando correo de prueba..."),
				callback: function(r) {
					if (r.message) {
						let result = r.message;
						if (result.sent > 0) {
							frappe.msgprint({
								title: __("Correo de Prueba Enviado"),
								indicator: "green",
								message: __("Se ha enviado un correo de prueba a {0}", [values.test_email])
							});
						} else {
							frappe.msgprint({
								title: __("Sin Datos"),
								indicator: "orange",
								message: __("No hay datos para enviar. Verifique los filtros del reporte.")
							});
						}
					}
				}
			});
		}
	});
	
	dialog.show();
}

function show_send_all_dialog(report) {
	let company = report.get_filter_value("company");
	let fiscal_year = report.get_filter_value("fiscal_year");
	let party_type = report.get_filter_value("party_type");
	
	if (!company || !fiscal_year) {
		frappe.msgprint(__("Por favor, seleccione una empresa y un año fiscal"));
		return;
	}
	
	// Primero obtener estadísticas
	frappe.call({
		method: "spain_account.spain_accounting.report.modelo_347.modelo_347_utils.get_email_stats",
		args: {
			company: company,
			fiscal_year: fiscal_year,
			party_type: party_type
		},
		callback: function(r) {
			if (r.message) {
				let stats = r.message;
				show_send_all_confirmation(report, company, fiscal_year, party_type, stats);
			}
		}
	});
}

function show_send_all_confirmation(report, company, fiscal_year, party_type, stats) {
	let dialog = new frappe.ui.Dialog({
		title: __("Enviar Certificados a Todos los Terceros"),
		fields: [
			{
				fieldname: "warning",
				fieldtype: "HTML",
				options: `<div class="alert alert-warning">
					<strong>⚠️ ATENCIÓN:</strong> Esta acción enviará correos electrónicos REALES 
					a todos los terceros con email registrado. Esta acción no se puede deshacer.
				</div>`
			},
			{
				fieldname: "stats",
				fieldtype: "HTML",
				options: `<div class="card" style="padding: 15px; margin: 10px 0;">
					<h5>Resumen de envío:</h5>
					<table class="table table-bordered" style="margin-top: 10px;">
						<tr>
							<td><strong>Total de terceros:</strong></td>
							<td>${stats.total}</td>
						</tr>
						<tr>
							<td><strong>Clientes:</strong></td>
							<td>${stats.customers}</td>
						</tr>
						<tr>
							<td><strong>Proveedores:</strong></td>
							<td>${stats.suppliers}</td>
						</tr>
						<tr style="background: #d4edda;">
							<td><strong>Con email (se enviarán):</strong></td>
							<td><strong>${stats.with_email}</strong></td>
						</tr>
						<tr style="background: #f8d7da;">
							<td><strong>Sin email (se omitirán):</strong></td>
							<td>${stats.without_email}</td>
						</tr>
					</table>
				</div>`
			},
			{
				fieldname: "party_type_filter",
				fieldtype: "Select",
				label: __("Enviar solo a"),
				options: "Todos\nSolo Clientes\nSolo Proveedores",
				default: "Todos"
			},
			{
				fieldname: "confirmation",
				fieldtype: "Check",
				label: __("Confirmo que deseo enviar {0} correos electrónicos", [stats.with_email]),
				reqd: 1
			}
		],
		primary_action_label: __("Enviar Todos"),
		primary_action: function(values) {
			if (!values.confirmation) {
				frappe.msgprint(__("Debe confirmar la acción"));
				return;
			}
			
			dialog.hide();
			
			let party_type_value = "";
			if (values.party_type_filter === "Solo Clientes") party_type_value = "Customer";
			else if (values.party_type_filter === "Solo Proveedores") party_type_value = "Supplier";
			
			frappe.call({
				method: "spain_account.spain_accounting.report.modelo_347.modelo_347_utils.send_modelo_347_emails",
				args: {
					company: company,
					fiscal_year: fiscal_year,
					party_type: party_type_value,
					test_email: null
				},
				freeze: true,
				freeze_message: __("Enviando correos... Por favor espere."),
				callback: function(r) {
					if (r.message) {
						let result = r.message;
						let msg = `
							<div style="padding: 10px;">
								<h4>Resultado del envío:</h4>
								<table class="table table-bordered">
									<tr style="background: #d4edda;">
										<td><strong>Enviados correctamente:</strong></td>
										<td><strong>${result.sent}</strong></td>
									</tr>
									<tr style="background: #f8d7da;">
										<td><strong>Fallidos:</strong></td>
										<td>${result.failed}</td>
									</tr>
									<tr>
										<td><strong>Omitidos (sin email):</strong></td>
										<td>${result.skipped}</td>
									</tr>
								</table>
							</div>
						`;
						
						if (result.errors && result.errors.length > 0) {
							msg += `<div class="alert alert-danger" style="margin-top: 10px;">
								<strong>Errores:</strong><br>`;
							result.errors.forEach(err => {
								msg += `- ${err.party}: ${err.error}<br>`;
							});
							msg += `</div>`;
						}
						
						frappe.msgprint({
							title: __("Envío Completado"),
							indicator: result.failed > 0 ? "orange" : "green",
							message: msg
						});
					}
				}
			});
		}
	});
	
	dialog.show();
}

function show_pdf_preview(report) {
	let data = frappe.query_report.data;
	
	if (!data || data.length === 0) {
		frappe.msgprint(__("No hay datos en el reporte para generar vista previa"));
		return;
	}
	
	// Crear opciones para el selector
	let options = data.map((row, idx) => {
		return {
			value: idx,
			label: `${row.party_name} (${row.party_type}) - ${format_currency(row.total)}`
		};
	});
	
	let dialog = new frappe.ui.Dialog({
		title: __("Vista Previa del PDF"),
		fields: [
			{
				fieldname: "party_idx",
				fieldtype: "Select",
				label: __("Seleccione un tercero"),
				options: options.map(o => o.label),
				reqd: 1
			}
		],
		primary_action_label: __("Ver PDF"),
		primary_action: function(values) {
			let selected_idx = options.findIndex(o => o.label === values.party_idx);
			let party_data = data[selected_idx];
			
			dialog.hide();
			
			frappe.call({
				method: "spain_account.spain_accounting.report.modelo_347.modelo_347_utils.preview_modelo_347_pdf",
				args: {
					company: report.get_filter_value("company"),
					fiscal_year: report.get_filter_value("fiscal_year"),
					party_data: JSON.stringify(party_data)
				},
				freeze: true,
				freeze_message: __("Generando PDF..."),
				callback: function(r) {
					if (r.message) {
						// Abrir PDF en nueva ventana
						let pdfWindow = window.open("");
						pdfWindow.document.write(
							`<iframe width='100%' height='100%' src='data:application/pdf;base64,${r.message}'></iframe>`
						);
					}
				}
			});
		}
	});
	
	dialog.show();
}

function show_email_stats(report) {
	let company = report.get_filter_value("company");
	let fiscal_year = report.get_filter_value("fiscal_year");
	let party_type = report.get_filter_value("party_type");
	
	if (!company || !fiscal_year) {
		frappe.msgprint(__("Por favor, seleccione una empresa y un año fiscal"));
		return;
	}
	
	frappe.call({
		method: "spain_account.spain_accounting.report.modelo_347.modelo_347_utils.get_email_stats",
		args: {
			company: company,
			fiscal_year: fiscal_year,
			party_type: party_type
		},
		callback: function(r) {
			if (r.message) {
				let stats = r.message;
				let percent_with_email = stats.total > 0 ? Math.round((stats.with_email / stats.total) * 100) : 0;
				
				frappe.msgprint({
					title: __("Estadísticas de Envío - Modelo 347"),
					indicator: percent_with_email >= 80 ? "green" : (percent_with_email >= 50 ? "orange" : "red"),
					message: `
						<div style="padding: 10px;">
							<h4>${company} - ${fiscal_year}</h4>
							<table class="table table-bordered" style="margin-top: 15px;">
								<tr>
									<td><strong>Total de terceros:</strong></td>
									<td><strong>${stats.total}</strong></td>
								</tr>
								<tr>
									<td>Clientes:</td>
									<td>${stats.customers}</td>
								</tr>
								<tr>
									<td>Proveedores:</td>
									<td>${stats.suppliers}</td>
								</tr>
								<tr style="background: #d4edda;">
									<td><strong>Con email:</strong></td>
									<td><strong>${stats.with_email}</strong> (${percent_with_email}%)</td>
								</tr>
								<tr style="background: #f8d7da;">
									<td><strong>Sin email:</strong></td>
									<td><strong>${stats.without_email}</strong></td>
								</tr>
							</table>
							
							<div class="progress" style="margin-top: 15px; height: 25px;">
								<div class="progress-bar bg-success" style="width: ${percent_with_email}%">
									${percent_with_email}% con email
								</div>
							</div>
							
							${stats.without_email > 0 ? `
								<div class="alert alert-warning" style="margin-top: 15px;">
									<strong>Nota:</strong> Hay ${stats.without_email} tercero(s) sin email registrado. 
									Para enviarles el certificado, debe completar su dirección de email en la 
									ficha de Cliente o Proveedor, o en su Dirección (Address).
								</div>
							` : ''}
						</div>
					`
				});
			}
		}
	});
}
