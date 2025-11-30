# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime

class DocumentTransmittal(Document):
	def validate(self):
		if self.acknowledgement_required and self.status == "Acknowledged" and not self.date_acknowledged:
			self.date_acknowledged = now_datetime()

	def on_submit(self):
		self.status = "Issued"
		self.send_transmittal_email()

	def on_cancel(self):
		self.status = "Cancelled"

	def send_transmittal_email(self):
		"""Send email to recipient with transmittal details"""
		if not self.recipient:
			return

		recipient_email = frappe.db.get_value("User", self.recipient, "email")
		if not recipient_email:
			return

		subject = f"Document Transmittal: {self.name}"
		
		# Build HTML table of items
		items_html = """
		<table class="table table-bordered" style="width: 100%; border-collapse: collapse;">
			<thead>
				<tr style="background-color: #f0f0f0;">
					<th style="padding: 8px; border: 1px solid #ddd;">Document</th>
					<th style="padding: 8px; border: 1px solid #ddd;">Revision</th>
					<th style="padding: 8px; border: 1px solid #ddd;">Title</th>
					<th style="padding: 8px; border: 1px solid #ddd;">Remarks</th>
				</tr>
			</thead>
			<tbody>
		"""
		
		for item in self.transmittal_items:
			items_html += f"""
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;">{item.document_name}</td>
					<td style="padding: 8px; border: 1px solid #ddd;">{item.revision or '-'}</td>
					<td style="padding: 8px; border: 1px solid #ddd;">{item.title or ''}</td>
					<td style="padding: 8px; border: 1px solid #ddd;">{item.remarks or ''}</td>
				</tr>
			"""
		
		items_html += "</tbody></table>"

		message = f"""
		<p>Dear {self.recipient},</p>
		<p>Please find attached the following documents for <b>{self.reason_for_issue}</b>.</p>
		<p><b>Transmittal No:</b> {self.name}<br>
		<b>Date:</b> {self.transmittal_date}</p>
		
		{items_html}
		
		<p>{self.message or ''}</p>
		"""

		if self.acknowledgement_required:
			message += f"""
			<p><b>Please acknowledge receipt of this transmittal.</b></p>
			<p><a href="{frappe.utils.get_url()}/app/document-transmittal/{self.name}" class="btn btn-primary">View & Acknowledge</a></p>
			"""

		frappe.sendmail(
			recipients=[recipient_email],
			subject=subject,
			message=message,
			reference_doctype=self.doctype,
			reference_name=self.name
		)
		
		frappe.msgprint(f"Transmittal sent to {recipient_email}")

@frappe.whitelist()
def acknowledge_transmittal(transmittal_name):
	"""API to acknowledge a transmittal"""
	doc = frappe.get_doc("Document Transmittal", transmittal_name)
	if doc.status == "Issued":
		doc.status = "Acknowledged"
		doc.date_acknowledged = now_datetime()
		doc.save(ignore_permissions=True)
		return {"success": True}
	return {"success": False, "error": "Transmittal is not in Issued state"}
