// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meeting Room Booking', {
    refresh: function (frm) {
        // Add custom buttons based on status
        if (frm.doc.docstatus === 1) {
            if (frm.doc.status === 'Pending' && frappe.user.has_role(['Correspondence Manager', 'System Manager'])) {
                frm.add_custom_button(__('Approve'), function () {
                    frm.set_value('status', 'Approved');
                    frm.set_value('approved_by', frappe.session.user);
                    frm.set_value('approval_date', frappe.datetime.now_datetime());
                    frm.save();
                }, __('Actions'));

                frm.add_custom_button(__('Reject'), function () {
                    frappe.prompt([
                        {
                            fieldname: 'rejection_reason',
                            fieldtype: 'Small Text',
                            label: __('Rejection Reason'),
                            reqd: 1
                        }
                    ], function (values) {
                        frm.set_value('status', 'Rejected');
                        frm.set_value('rejection_reason', values.rejection_reason);
                        frm.save();
                    }, __('Reject Booking'));
                }, __('Actions'));
            }

            if (frm.doc.status === 'Approved') {
                frm.add_custom_button(__('Mark as Completed'), function () {
                    frm.set_value('status', 'Completed');
                    frm.save();
                }, __('Actions'));
            }
        }

        // Add calendar view button
        if (!frm.is_new()) {
            frm.add_custom_button(__('View Calendar'), function () {
                frappe.set_route('List', 'Meeting Room Booking', 'Calendar');
            });
        }

        // Set color indicator based on status
        if (frm.doc.status) {
            frm.page.set_indicator(frm.doc.status, {
                'Pending': 'orange',
                'Approved': 'green',
                'Rejected': 'red',
                'Completed': 'blue',
                'Cancelled': 'gray'
            }[frm.doc.status]);
        }
    },

    meeting_room: function (frm) {
        if (frm.doc.meeting_room) {
            // Fetch room details
            frappe.db.get_doc('Meeting Room', frm.doc.meeting_room).then(room => {
                // Show room capacity
                if (room.capacity) {
                    frm.set_df_property('number_of_attendees', 'description',
                        __('Room capacity: {0} people', [room.capacity]));
                }

                // Check facilities
                let facilities = [];
                if (room.has_projector) facilities.push(__('Projector'));
                if (room.has_whiteboard) facilities.push(__('Whiteboard'));
                if (room.has_video_conferencing) facilities.push(__('Video Conferencing'));
                if (room.has_audio_system) facilities.push(__('Audio System'));
                if (room.has_wifi) facilities.push(__('WiFi'));
                if (room.has_air_conditioning) facilities.push(__('Air Conditioning'));

                if (facilities.length > 0) {
                    frm.set_df_property('meeting_room', 'description',
                        __('Available facilities: {0}', [facilities.join(', ')]));
                }
            });
        }
    },

    booking_date: function (frm) {
        check_availability(frm);
    },

    start_time: function (frm) {
        check_availability(frm);
    },

    end_time: function (frm) {
        check_availability(frm);
    }
});

function check_availability(frm) {
    if (frm.doc.meeting_room && frm.doc.booking_date && frm.doc.start_time && frm.doc.end_time) {
        frappe.call({
            method: 'correspondence.correspondence.doctype.meeting_room_booking.meeting_room_booking.check_room_availability',
            args: {
                room: frm.doc.meeting_room,
                date: frm.doc.booking_date,
                start_time: frm.doc.start_time,
                end_time: frm.doc.end_time,
                current_booking: frm.doc.name
            },
            callback: function (r) {
                if (r.message && r.message.available === false) {
                    frappe.msgprint({
                        title: __('Room Not Available'),
                        indicator: 'red',
                        message: __('This room is already booked for the selected time slot.')
                    });
                }
            }
        });
    }
}
