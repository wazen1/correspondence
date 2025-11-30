import frappe
from frappe.utils import getdate, add_days

def notify_on_assignment(doc, method):
	"""
	Notify the user when they are assigned to an Incoming Letter.
	"""
	if doc.doctype == "Incoming Letter" and doc.assigned_to:
		# Check if assignment changed
		# In on_update, we check against the previous state
		if doc.has_value_changed("assigned_to") or (not doc.get_doc_before_save() and doc.assigned_to):
			subject = f"Assignment: {doc.name} - {doc.subject}"
			message = f"""
				<p>You have been assigned to the following Incoming Letter:</p>
				<p><b>Letter Number:</b> {doc.name}</p>
				<p><b>Subject:</b> {doc.subject}</p>
				<p><b>Priority:</b> {doc.priority}</p>
				<p><a href="{frappe.utils.get_url_to_form(doc.doctype, doc.name)}">View Letter</a></p>
			"""
			
			# Send System Notification
			create_system_notification(doc, doc.assigned_to, subject)
			
			# Send Email
			frappe.sendmail(
				recipients=[doc.assigned_to],
				subject=subject,
				message=message
			)

def notify_on_status_change(doc, method):
	"""
	Notify relevant users when status changes.
	"""
	if doc.has_value_changed("status"):
		subject = f"Status Update: {doc.name} is now {doc.status}"
		
		# Notify Owner
		if doc.owner != frappe.session.user:
			create_system_notification(doc, doc.owner, subject)

def check_daily_follow_ups():
	"""
	Check for follow-ups due today.
	"""
	today = getdate()
	
	# Check Incoming Letters
	incoming_letters = frappe.get_all("Incoming Letter", fields=["name", "subject", "assigned_to"])
	for letter in incoming_letters:
		doc = frappe.get_doc("Incoming Letter", letter.name)
		for follow_up in doc.follow_ups:
			if follow_up.status == "Pending" and follow_up.next_follow_up_date and getdate(follow_up.next_follow_up_date) <= today:
				subject = f"Follow Up Due: {doc.name}"
				recipient = follow_up.followed_up_by or doc.assigned_to or doc.owner
				
				create_system_notification(doc, recipient, subject)
				
				# Send Email for Overdue
				if getdate(follow_up.next_follow_up_date) < today:
					frappe.sendmail(
						recipients=[recipient],
						subject=f"OVERDUE: {subject}",
						message=f"Follow up for letter {doc.name} was due on {follow_up.next_follow_up_date}."
					)

def create_system_notification(doc, recipient, subject):
	if not recipient:
		return
		
	notification = frappe.new_doc("Notification Log")
	notification.subject = subject
	notification.for_user = recipient
	notification.document_type = doc.doctype
	notification.document_name = doc.name
	notification.insert(ignore_permissions=True)
