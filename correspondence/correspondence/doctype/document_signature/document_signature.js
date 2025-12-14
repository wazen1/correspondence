// Copyright (c) 2025, ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document Signature', {
    refresh: function (frm) {
        if (!frm.is_new() && !frm.doc.signature) {
            frm.add_custom_button(__('Sign Document'), function () {
                frm.trigger('sign_document');
            });
        }
    },

    sign_document: function (frm) {
        frappe.call({
            method: 'correspondence.correspondence.utils.digital_signature.sign_document_api',
            args: {
                doctype: frm.doc.document_type,
                docname: frm.doc.document_name
            },
            callback: function (r) {
                if (r.message && r.message.success) {
                    frappe.msgprint(__('Document signed successfully'));
                    frm.reload_doc();
                }
            }
        });
    }
});
