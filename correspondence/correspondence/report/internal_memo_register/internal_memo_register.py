# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = [
		{"fieldname": "reference_number", "label": "Reference Number", "fieldtype": "Link", "options": "Internal Memo", "width": 150},
		{"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 100},
		{"fieldname": "subject", "label": "Subject", "fieldtype": "Data", "width": 200},
		{"fieldname": "sender", "label": "Sender", "fieldtype": "Link", "options": "User", "width": 150},
		{"fieldname": "recipient_type", "label": "Recipient Type", "fieldtype": "Data", "width": 120},
		{"fieldname": "recipient_department", "label": "Recipient Dept", "fieldtype": "Link", "options": "Department", "width": 150},
		{"fieldname": "recipient_user", "label": "Recipient User", "fieldtype": "Link", "options": "User", "width": 150},
		{"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
		{"fieldname": "priority", "label": "Priority", "fieldtype": "Data", "width": 100}
	]
	
	conditions = ""
	if filters.get("from_date"):
		conditions += f" AND date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" AND date <= '{filters.get('to_date')}'"
	if filters.get("status"):
		conditions += f" AND status = '{filters.get('status')}'"
	if filters.get("priority"):
		conditions += f" AND priority = '{filters.get('priority')}'"

	data = frappe.db.sql(f"""
		SELECT
			name as reference_number,
			date,
			subject,
			sender,
			recipient_type,
			recipient_department,
			recipient_user,
			status,
			priority
		FROM
			`tabInternal Memo`
		WHERE
			docstatus < 2 {conditions}
		ORDER BY
			date DESC
	""", as_dict=1)

	return columns, data
