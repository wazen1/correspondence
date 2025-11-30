from frappe import _

def get_data(data=None):
	return {
		"non_standard_fieldnames": {
			"GM Decision": "related_outgoing_letter"
		},
		"transactions": [
			{
				"label": _("Reference"),
				"items": ["GM Decision"]
			}
		]
	}
