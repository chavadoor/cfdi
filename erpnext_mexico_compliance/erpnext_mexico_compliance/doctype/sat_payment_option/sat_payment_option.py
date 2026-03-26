import frappe
from frappe.model.document import Document
from frappe import _

class SATPaymentOption(Document):
    def validate(self):
        # Exclusividad: El Método de Pago DEBE ser PUE o PPD.
        # No permitimos códigos numéricos aquí.
        if self.key.upper() not in ["PUE", "PPD"]:
            frappe.throw(_("Código '{0}' inválido para Método de Pago. Este catálogo solo acepta 'PUE' o 'PPD'.").format(self.key))
