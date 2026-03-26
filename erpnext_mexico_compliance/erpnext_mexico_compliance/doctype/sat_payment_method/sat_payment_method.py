import frappe
from frappe.model.document import Document
from frappe import _

class SATPaymentMethod(Document):
    def validate(self):
        # Exclusividad: La Forma de Pago (01, 03, etc) DEBE ser numérica o 99.
        # No permitimos PUE ni PPD aquí.
        if not self.key.isdigit() and self.key not in ["99"]:
            frappe.throw(_("Código '{0}' inválido para Forma de Pago. Este catálogo solo acepta códigos numéricos del SAT (01, 03, 99, etc).").format(self.key))
