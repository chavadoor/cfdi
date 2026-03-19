"""Copyright (c) 2024-2026, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe

from . import finkok_client


def get_ws_client():
	"""Retrieves a stamping client based on the current CFDI Stamping Settings.

	Returns:
		FinkokClient: Configured for Finkok (Sandbox or Production via test_mode).
	"""
	settings = frappe.get_single("CFDI Stamping Settings")
	return finkok_client.FinkokClient(
		username=settings.api_key or "",
		password=settings.get_secret() or "",
		use_sandbox=bool(settings.test_mode),
	)


__all__ = ["get_ws_client"]
