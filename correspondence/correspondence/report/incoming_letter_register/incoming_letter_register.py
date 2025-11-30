# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = [
		{"fieldname": "letter_number", "label": "Letter Number", "fieldtype": "Link", "options": "Incoming Letter", "width": 150},
		{"fieldname": "date_received", "label": "Date Received", "fieldtype": "Date", "width": 100},
		{"fieldname": "subject", "label": "Subject", "fieldtype": "Data", "width": 200},
		{"fieldname": "sender", "label": "Sender", "fieldtype": "Data", "width": 150},
		{"fieldname": "sender_organization", "label": "Organization", "fieldtype": "Link", "options": "Company", "width": 150},
		{"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
		{"fieldname": "priority", "label": "Priority", "fieldtype": "Data", "width": 100},
		{"fieldname": "assigned_to", "label": "Assigned To", "fieldtype": "Link", "options": "User", "width": 150}
	]
	
	conditions = ""
	if filters.get("from_date"):
		conditions += f" AND date_received >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" AND date_received <= '{filters.get('to_date')}'"
	if filters.get("status"):
		conditions += f" AND status = '{filters.get('status')}'"
	if filters.get("priority"):
		conditions += f" AND priority = '{filters.get('priority')}'"

	data = frappe.db.sql(f"""
		SELECT
			name as letter_number,
			date_received,
			subject,
			sender,
			sender_organization,
			status,
			priority,
			assigned_to
		FROM
			`tabIncoming Letter`
		WHERE
			docstatus < 2 {conditions}
		ORDER BY
			date_received DESC
	""", as_dict=1)

	return columns, data
