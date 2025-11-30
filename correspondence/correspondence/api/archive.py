# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

"""
Archive API Module
Handles archiving operations
"""

import frappe
from frappe.utils import now


@frappe.whitelist()
def archive_document(doctype, docname, archive_location=None):
	"""
	Archive a single document
	
	Args:
		doctype: Document type
		docname: Document name
		archive_location: Optional archive location
	
	Returns:
		Success status and archive number
	"""
	try:
		doc = frappe.get_doc(doctype, docname)
		
		# Check if already archived
		if doc.is_archived:
			return {"success": False, "error": "Document is already archived"}
		
		# Generate archive number
		from frappe.model.naming import make_autoname
		archive_number = make_autoname("ARCH-.YYYY.-.MM.-.#####")
		
		# Update document
		doc.is_archived = 1
		doc.archive_number = archive_number
		doc.archived_on = now()
		doc.archived_by = frappe.session.user
		doc.status = "Archived"
		
		if archive_location:
			doc.archive_location = archive_location
		
		doc.save(ignore_permissions=True)
		
		# Update archive location count
		if archive_location:
			update_archive_location_count(archive_location)
		
		return {
			"success": True,
			"archive_number": archive_number,
			"message": f"Document archived successfully with number {archive_number}"
		}
	
	except Exception as e:
		frappe.log_error(f"Archive document failed: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def bulk_archive(documents, archive_location=None):
	"""
	Bulk archive multiple documents
	
	Args:
		documents: List of documents (JSON string or list of dicts with doctype and name)
		archive_location: Optional archive location for all documents
	
	Returns:
		Results summary
	"""
	import json
	
	if isinstance(documents, str):
		documents = json.loads(documents)
	
	results = {
		"success": [],
		"failed": [],
		"total": len(documents)
	}
	
	for doc_info in documents:
		try:
			doctype = doc_info.get('doctype')
			docname = doc_info.get('name')
			
			if not doctype or not docname:
				results['failed'].append({
					"doc": doc_info,
					"error": "Missing doctype or name"
				})
				continue
			
			result = archive_document(doctype, docname, archive_location)
			
			if result.get('success'):
				results['success'].append({
					"doctype": doctype,
					"name": docname,
					"archive_number": result.get('archive_number')
				})
			else:
				results['failed'].append({
					"doctype": doctype,
					"name": docname,
					"error": result.get('error')
				})
		
		except Exception as e:
			results['failed'].append({
				"doc": doc_info,
				"error": str(e)
			})
	
	return results


@frappe.whitelist()
def unarchive_document(doctype, docname):
	"""
	Unarchive a document (Admin only)
	
	Args:
		doctype: Document type
		docname: Document name
	
	Returns:
		Success status
	"""
	try:
		# Check if user is System Manager
		if "System Manager" not in frappe.get_roles():
			return {"success": False, "error": "Only System Manager can unarchive documents"}
		
		doc = frappe.get_doc(doctype, docname)
		
		if not doc.is_archived:
			return {"success": False, "error": "Document is not archived"}
		
		# Update archive location count before unarchiving
		if doc.archive_location:
			update_archive_location_count(doc.archive_location)
		
		# Unarchive
		doc.is_archived = 0
		doc.status = "Completed"  # Reset to completed status
		doc.save(ignore_permissions=True)
		
		return {"success": True, "message": "Document unarchived successfully"}
	
	except Exception as e:
		frappe.log_error(f"Unarchive document failed: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_archive_statistics():
	"""
	Get archive statistics
	
	Returns:
		Statistics about archived documents
	"""
	try:
		stats = {}
		
		# Total archived documents
		stats['total_archived'] = frappe.db.count('Incoming Letter', {'is_archived': 1})
		stats['total_archived'] += frappe.db.count('Outgoing Letter', {'is_archived': 1})
		
		# By department
		stats['by_department'] = frappe.db.sql("""
			SELECT department, COUNT(*) as count
			FROM (
				SELECT department FROM `tabIncoming Letter` WHERE is_archived = 1
				UNION ALL
				SELECT department FROM `tabOutgoing Letter` WHERE is_archived = 1
			) as combined
			WHERE department IS NOT NULL
			GROUP BY department
			ORDER BY count DESC
		""", as_dict=True)
		
		# By location
		stats['by_location'] = frappe.db.sql("""
			SELECT archive_location, COUNT(*) as count
			FROM (
				SELECT archive_location FROM `tabIncoming Letter` WHERE is_archived = 1
				UNION ALL
				SELECT archive_location FROM `tabOutgoing Letter` WHERE is_archived = 1
			) as combined
			WHERE archive_location IS NOT NULL
			GROUP BY archive_location
			ORDER BY count DESC
		""", as_dict=True)
		
		# By year
		stats['by_year'] = frappe.db.sql("""
			SELECT YEAR(archived_on) as year, COUNT(*) as count
			FROM (
				SELECT archived_on FROM `tabIncoming Letter` WHERE is_archived = 1
				UNION ALL
				SELECT archived_on FROM `tabOutgoing Letter` WHERE is_archived = 1
			) as combined
			WHERE archived_on IS NOT NULL
			GROUP BY YEAR(archived_on)
			ORDER BY year DESC
		""", as_dict=True)
		
		return {"success": True, "statistics": stats}
	
	except Exception as e:
		frappe.log_error(f"Get archive statistics failed: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_available_archive_locations():
	"""
	Get archive locations with available space
	
	Returns:
		List of locations with capacity info
	"""
	try:
		locations = frappe.get_all(
			"Archive Location",
			fields=["name", "location_code", "building", "floor", "room", 
			        "shelf", "box", "capacity", "current_count", "available_space"],
			filters={"available_space": [">", 0]},
			order_by="available_space desc"
		)
		
		return {"success": True, "locations": locations}
	
	except Exception as e:
		frappe.log_error(f"Get available locations failed: {str(e)}")
		return {"success": False, "error": str(e)}


def update_archive_location_count(location_name):
	"""
	Update the count of documents in an archive location
	
	Args:
		location_name: Archive location name
	"""
	try:
		location = frappe.get_doc("Archive Location", location_name)
		location.update_count()
	except Exception as e:
		frappe.log_error(f"Update archive location count failed: {str(e)}")


@frappe.whitelist()
def search_archived_documents(filters=None):
	"""
	Search archived documents
	
	Args:
		filters: Search filters (JSON string or dict)
	
	Returns:
		Archived documents
	"""
	import json
	
	if isinstance(filters, str):
		filters = json.loads(filters) if filters else {}
	
	try:
		# Base filter
		base_filter = {"is_archived": 1}
		
		# Add additional filters
		if filters:
			base_filter.update(filters)
		
		# Search in both doctypes
		incoming = frappe.get_all(
			"Incoming Letter",
			filters=base_filter,
			fields=["name", "letter_number", "subject", "sender", "archive_number", 
			        "archive_location", "archived_on", "archived_by"],
			limit=100
		)
		
		outgoing = frappe.get_all(
			"Outgoing Letter",
			filters=base_filter,
			fields=["name", "letter_number", "subject", "recipient", "archive_number",
			        "archive_location", "archived_on", "archived_by"],
			limit=100
		)
		
		# Add doctype to results
		for doc in incoming:
			doc['doctype'] = 'Incoming Letter'
		
		for doc in outgoing:
			doc['doctype'] = 'Outgoing Letter'
		
		results = incoming + outgoing
		
		return {"success": True, "results": results, "count": len(results)}
	
	except Exception as e:
		frappe.log_error(f"Search archived documents failed: {str(e)}")
		return {"success": False, "error": str(e)}
