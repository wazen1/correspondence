// Copyright (c) 2025, ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document QR Code', {
    refresh: function (frm) {
        if (!frm.is_new() && !frm.doc.qr_image) {
            frm.add_custom_button(__('Generate QR Code'), function () {
                frm.trigger('generate_qr_code');
            });
        }
    },

    generate_qr_code: function (frm) {
        frappe.call({
            method: 'correspondence.correspondence.utils.barcode_qr.generate_qr_code_api',
            args: {
                doctype: frm.doc.document_type,
                docname: frm.doc.document_name,
                include_metadata: 1
            },
            callback: function (r) {
                if (r.message && r.message.success) {
                    frappe.msgprint(__('QR Code generated successfully'));
                    frm.reload_doc();
                }
            }
        });
    }
});
