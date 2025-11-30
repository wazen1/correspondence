// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Outgoing Letter Register"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": "\nDraft\nUnder Review\nApproved\nSent\nDelivered\nArchived"
        },
        {
            "fieldname": "priority",
            "label": "Priority",
            "fieldtype": "Select",
            "options": "\nLow\nMedium\nHigh\nUrgent"
        }
    ]
};
