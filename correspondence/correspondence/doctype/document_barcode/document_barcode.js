// Copyright (c) 2025, ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document Barcode', {
    refresh: function (frm) {
        if (!frm.is_new() && !frm.doc.barcode_image) {
            frm.add_custom_button(__('Generate Barcode'), function () {
                frm.trigger('generate_barcode');
            });
        }
    },

    generate_barcode: function (frm) {
        frappe.call({
            method: 'correspondence.correspondence.utils.barcode_qr.generate_barcode_api',
            args: {
                doctype: frm.doc.document_type,
                docname: frm.doc.document_name,
                barcode_type: frm.doc.barcode_type || 'code128'
            },
            callback: function (r) {
                if (r.message && r.message.success) {
                    frappe.msgprint(__('Barcode generated successfully'));
                    frm.reload_doc();
                }
            }
        });
    }
});
