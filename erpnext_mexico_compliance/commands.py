import click
import frappe
import sqlite3
import datetime
from erpnext_mexico_compliance.sat_catalogs import get_sqlite_connection

@click.command("sync-sat-catalogs")
def sync_sat_catalogs():
    """Descarga y sincroniza catálogos del SAT desde sqlite a ERPNext."""
    frappe.init(site=frappe.utils.get_sites()[0] if frappe.utils.get_sites() else "site1.local")
    frappe.connect()
    sync_catalogs_logic()
    frappe.destroy()

def sync_catalogs_logic():
    print("Iniciando sincronización de catálogos del SAT para contabilidad...")

    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"Error al obtener base de datos SQLite: {e}")
        return

    # Mapeo de tablas a DocTypes y sus campos
    catalogs_mapping = {
        "cfdi_40_formas_pago": {
            "doctype": "SAT Payment Method",
            "key": "id",
            "fields": {
                "key": "id",
                "key_name": "texto",
                "description": "texto",
                "enabled": "1"
            }
        },
        "cfdi_40_metodos_pago": {
            "doctype": "SAT Payment Option",
            "key": "id",
            "fields": {
                "key": "id",
                "key_name": "texto",
                "description": "texto",
                "enabled": "1"
            }
        },
        "cfdi_40_claves_unidades": {
            "doctype": "SAT UOM Key",
            "key": "id",
            "fields": {
                "key": "id",
                "key_name": "texto",
                "uom_name": "texto",
                "description": "descripcion",
                "enabled": "1"
            }
        },
        "cfdi_40_regimenes_fiscales": {
            "doctype": "SAT Tax Regime",
            "key": "id",
            "fields": {
                "key": "id",
                "key_name": "texto",
                "description": "texto",
                "enabled": "1"
            }
        },
        "cfdi_40_usos_cfdi": {
            "doctype": "SAT CFDI Use",
            "key": "id",
            "fields": {
                "key": "id",
                "key_name": "texto",
                "description": "texto",
                "enabled": "1"
            }
        },
        "cfdi_40_tipos_relaciones": {
            "doctype": "SAT Relationship Type",
            "key": "id",
            "fields": {
                "code": "id",
                "description": "texto",
                "enabled": "1"
            }
        },
        "cfdi_40_productos_servicios": {
            "doctype": "SAT Product or Service Key",
            "key": "id",
            "fields": {
                "key": "id",
                "key_name": "texto",
                "description": "texto",
                "enabled": "1"
            }
        },
        "cfdi_40_codigos_postales": {
            "doctype": "SAT Postal Code",
            "key": "id",
            "fields": {
                "key": "id",
                "key_name": "id",
                "state": "estado",
                "municipality": "municipio",
                "locality": "localidad",
                "enabled": "1"
            }
        }
    }

    for table, mapping in catalogs_mapping.items():
        doctype = mapping["doctype"]
        
        if not frappe.db.exists("DocType", doctype):
            click.echo(f"Omitiendo la tabla '{table}' porque el DocType '{doctype}' no existe en el sistema.")
            continue

        try:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                click.echo(f"La tabla '{table}' no existe en el archivo SQLite. Omitiendo.")
                continue

            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # Obtener llaves existentes para no duplicar ni intentar insertar
            existing_keys = set(frappe.get_all(doctype, pluck="name"))
            
            to_insert = []
            now = frappe.utils.now()

            for row in rows:
                row_dict = dict(zip(columns, row))
                
                doc_key_val = row_dict.get(mapping["key"])
                if not doc_key_val:
                    continue
                
                doc_name = str(doc_key_val)
                
                if doc_name not in existing_keys:
                    doc_data = {
                        "doctype": doctype,
                        "name": doc_name,
                        "owner": "Administrator",
                        "modified_by": "Administrator",
                        "creation": now,
                        "modified": now
                    }
                    for doc_field, db_field in mapping["fields"].items():
                        if db_field == "1" or db_field == "0":
                            doc_data[doc_field] = int(db_field)
                        else:
                            val = row_dict.get(db_field)
                            doc_data[doc_field] = val if val else ""
                    to_insert.append(doc_data)

            if to_insert:
                click.echo(f"Insertando {len(to_insert)} nuevos registros en {doctype}...")
                
                # Bulk insert in chunks of 5000 to avoid query size limits
                chunk_size = 5000
                for i in range(0, len(to_insert), chunk_size):
                    chunk = to_insert[i:i+chunk_size]
                    try:
                        fields = [f for f in chunk[0].keys() if f != "doctype"]
                        values = [tuple(doc.get(f) for f in fields) for doc in chunk]
                        frappe.db.bulk_insert(doctype, fields=fields, values=values, ignore_duplicates=True)
                        frappe.db.commit()
                    except Exception as e:
                        click.echo(f"Advertencia: fallo en bulk insert para {doctype}, intentando uno a uno. Error: {e}")
                        frappe.db.rollback()
                        for doc_data in chunk:
                            try:
                                doc = frappe.get_doc(doc_data)
                                doc.db_insert()
                                frappe.db.commit()
                            except frappe.DuplicateEntryError:
                                frappe.db.rollback()
                            except Exception as inner_e:
                                frappe.db.rollback()

                click.echo(f"¡Importación de '{table}' a '{doctype}' completada exitosamente!")
            else:
                click.echo(f"El DocType '{doctype}' ya se encuentra actualizado (0 registros nuevos).")
            
        except sqlite3.Error as e:
            click.echo(f"Error al procesar la tabla {table}: {e}")

    conn.close()
    frappe.destroy()

commands = [sync_sat_catalogs]
