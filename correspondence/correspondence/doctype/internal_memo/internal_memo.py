# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class InternalMemo(Document):
	def before_insert(self):
		# Generate Reference Number
		# Format: REF/Year/Sequence (e.g., REF/2025/0001)
		if not self.reference_number:
			self.reference_number = self.generate_reference_number()
			
	def generate_reference_number(self):
		"""Generate a unique reference number"""
		from frappe.model.naming import make_autoname
		return make_autoname("REF/.YYYY./.#####")

	def on_submit(self):
		self.status = "Sent"
		self.send_notification()

	def send_notification(self):
		"""Send notification to recipient"""
		recipient = self.recipient_user
		
		if self.recipient_type == "Department":
			# Try to get department head safely
			try:
				if frappe.db.has_column("Department", "department_head"):
					dept_head = frappe.db.get_value("Department", self.recipient_department, "department_head")
					if dept_head:
						recipient = dept_head
			except Exception:
				# Field might not exist or other error, ignore
				pass
		
		if recipient:
			frappe.sendmail(
				recipients=[recipient],
				subject=f"New Internal Memo: {self.subject}",
				message=f"""
					<div style="direction: rtl; text-align: right; font-family: Tahoma, Arial, sans-serif;">
						<p>لديك مذكرة داخلية جديدة:</p>
						<p><b>المرسل:</b> {self.sender}</p>
						<p><b>الموضوع:</b> {self.subject}</p>
						<p><b>الرقم الإشاري:</b> {self.reference_number}</p>
						<p><a href="{frappe.utils.get_url_to_form(self.doctype, self.name)}">عرض المذكرة</a></p>
					</div>
				"""
			)

@frappe.whitelist()
def generate_word_document(memo_name):
	"""Generate a Word document from the memo"""
	try:
		doc = frappe.get_doc("Internal Memo", memo_name)
		
		# Create HTML content for the Word document
		# We use a simple HTML structure that Word can open
		html_content = f"""
		<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
		<head>
			<meta charset="utf-8">
			<title>{doc.subject}</title>
			<style>
				body {{ font-family: 'Arial', sans-serif; direction: rtl; text-align: right; }}
				.header {{ text-align: center; margin-bottom: 30px; }}
				.meta {{ margin-bottom: 20px; }}
				.content {{ line-height: 1.6; }}
				.footer {{ margin-top: 50px; }}
			</style>
		</head>
		<body>
			<div class="header">
				<h2>مذكرة داخلية</h2>
				<h3>Internal Memo</h3>
			</div>
			
			<div class="meta">
				<p><b>الرقم الإشاري:</b> {doc.reference_number}</p>
				<p><b>التاريخ:</b> {doc.date}</p>
				<p><b>من:</b> {doc.sender}</p>
				<p><b>إلى:</b> {doc.recipient_department or doc.recipient_user}</p>
				<p><b>الموضوع:</b> {doc.subject}</p>
			</div>
			
			<hr>
			
			<div class="content">
				{doc.content}
			</div>
			
			<div class="footer">
				<p><b>التوقيع:</b> ____________________</p>
			</div>
		</body>
		</html>
		"""
		
		# Encode to base64
		import base64
		b64_content = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
		
		return {
			"filename": f"{doc.name}.doc",
			"content": b64_content
		}
		
	except Exception as e:
		frappe.log_error(f"Word generation failed: {str(e)}")
		return None
