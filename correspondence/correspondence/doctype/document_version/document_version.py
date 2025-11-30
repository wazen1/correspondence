# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import hashlib
import os


class DocumentVersion(Document):
	def before_insert(self):
		"""Before inserting a new version"""
		# Set version number
		if not self.version_number:
			self.version_number = self.get_next_version_number()
		
		# Set editor
		if not self.editor:
			self.editor = frappe.session.user
		
		# Calculate file hash if file exists
		if self.original_file:
			self.file_hash = self.calculate_file_hash(self.original_file)
	
	def after_insert(self):
		"""After inserting"""
		# Mark all other versions as not current
		if self.is_current:
			self.mark_others_as_old()
	
	def get_next_version_number(self):
		"""Get the next version number for this document"""
		last_version = frappe.db.get_value(
			"Document Version",
			filters={
				"reference_doctype": self.reference_doctype,
				"reference_name": self.reference_name
			},
			fieldname="version_number",
			order_by="version_number desc"
		)
		
		return (last_version or 0) + 1
	
	def calculate_file_hash(self, file_url):
		"""Calculate SHA256 hash of file"""
		try:
			file_path = frappe.get_site_path('public', file_url.lstrip('/'))
			
			if os.path.exists(file_path):
				sha256_hash = hashlib.sha256()
				with open(file_path, "rb") as f:
					for byte_block in iter(lambda: f.read(4096), b""):
						sha256_hash.update(byte_block)
				return sha256_hash.hexdigest()
		except Exception as e:
			frappe.log_error(f"Error calculating file hash: {str(e)}")
		
		return None
	
	def mark_others_as_old(self):
		"""Mark all other versions as not current"""
		frappe.db.sql("""
			UPDATE `tabDocument Version`
			SET is_current = 0
			WHERE reference_doctype = %s
			AND reference_name = %s
			AND name != %s
		""", (self.reference_doctype, self.reference_name, self.name))


@frappe.whitelist()
def compare_versions(version1, version2):
	"""Compare two versions and return differences"""
	v1 = frappe.get_doc("Document Version", version1)
	v2 = frappe.get_doc("Document Version", version2)
	
	return {
		"version1": {
			"number": v1.version_number,
			"editor": v1.editor,
			"created_on": v1.created_on,
			"changes_summary": v1.changes_summary,
			"file_hash": v1.file_hash
		},
		"version2": {
			"number": v2.version_number,
			"editor": v2.editor,
			"created_on": v2.created_on,
			"changes_summary": v2.changes_summary,
			"file_hash": v2.file_hash
		},
		"files_identical": v1.file_hash == v2.file_hash if v1.file_hash and v2.file_hash else None
	}


@frappe.whitelist()
def get_version_history(doctype, docname):
	"""Get all versions for a document"""
	versions = frappe.get_all(
		"Document Version",
		filters={
			"reference_doctype": doctype,
			"reference_name": docname
		},
		fields=["name", "version_number", "editor", "created_on", "changes_summary", "is_current"],
		order_by="version_number desc"
	)
	
	return versions
