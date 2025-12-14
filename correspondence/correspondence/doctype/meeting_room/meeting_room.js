// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meeting Room', {
    refresh: function (frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('View Bookings'), function () {
                frappe.set_route('List', 'Meeting Room Booking', {
                    'meeting_room': frm.doc.name
                });
            });
        }
    }
});
