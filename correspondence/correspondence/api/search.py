# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

"""
Search API Module
Provides advanced search functionality for letters
"""

import frappe
from frappe.utils import cstr


@frappe.whitelist()
def search_letters(query, filters=None, doctype=None, limit=50):
	"""
	Full-text search across letters
	
	Args:
		query: Search query string
		filters: Additional filters (JSON string or dict)
		doctype: Specific doctype to search (Incoming Letter / Outgoing Letter)
		limit: Maximum results
	
	Returns:
		Search results
	"""
	import json
	
	if isinstance(filters, str):
		filters = json.loads(filters) if filters else {}
	
	if not filters:
		filters = {}
	
	# Determine which doctypes to search
	doctypes_to_search = []
	if doctype:
		doctypes_to_search = [doctype]
	else:
		doctypes_to_search = ["Incoming Letter", "Outgoing Letter"]
	
	results = []
	
	for dt in doctypes_to_search:
		try:
			# Build search conditions
			conditions = build_search_conditions(query, dt)
			
			# Add user filters
			for key, value in filters.items():
				if key and value:
					conditions.append(f"`{key}` = '{frappe.db.escape(cstr(value))}'")
			
			# Build query
			if dt == "Incoming Letter":
				fields = ["name", "letter_number", "subject", "sender", "date_received", "status", "priority"]
			else:
				fields = ["name", "letter_number", "subject", "recipient", "date_created", "status", "priority"]
			
			where_clause = " AND ".join(conditions) if conditions else "1=1"
			
			sql = f"""
				SELECT {', '.join([f'`{f}`' for f in fields])}
				FROM `tab{dt}`
				WHERE {where_clause}
				ORDER BY modified DESC
				LIMIT {int(limit)}
			"""
			
			docs = frappe.db.sql(sql, as_dict=True)
			
			# Add doctype to results
			for doc in docs:
				doc['doctype'] = dt
				results.append(doc)
		
		except Exception as e:
			frappe.log_error(f"Search failed for {dt}: {str(e)}")
	
	return {"success": True, "results": results, "count": len(results)}


def build_search_conditions(query, doctype):
	"""
	Build search conditions for SQL query
	
	Args:
		query: Search query
		doctype: Document type
	
	Returns:
		List of SQL conditions
	"""
	if not query or not query.strip():
		return []
	
	query = frappe.db.escape(query)
	conditions = []
	
	# Search in multiple fields
	search_fields = []
	
	if doctype == "Incoming Letter":
		search_fields = [
			f"`subject` LIKE '%{query}%'",
			f"`sender` LIKE '%{query}%'",
			f"`summary` LIKE '%{query}%'",
			f"`ocr_text` LIKE '%{query}%'",
			f"`letter_number` LIKE '%{query}%'"
		]
	else:  # Outgoing Letter
		search_fields = [
			f"`subject` LIKE '%{query}%'",
			f"`recipient` LIKE '%{query}%'",
			f"`body_text` LIKE '%{query}%'",
			f"`ocr_text` LIKE '%{query}%'",
			f"`letter_number` LIKE '%{query}%'"
		]
	
	# Combine with OR
	if search_fields:
		conditions.append(f"({' OR '.join(search_fields)})")
	
	return conditions


@frappe.whitelist()
def advanced_search(filters):
	"""
	Advanced search with multiple filters
	
	Args:
		filters: Dictionary of filters (JSON string or dict)
	
	Returns:
		Search results
	"""
	import json
	
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	try:
		doctype = filters.get('doctype', 'Incoming Letter')
		
		# Build filter dict for frappe.get_all
		frappe_filters = {}
		
		if filters.get('department'):
			frappe_filters['department'] = filters['department']
		
		if filters.get('status'):
			frappe_filters['status'] = filters['status']
		
		if filters.get('priority'):
			frappe_filters['priority'] = filters['priority']
		
		if filters.get('date_from') and filters.get('date_to'):
			date_field = 'date_received' if doctype == 'Incoming Letter' else 'date_created'
			frappe_filters[date_field] = ['between', [filters['date_from'], filters['date_to']]]
		
		if filters.get('is_archived') is not None:
			frappe_filters['is_archived'] = filters['is_archived']
		
		# Get results
		results = frappe.get_all(
			doctype,
			filters=frappe_filters,
			fields=['*'],
			limit=filters.get('limit', 100),
			order_by=filters.get('order_by', 'modified desc')
		)
		
		return {"success": True, "results": results, "count": len(results)}
	
	except Exception as e:
		frappe.log_error(f"Advanced search failed: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def search_by_topic(topic_name, limit=50):
	"""
	Search letters by topic
	
	Args:
		topic_name: Topic name
		limit: Maximum results
	
	Returns:
		Letters with this topic
	"""
	try:
		# Search in both incoming and outgoing letters
		results = []
		
		# Incoming letters
		incoming = frappe.db.sql("""
			SELECT DISTINCT il.name, il.letter_number, il.subject, il.sender, 
			       il.date_received, il.status, 'Incoming Letter' as doctype
			FROM `tabIncoming Letter` il
			WHERE il.name IN (
				SELECT parent FROM `tabTopic Link`
				WHERE topic = %s AND parenttype = 'Incoming Letter'
			)
			ORDER BY il.modified DESC
			LIMIT %s
		""", (topic_name, int(limit)), as_dict=True)
		
		results.extend(incoming)
		
		# Outgoing letters
		outgoing = frappe.db.sql("""
			SELECT DISTINCT ol.name, ol.letter_number, ol.subject, ol.recipient,
			       ol.date_created, ol.status, 'Outgoing Letter' as doctype
			FROM `tabOutgoing Letter` ol
			WHERE ol.name IN (
				SELECT parent FROM `tabTopic Link`
				WHERE topic = %s AND parenttype = 'Outgoing Letter'
			)
			ORDER BY ol.modified DESC
			LIMIT %s
		""", (topic_name, int(limit)), as_dict=True)
		
		results.extend(outgoing)
		
		return {"success": True, "results": results, "count": len(results)}
	
	except Exception as e:
		frappe.log_error(f"Search by topic failed: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_search_suggestions(query, limit=10):
	"""
	Get search suggestions based on partial query
	
	Args:
		query: Partial search query
		limit: Maximum suggestions
	
	Returns:
		List of suggestions
	"""
	if not query or len(query) < 2:
		return {"success": True, "suggestions": []}
	
	try:
		query = frappe.db.escape(query)
		suggestions = []
		
		# Get subject suggestions
		subjects = frappe.db.sql(f"""
			SELECT DISTINCT subject
			FROM (
				SELECT subject FROM `tabIncoming Letter` WHERE subject LIKE '%{query}%'
				UNION
				SELECT subject FROM `tabOutgoing Letter` WHERE subject LIKE '%{query}%'
			) as combined
			LIMIT {int(limit)}
		""", as_dict=True)
		
		for s in subjects:
			suggestions.append({
				"type": "subject",
				"value": s.subject
			})
		
		# Get sender/recipient suggestions
		senders = frappe.db.sql(f"""
			SELECT DISTINCT sender as value
			FROM `tabIncoming Letter`
			WHERE sender LIKE '%{query}%'
			LIMIT 5
		""", as_dict=True)
		
		for s in senders:
			suggestions.append({
				"type": "sender",
				"value": s.value
			})
		
		return {"success": True, "suggestions": suggestions[:limit]}
	
	except Exception as e:
		frappe.log_error(f"Get suggestions failed: {str(e)}")
		return {"success": False, "error": str(e)}
