# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def check_room_availability(room, date, start_time, end_time, current_booking=None):
	"""Check if a meeting room is available for the given time slot"""
	
	overlapping_bookings = frappe.db.sql("""
		SELECT name, meeting_title, start_time, end_time, booked_by
		FROM `tabMeeting Room Booking`
		WHERE meeting_room = %(room)s
			AND booking_date = %(date)s
			AND name != %(current_booking)s
			AND status NOT IN ('Rejected', 'Cancelled')
			AND docstatus < 2
			AND (
				(start_time < %(end_time)s AND end_time > %(start_time)s)
			)
	""", {
		'room': room,
		'date': date,
		'start_time': start_time,
		'end_time': end_time,
		'current_booking': current_booking or 'new'
	}, as_dict=True)
	
	return {
		'available': len(overlapping_bookings) == 0,
		'conflicts': overlapping_bookings
	}

@frappe.whitelist()
def get_room_schedule(room, date):
	"""Get all bookings for a room on a specific date"""
	
	bookings = frappe.db.sql("""
		SELECT name, meeting_title, start_time, end_time, status, booked_by
		FROM `tabMeeting Room Booking`
		WHERE meeting_room = %(room)s
			AND booking_date = %(date)s
			AND status NOT IN ('Rejected', 'Cancelled')
			AND docstatus < 2
		ORDER BY start_time
	""", {
		'room': room,
		'date': date
	}, as_dict=True)
	
	return bookings
