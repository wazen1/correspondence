// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Incoming Letter Register"] = {
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
            "options": "\nNew\nUnder Process\nWaiting\nCompleted\nArchived"
        },
        {
            "fieldname": "priority",
            "label": "Priority",
            "fieldtype": "Select",
            "options": "\nLow\nMedium\nHigh\nUrgent"
        }
    ]
};
