// Copyright (c) 2024, TI Sin Problemas and contributors
// For license information, please see license.txt

frappe.ui.form.on("CFDI Stamping Settings", {
  refresh(frm) {
    frm.set_df_property("test_mode", "label", __("Usar Sandbox Finkok"));
    frm.set_df_property("test_mode", "description", __("Use Finkok sandbox (test credentials). Uncheck for production."));
  },
});

frappe.ui.form.on("CFDI PDF Template", {
  print_example(frm, cdt, cdn) {
    if (cdn.startsWith("new")) {
      frappe.throw(__("Please save the CFDI PDF Template first"));
    }
    const url = `/api/method/erpnext_mexico_compliance.erpnext_mexico_compliance.doctype.cfdi_pdf_template.cfdi_pdf_template.print_example?docname=${cdn}`;
    window.open(url);
  },
  async load_css_sample(frm, cdt, cdn) {
    const { message } = await frappe.call({
      method: "get_sample_css",
      doc: frappe.get_doc(cdt, cdn),
    });
    frappe.model.set_value(cdt, cdn, "css_styles", message);
  },
  async load_content_sample(frm, cdt, cdn) {
    const { message } = await frappe.call({
      method: "get_sample_content",
      doc: frappe.get_doc(cdt, cdn),
    });
    frappe.model.set_value(cdt, cdn, "content_html", message);
  },
});
