// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('GM Decision', {
    refresh: function (frm) {
        // Add custom buttons
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            // Mark as Implemented button
            if (frm.doc.status !== 'Implemented' && frm.doc.status !== 'Cancelled') {
                frm.add_custom_button(__('Mark as Implemented'), function () {
                    mark_as_implemented(frm);
                }, __('Actions'));
            }

            // Create Outgoing Letter button
            frm.add_custom_button(__('Create Outgoing Letter'), function () {
                create_outgoing_letter(frm);
            }, __('Create'));
        }

        // Set color indicator based on status
        set_status_indicator(frm);
    },

    status: function (frm) {
        set_status_indicator(frm);
    },

    related_incoming_letter: function (frm) {
        // Auto-fill subject from incoming letter
        if (frm.doc.related_incoming_letter && !frm.doc.subject) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Incoming Letter',
                    filters: { name: frm.doc.related_incoming_letter },
                    fieldname: 'subject'
                },
                callback: function (r) {
                    if (r.message && r.message.subject) {
                        frm.set_value('subject', 'Decision: ' + r.message.subject);
                    }
                }
            });
        }
    }
});

function set_status_indicator(frm) {
    let color_map = {
        'Draft': 'orange',
        'Issued': 'blue',
        'Implemented': 'green',
        'Cancelled': 'red'
    };

    frm.page.set_indicator(frm.doc.status, color_map[frm.doc.status] || 'gray');
}

function mark_as_implemented(frm) {
    frappe.confirm(
        __('Are you sure you want to mark this decision as implemented?'),
        function () {
            frappe.call({
                method: 'correspondence.correspondence.doctype.gm_decision.gm_decision.mark_as_implemented',
                args: {
                    decision_name: frm.docname
                },
                callback: function (r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('Decision marked as implemented'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    } else {
                        frappe.msgprint(__('Failed to mark as implemented: ') + (r.message.error || 'Unknown error'));
                    }
                }
            });
        }
    );
}

function create_outgoing_letter(frm) {
    frappe.route_options = {
        'related_incoming_letter': frm.doc.related_incoming_letter,
        'subject': 'Re: ' + frm.doc.subject
    };
    frappe.new_doc('Outgoing Letter');
}
