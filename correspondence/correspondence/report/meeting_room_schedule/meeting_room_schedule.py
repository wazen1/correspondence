# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"fieldname": "booking_id", "label": _("Booking ID"), "fieldtype": "Link", "options": "Meeting Room Booking", "width": 150},
		{"fieldname": "meeting_room", "label": _("Meeting Room"), "fieldtype": "Link", "options": "Meeting Room", "width": 150},
		{"fieldname": "booking_date", "label": _("Date"), "fieldtype": "Date", "width": 100},
		{"fieldname": "start_time", "label": _("Start Time"), "fieldtype": "Time", "width": 100},
		{"fieldname": "end_time", "label": _("End Time"), "fieldtype": "Time", "width": 100},
		{"fieldname": "duration", "label": _("Duration (hrs)"), "fieldtype": "Float", "width": 100},
		{"fieldname": "meeting_title", "label": _("Meeting Title"), "fieldtype": "Data", "width": 200},
		{"fieldname": "booked_by", "label": _("Booked By"), "fieldtype": "Link", "options": "User", "width": 150},
		{"fieldname": "department", "label": _("Department"), "fieldtype": "Link", "options": "Department", "width": 150},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
		{"fieldname": "number_of_attendees", "label": _("Attendees"), "fieldtype": "Int", "width": 80}
	]
	
	conditions = "WHERE docstatus < 2"
	
	if filters.get("from_date"):
		conditions += f" AND booking_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" AND booking_date <= '{filters.get('to_date')}'"
	if filters.get("meeting_room"):
		conditions += f" AND meeting_room = '{filters.get('meeting_room')}'"
	if filters.get("status"):
		conditions += f" AND status = '{filters.get('status')}'"
	if filters.get("department"):
		conditions += f" AND department = '{filters.get('department')}'"

	data = frappe.db.sql(f"""
		SELECT
			name as booking_id,
			meeting_room,
			booking_date,
			start_time,
			end_time,
			TIMESTAMPDIFF(MINUTE, 
				CONCAT(booking_date, ' ', start_time), 
				CONCAT(booking_date, ' ', end_time)
			) / 60.0 as duration,
			meeting_title,
			booked_by,
			department,
			status,
			number_of_attendees
		FROM
			`tabMeeting Room Booking`
		{conditions}
		ORDER BY
			booking_date DESC, start_time ASC
	""", as_dict=1)

	return columns, data
