"""Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe
from frappe import _
from frappe.model.document import Document


class CFDIStampingSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.default_csd.default_csd import (
			DefaultCSD,
		)

		api_key: DF.Data | None
		api_secret: DF.Password | None
		default_csds: DF.Table[DefaultCSD]
		stamp_on_submit: DF.Check
		test_mode: DF.Check
	# end: auto-generated types

	def get_secret(self) -> str:
		"""Retrieves the API secret.

		Returns:
			str: The API secret.
		"""
		return self.get_password("api_secret")

	def get_token(self) -> str:
		"""Retrieves the API token.

		Returns:
			str: The API token.
		"""
		return f"{self.api_key}:{self.get_secret()}"

	def set_field_from_site_config(self, field):
		"""Sets a field from the site config if it is set.

		Args:
			field (str): The name of the field to set.
		"""
		value = frappe.conf.get(f"cfdi_{field}")
		doc_field = self.meta.get_field(field)

		current_value = getattr(self, field)
		if doc_field.fieldtype == "Password" and current_value:
			current_value = self.get_password(field)

		if value and current_value != value:
			msg = _(
				"The value of {0} is set from the site config and cannot be changed here. Only the site admin can change it."
			).format(_(doc_field.label))
			frappe.msgprint(msg)
			setattr(self, field, value)

	def before_validate(self):
		self.set_field_from_site_config("api_key")
		self.set_field_from_site_config("api_secret")
		self.set_field_from_site_config("test_mode")

	@property
	def api_url(self):
		"""Determines the URL of the CFDI Web Service API.

		For Finkok, URL is resolved by the PAC client (Sandbox/Production).
		Returns empty string for Finkok.
		"""
		return ""
