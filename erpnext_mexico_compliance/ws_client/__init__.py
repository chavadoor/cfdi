"""Copyright (c) 2024-2026, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe

from . import client
from . import finkok_client


def get_ws_client():
	"""Retrieves a stamping client based on the current CFDI Stamping Settings.

	Returns:
		APIClient or FinkokClient: Configured for TI Sin Problemas or Finkok (Sandbox/Production).
	"""
	settings = frappe.get_single("CFDI Stamping Settings")
	if getattr(settings, "stamping_provider", None) == "Finkok":
		return finkok_client.FinkokClient(
			username=settings.api_key or "",
			password=settings.get_secret() or "",
			use_sandbox=bool(settings.test_mode),
		)
	return client.APIClient(
		url=settings.api_url,
		api_key=settings.api_key,
		api_secret=settings.get_secret(),
	)


__all__ = ["get_ws_client"]
