// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer File', {
    refresh: function (frm) {
        // Add custom buttons
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            // Archive button
            if (frm.doc.status !== 'Archived') {
                frm.add_custom_button(__('Archive File'), function () {
                    archive_file(frm);
                }, __('Actions'));
            }

            // Print File Summary
            frm.add_custom_button(__('Print File Summary'), function () {
                frm.print_doc();
            }, __('Actions'));
        }

        // Set indicator based on status
        set_status_indicator(frm);
    },

    file_type: function (frm) {
        // Clear fields when file type changes
        if (frm.doc.file_type === 'Individual') {
            frm.set_value('company_name', '');
            frm.set_value('commercial_registration', '');
            frm.set_value('tax_id', '');
        } else {
            frm.set_value('customer_name', '');
            frm.set_value('passport_number', '');
            frm.set_value('national_id', '');
        }
    },

    status: function (frm) {
        set_status_indicator(frm);
    }
});

function set_status_indicator(frm) {
    let color_map = {
        'Active': 'green',
        'Inactive': 'orange',
        'Closed': 'red',
        'Archived': 'gray'
    };

    frm.page.set_indicator(frm.doc.status, color_map[frm.doc.status] || 'blue');
}

function archive_file(frm) {
    frappe.confirm(
        __('Are you sure you want to archive this customer file?'),
        function () {
            frm.set_value('status', 'Archived');
            frm.save();

            frappe.show_alert({
                message: __('File archived successfully'),
                indicator: 'green'
            });
        }
    );
}
