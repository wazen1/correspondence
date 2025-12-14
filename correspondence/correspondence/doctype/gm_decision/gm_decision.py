# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, getdate

class GMDecision(Document):
	def validate(self):
		"""Validate the document"""
		# Auto-update completion date when status is Implemented
		if self.status == "Implemented" and not self.completion_date:
			self.completion_date = getdate()
	
	def on_submit(self):
		"""On submit"""
		# Update status to Issued
		if self.status == "Draft":
			self.status = "Issued"
			self.save()
		
		# Send notification to responsible person
		self.send_notification()
	
	def send_notification(self):
		"""Send notification to responsible person"""
		if not self.responsible_person:
			return
		
		try:
			# Create notification
			notification = frappe.new_doc("Notification Log")
			notification.subject = f"تكليف بقرار المدير العام: {self.subject}"
			notification.for_user = self.responsible_person
			notification.type = "Alert"
			notification.document_type = self.doctype
			notification.document_name = self.name
			notification.email_content = f"""
				<div style="direction: rtl; text-align: right; font-family: Tahoma, Arial, sans-serif;">
					<p>تم تكليفك بتنفيذ قرار المدير العام التالي:</p>
					<ul>
						<li><strong>الموضوع:</strong> {self.subject}</li>
						<li><strong>تاريخ القرار:</strong> {self.decision_date}</li>
						<li><strong>الأولوية:</strong> {self.priority}</li>
						<li><strong>الموعد النهائي:</strong> {self.implementation_deadline or 'غير محدد'}</li>
					</ul>
					<p>الرجاء المراجعة والتنفيذ.</p>
				</div>
			"""
			notification.insert(ignore_permissions=True)
			
			# Send email
			frappe.sendmail(
				recipients=[self.responsible_person],
				subject=f"تكليف بقرار المدير العام: {self.subject}",
				message=notification.email_content,
				reference_doctype=self.doctype,
				reference_name=self.name
			)
		except Exception as e:
			frappe.log_error(f"Sending notification failed: {str(e)}")


@frappe.whitelist()
def mark_as_implemented(decision_name):
	"""Mark a decision as implemented"""
	try:
		doc = frappe.get_doc("GM Decision", decision_name)
		doc.status = "Implemented"
		doc.completion_date = getdate()
		doc.save(ignore_permissions=True)
		
		return {"success": True, "message": "Decision marked as implemented"}
	except Exception as e:
		frappe.log_error(f"Mark as implemented failed: {str(e)}")
		return {"success": False, "error": str(e)}
