from frappe import _

def get_data(data=None):
	return {
		"non_standard_fieldnames": {
			"Outgoing Letter": "related_incoming_letter",
			"GM Decision": "related_incoming_letter"
		},
		"transactions": [
			{
				"label": _("Reference"),
				"items": ["Outgoing Letter", "GM Decision"]
			}
		]
	}
