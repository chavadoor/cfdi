"""Copyright (c) 2024-2026, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe
from frappe import _
from satcfdi.cfdi import CFDI
from satcfdi.exceptions import ResponseError
from satcfdi.pacs import CancelReason, Environment
from satcfdi.pacs.finkok import Finkok


class FinkokClient:
	"""Client for Finkok PAC (WS Timbrado). Supports Sandbox and Production."""

	def __init__(self, username: str, password: str, use_sandbox: bool = True):
		self._username = username
		self._password = password
		self._environment = Environment.TEST if use_sandbox else Environment.PRODUCTION
		self._finkok = Finkok(
			username=username,
			password=password,
			environment=self._environment,
		)

	def _handle_response_error(self, e: Exception):
		msg = str(e)
		if hasattr(e, "message"):
			msg = getattr(e, "message", msg)
		frappe.throw(msg, title=_("CFDI Web Service Error"))

	def stamp(self, cfdi: CFDI) -> dict:
		"""Stamps the provided CFDI via Finkok.

		Args:
			cfdi (CFDI): The CFDI to be stamped.

		Returns:
			dict: {"xml": str} with the stamped CFDI XML.
		"""
		try:
			doc = self._finkok.stamp(cfdi)
		except ResponseError as e:
			self._handle_response_error(e)
		xml_str = doc.xml.decode("utf-8") if isinstance(doc.xml, bytes) else doc.xml
		return {"xml": xml_str}

	def cancel_cfdi(
		self,
		signing_certificate: str,
		cfdi: CFDI,
		reason: str,
		substitute_uuid: str,
	) -> dict:
		"""Cancels a CFDI using Finkok.

		Args:
			signing_certificate: Name of the Digital Signing Certificate DocType.
			cfdi: The CFDI to cancel.
			reason: Cancellation reason code ("01", "02", "03", "04").
			substitute_uuid: Optional UUID of substitute document.

		Returns:
			dict: {"acknowledgement": str} with the cancellation acknowledgement XML.
		"""
		csd = frappe.get_doc("Digital Signing Certificate", signing_certificate)
		signer = csd.signer
		if not signer:
			frappe.throw(_("Invalid or incomplete Digital Signing Certificate"))

		try:
			cancel_reason = CancelReason(reason)
		except ValueError:
			frappe.throw(
				_("Invalid cancellation reason: {0}. Use 01, 02, 03, or 04.").format(reason),
				title=_("CFDI Web Service Error"),
			)

		try:
			ack = self._finkok.cancel(
				cfdi=cfdi,
				reason=cancel_reason,
				substitution_id=substitute_uuid or None,
				signer=signer,
			)
		except ResponseError as e:
			self._handle_response_error(e)
		except ValueError as e:
			frappe.throw(str(e), title=_("CFDI Web Service Error"))

		acuse = getattr(ack, "acuse", None)
		if acuse is not None:
			ack_str = acuse.decode("utf-8") if isinstance(acuse, bytes) else str(acuse)
		else:
			ack_str = str(ack) if ack is not None else ""
		return {"acknowledgement": ack_str}

	def get_status(self, cfdi: CFDI):
		"""Finkok does not expose a status query like TISP. Returns a placeholder status.

		Callers (e.g. Check cancellation status) should hide or disable this when
		using Finkok, or implement SAT public status query later.
		"""
		frappe.throw(
			_("Status query is not supported for Finkok. Use the SAT verification portal."),
			title=_("CFDI Web Service Error"),
		)

	def get_subscription(self) -> dict:
		"""Finkok does not use credits. Returns a compatible dict for UI."""
		return {"available_credits": 0, "has_subscription": True}
