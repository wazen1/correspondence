// Client Script for Document Transmittal

frappe.ui.form.on('Document Transmittal', {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1 && frm.doc.status === 'Issued') {
            // Check if current user is the recipient
            if (frm.doc.recipient === frappe.session.user || frappe.user.has_role('System Manager')) {
                if (frm.doc.acknowledgement_required && !frm.doc.date_acknowledged) {
                    frm.add_custom_button(__('Acknowledge Receipt'), function () {
                        acknowledge_transmittal(frm);
                    }, __('Actions'));

                    frm.page.set_indicator('Waiting for Acknowledgement', 'orange');
                }
            }
        }
    }
});

function acknowledge_transmittal(frm) {
    frappe.confirm(
        __('Are you sure you want to acknowledge receipt of these documents?'),
        function () {
            frappe.call({
                method: 'correspondence.correspondence.doctype.document_transmittal.document_transmittal.acknowledge_transmittal',
                args: {
                    transmittal_name: frm.doc.name
                },
                callback: function (r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('Transmittal Acknowledged'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}
