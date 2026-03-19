import frappe


def check_app_permission():
    if frappe.session.user == "Administrator":
        return True

    roles = set(frappe.get_roles())
    allowed_roles = {
        "System Manager",
        "Accounts Manager",
        "Accounts User",
        "Sales Manager",
        "Sales User",
    }

    if roles.intersection(allowed_roles):
        return True

    # Fallback: show the app when the user can access the core module settings doctype.
    return frappe.has_permission("Digital Signing Certificate", ptype="read")
