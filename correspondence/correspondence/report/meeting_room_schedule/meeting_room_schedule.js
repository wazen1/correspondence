// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Meeting Room Schedule"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -7),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), 30),
            "reqd": 1
        },
        {
            "fieldname": "meeting_room",
            "label": __("Meeting Room"),
            "fieldtype": "Link",
            "options": "Meeting Room"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nPending\nApproved\nRejected\nCompleted\nCancelled"
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department"
        }
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname == "status") {
            if (value && value.includes("Approved")) {
                value = `<span class="indicator-pill green">${data.status}</span>`;
            } else if (value && value.includes("Pending")) {
                value = `<span class="indicator-pill orange">${data.status}</span>`;
            } else if (value && value.includes("Rejected")) {
                value = `<span class="indicator-pill red">${data.status}</span>`;
            } else if (value && value.includes("Completed")) {
                value = `<span class="indicator-pill blue">${data.status}</span>`;
            } else if (value && value.includes("Cancelled")) {
                value = `<span class="indicator-pill gray">${data.status}</span>`;
            }
        }

        return value;
    }
};
