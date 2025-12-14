// Copyright (c) 2025, ERP Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Internal Memo', {
    refresh: function (frm) {
        if (!frm.is_new()) {
            // Add "Export to Word" button
            frm.add_custom_button(__('Export to Word'), function () {
                frappe.call({
                    method: 'correspondence.correspondence.doctype.internal_memo.internal_memo.generate_word_document',
                    args: {
                        memo_name: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            // Download the file
                            download_file(r.message.filename, r.message.content);
                        }
                    }
                });
            }, __('Actions'));
        }
    },

    setup: function (frm) {
        // Set default sender to current user
        if (frm.is_new()) {
            frm.set_value('sender', frappe.session.user);
        }
    }
});

function download_file(filename, content) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:application/msword;base64,' + content);
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}
