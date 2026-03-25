import frappe

def execute():
    """
    Automatically links standard Modes of Payment to their corresponding SAT Payment Method codes.
    """
    frappe.print("Iniciando enlace automático de Formas de Pago con códigos del SAT...")

    # Mapping from common Mode of Payment names (and parts) to SAT codes.
    # Case-insensitive.
    payment_mapping = {
        "efectivo": "01",
        "cash": "01",
        "cheque": "02",
        "check": "02",
        "transferencia": "03",
        "transfer": "03",
        "tarjeta de crédito": "04",
        "credit card": "04",
        "crédito": "04",
        "monedero": "05",
        "dinero electrónico": "06",
        "vales": "08",
        "por definir": "99",
    }

    # Get all existing SAT Payment Method codes to ensure we link to valid records.
    sat_codes = frappe.get_all("SAT Payment Method", fields=["name", "description"])
    sat_code_map = {d.name: d.description for d in sat_codes}

    if not sat_code_map:
        frappe.print("Error: No se encontraron 'SAT Payment Method' en el sistema. Sincronice los catálogos del SAT primero y vuelva a intentarlo.")
        return

    # Get all Modes of Payment
    modes_of_payment = frappe.get_all("Mode of Payment", fields=["name", "sat_payment_method"])

    updated_count = 0
    skipped_count = 0
    not_found_count = 0

    for mop in modes_of_payment:
        if mop.get("sat_payment_method"):
            skipped_count += 1
            continue

        mop_name_lower = mop.name.lower()
        found_code = None

        # Find a matching code from our mapping
        for key, code in payment_mapping.items():
            if key in mop_name_lower:
                found_code = code
                break
        
        if found_code and found_code in sat_code_map:
            try:
                doc = frappe.get_doc("Mode of Payment", mop.name)
                doc.sat_payment_method = found_code
                doc.save(ignore_permissions=True)
                frappe.print(f"OK: '{mop.name}' fue enlazado con el código SAT '{found_code}' ({sat_code_map[found_code]}).")
                updated_count += 1
            except Exception as e:
                frappe.log_error(f"Error al actualizar '{mop.name}'", str(e))
                frappe.print(f"Error: No se pudo actualizar '{mop.name}'. Detalles en el log de errores.")
        else:
            frappe.print(f"Aviso: No se encontró un código SAT para '{mop.name}'. Se omitió.")
            not_found_count += 1

    frappe.db.commit()
    frappe.print(f"
--- Proceso completado ---")
    frappe.print(f"Formas de pago actualizadas exitosamente: {updated_count}")
    frappe.print(f"Omitidas (ya tenían un código asignado): {skipped_count}")
    frappe.print(f"Omitidas (no se encontró un código compatible): {not_found_count}")

