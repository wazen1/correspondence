# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class CustomerFile(Document):
	def autoname(self):
		"""Generate file number based on file type"""
		if self.file_type == "Individual":
			self.name = make_autoname("CF-IND-.YYYY.-.#####")
		else:
			self.name = make_autoname("CF-COM-.YYYY.-.#####")
		
		self.file_number = self.name
	
	def validate(self):
		"""Validate the document"""
		# Ensure either customer_name or company_name is filled
		if self.file_type == "Individual" and not self.customer_name:
			frappe.throw("Customer Name is required for Individual files")
		
		if self.file_type == "Company" and not self.company_name:
			frappe.throw("Company Name is required for Company files")
		
		# Set title field based on file type
		if self.file_type == "Individual":
			self.customer_name = self.customer_name
		else:
			self.customer_name = self.company_name
	
	def on_submit(self):
		"""On submit"""
		# Create version snapshot if documents exist
		if self.documents:
			self.create_version_snapshot()
	
	def create_version_snapshot(self):
		"""Create a version snapshot of the document"""
		from correspondence.correspondence.utils.version_control import create_document_version
		
		try:
			create_document_version(
				doctype=self.doctype,
				docname=self.name,
				user=frappe.session.user,
				changes_summary=f"File submitted: {self.status}"
			)
		except Exception as e:
			frappe.log_error(f"Version snapshot creation failed: {str(e)}")


@frappe.whitelist()
def get_customer_files_summary():
	"""Get summary of customer files"""
	try:
		summary = {
			"total": frappe.db.count("Customer File"),
			"active": frappe.db.count("Customer File", {"status": "Active"}),
			"individual": frappe.db.count("Customer File", {"file_type": "Individual"}),
			"company": frappe.db.count("Customer File", {"file_type": "Company"}),
			"archived": frappe.db.count("Customer File", {"status": "Archived"})
		}
		
		return {"success": True, "summary": summary}
	except Exception as e:
		frappe.log_error(f"Get customer files summary failed: {str(e)}")
		return {"success": False, "error": str(e)}
