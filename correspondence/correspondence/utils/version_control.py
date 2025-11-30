# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

"""
Version Control Module
Handles document versioning, preserving originals, and managing working copies
"""

import frappe
from frappe.utils import now
import shutil
import os


def create_document_version(doctype, docname, user=None, changes_summary=""):
	"""
	Create a new version of a document
	
	Args:
		doctype: Document type
		docname: Document name
		user: User creating the version
		changes_summary: Summary of changes
	
	Returns:
		Document Version name
	"""
	if not user:
		user = frappe.session.user
	
	try:
		# Get the document
		doc = frappe.get_doc(doctype, docname)
		
		# Get attachments
		attachments = doc.get("attachments") if hasattr(doc, "attachments") else []
		
		if not attachments:
			return None
		
		# Create version for each attachment
		for attachment in attachments:
			if attachment.file and attachment.is_original:
				# Create version record
				version = frappe.new_doc("Document Version")
				version.reference_doctype = doctype
				version.reference_name = docname
				version.editor = user
				version.created_on = now()
				version.changes_summary = changes_summary
				version.original_file = attachment.file
				version.is_current = 1
				
				# Save version
				version.insert(ignore_permissions=True)
				
				return version.name
		
		return None
	
	except Exception as e:
		frappe.log_error(f"Version creation failed: {str(e)}")
		return None


def get_working_copy(doctype, docname, attachment_name):
	"""
	Get or create a working copy of a document for editing
	
	Args:
		doctype: Document type
		docname: Document name
		attachment_name: Attachment file name
	
	Returns:
		Working copy file URL
	"""
	try:
		# Get current version
		current_version = frappe.get_all(
			"Document Version",
			filters={
				"reference_doctype": doctype,
				"reference_name": docname,
				"is_current": 1
			},
			fields=["name", "original_file", "working_copy"],
			limit=1
		)
		
		if not current_version:
			return None
		
		version = frappe.get_doc("Document Version", current_version[0].name)
		
		# If working copy exists, return it
		if version.working_copy:
			return version.working_copy
		
		# Create working copy by copying original
		if version.original_file:
			original_path = frappe.get_site_path('public', version.original_file.lstrip('/'))
			
			if os.path.exists(original_path):
				# Create working copy filename
				base_name = os.path.basename(original_path)
				name, ext = os.path.splitext(base_name)
				working_copy_name = f"{name}_working_copy{ext}"
				
				# Copy file
				working_copy_dir = os.path.dirname(original_path)
				working_copy_path = os.path.join(working_copy_dir, working_copy_name)
				
				shutil.copy2(original_path, working_copy_path)
				
				# Update version with working copy
				working_copy_url = version.original_file.replace(base_name, working_copy_name)
				version.working_copy = working_copy_url
				version.save(ignore_permissions=True)
				
				return working_copy_url
		
		return None
	
	except Exception as e:
		frappe.log_error(f"Getting working copy failed: {str(e)}")
		return None


def save_new_version(doctype, docname, file_url, user=None, changes_summary=""):
	"""
	Save a new version of a document (when working copy is modified)
	
	Args:
		doctype: Document type
		docname: Document name
		file_url: URL of the modified file
		user: User saving the version
		changes_summary: Summary of changes
	
	Returns:
		New version name
	"""
	if not user:
		user = frappe.session.user
	
	try:
		# Mark current version as not current
		frappe.db.sql("""
			UPDATE `tabDocument Version`
			SET is_current = 0
			WHERE reference_doctype = %s
			AND reference_name = %s
			AND is_current = 1
		""", (doctype, docname))
		
		# Create new version
		version = frappe.new_doc("Document Version")
		version.reference_doctype = doctype
		version.reference_name = docname
		version.editor = user
		version.created_on = now()
		version.changes_summary = changes_summary
		version.original_file = file_url
		version.is_current = 1
		
		version.insert(ignore_permissions=True)
		
		return version.name
	
	except Exception as e:
		frappe.log_error(f"Saving new version failed: {str(e)}")
		return None


def lock_original_file(file_url):
	"""
	Lock original file to prevent modifications (make read-only)
	
	Args:
		file_url: URL of the file to lock
	
	Returns:
		Success status
	"""
	try:
		file_path = frappe.get_site_path('public', file_url.lstrip('/'))
		
		if os.path.exists(file_path):
			# Make file read-only
			os.chmod(file_path, 0o444)
			return True
		
		return False
	
	except Exception as e:
		frappe.log_error(f"Locking file failed: {str(e)}")
		return False


@frappe.whitelist()
def get_version_history_api(doctype, docname):
	"""
	API endpoint to get version history
	
	Args:
		doctype: Document type
		docname: Document name
	
	Returns:
		List of versions
	"""
	try:
		versions = frappe.get_all(
			"Document Version",
			filters={
				"reference_doctype": doctype,
				"reference_name": docname
			},
			fields=[
				"name", "version_number", "editor", "created_on",
				"changes_summary", "is_current", "original_file", "working_copy"
			],
			order_by="version_number desc"
		)
		
		return {"success": True, "versions": versions}
	
	except Exception as e:
		frappe.log_error(f"Get version history API failed: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def create_working_copy_api(doctype, docname):
	"""
	API endpoint to create a working copy
	
	Args:
		doctype: Document type
		docname: Document name
	
	Returns:
		Working copy URL
	"""
	try:
		doc = frappe.get_doc(doctype, docname)
		
		# Get first attachment
		if doc.attachments and len(doc.attachments) > 0:
			attachment = doc.attachments[0]
			working_copy = get_working_copy(doctype, docname, attachment.file_name)
			
			return {"success": True, "working_copy": working_copy}
		else:
			return {"success": False, "error": "No attachments found"}
	
	except Exception as e:
		frappe.log_error(f"Create working copy API failed: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def save_version_api(doctype, docname, file_url, changes_summary=""):
	"""
	API endpoint to save a new version
	
	Args:
		doctype: Document type
		docname: Document name
		file_url: Modified file URL
		changes_summary: Summary of changes
	
	Returns:
		New version name
	"""
	try:
		version_name = save_new_version(doctype, docname, file_url, changes_summary=changes_summary)
		
		if version_name:
			return {"success": True, "version": version_name}
		else:
			return {"success": False, "error": "Failed to create version"}
	
	except Exception as e:
		frappe.log_error(f"Save version API failed: {str(e)}")
		return {"success": False, "error": str(e)}
