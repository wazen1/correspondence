# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

"""
Topic Classifier Module
Handles automatic topic/category classification for documents
"""

import frappe


def classify_document(text):
	"""
	Classify document into topics based on keywords and rules
	
	Args:
		text: Document text (subject + body + OCR text)
	
	Returns:
		List of topic names
	"""
	if not text or not text.strip():
		return []
	
	try:
		# Get all topics with auto-categorization enabled
		topics = frappe.get_all(
			"Topic",
			filters={"enable_auto_categorization": 1},
			fields=["name", "keywords", "auto_categorization_rules"]
		)
		
		if not topics:
			return []
		
		matched_topics = []
		text_lower = text.lower()
		
		for topic in topics:
			# Check keyword matching
			if topic.get("keywords"):
				keywords = [kw.strip().lower() for kw in topic.keywords.split(",")]
				
				# Check if any keyword is in the text
				for keyword in keywords:
					if keyword and keyword in text_lower:
						matched_topics.append(topic.name)
						break  # Topic matched, no need to check other keywords
			
			# Check advanced rules (if any)
			if topic.get("auto_categorization_rules"):
				try:
					if check_advanced_rules(text, topic.auto_categorization_rules):
						if topic.name not in matched_topics:
							matched_topics.append(topic.name)
				except Exception as e:
					frappe.log_error(f"Advanced rule check failed for topic {topic.name}: {str(e)}")
		
		return matched_topics
	
	except Exception as e:
		frappe.log_error(f"Document classification failed: {str(e)}")
		return []


def check_advanced_rules(text, rules_json):
	"""
	Check advanced categorization rules (JSON-based)
	
	Args:
		text: Document text
		rules_json: JSON rules string
	
	Returns:
		True if rules match, False otherwise
	"""
	import json
	
	try:
		rules = json.loads(rules_json)
		
		# Example rule structure:
		# {
		#     "operator": "AND" or "OR",
		#     "conditions": [
		#         {"field": "text", "operator": "contains", "value": "keyword"},
		#         {"field": "text", "operator": "regex", "pattern": "pattern"}
		#     ]
		# }
		
		if not isinstance(rules, dict):
			return False
		
		operator = rules.get("operator", "AND")
		conditions = rules.get("conditions", [])
		
		if not conditions:
			return False
		
		results = []
		text_lower = text.lower()
		
		for condition in conditions:
			field = condition.get("field")
			cond_operator = condition.get("operator")
			value = condition.get("value", "").lower()
			
			if field == "text":
				if cond_operator == "contains":
					results.append(value in text_lower)
				elif cond_operator == "not_contains":
					results.append(value not in text_lower)
				elif cond_operator == "starts_with":
					results.append(text_lower.startswith(value))
				elif cond_operator == "ends_with":
					results.append(text_lower.endswith(value))
				elif cond_operator == "regex":
					import re
					pattern = condition.get("pattern", "")
					results.append(bool(re.search(pattern, text, re.IGNORECASE)))
		
		# Apply operator
		if operator == "AND":
			return all(results)
		elif operator == "OR":
			return any(results)
		else:
			return False
	
	except Exception as e:
		frappe.log_error(f"Advanced rules check failed: {str(e)}")
		return False


@frappe.whitelist()
def classify_document_api(doctype, docname):
	"""
	API endpoint to classify a document
	
	Args:
		doctype: Document type
		docname: Document name
	
	Returns:
		List of suggested topics
	"""
	try:
		doc = frappe.get_doc(doctype, docname)
		
		# Build text for classification
		if doctype == "Incoming Letter":
			text = f"{doc.subject or ''} {doc.summary or ''} {doc.ocr_text or ''}"
		elif doctype == "Outgoing Letter":
			text = f"{doc.subject or ''} {doc.body_text or ''} {doc.ocr_text or ''}"
		else:
			return {"success": False, "error": "Unsupported doctype"}
		
		# Classify
		topics = classify_document(text)
		
		return {"success": True, "topics": topics}
	
	except Exception as e:
		frappe.log_error(f"Classify document API failed: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def apply_topics_to_document(doctype, docname, topics):
	"""
	Apply topics to a document
	
	Args:
		doctype: Document type
		docname: Document name
		topics: List of topic names (JSON string or list)
	
	Returns:
		Success status
	"""
	import json
	
	if isinstance(topics, str):
		topics = json.loads(topics)
	
	try:
		doc = frappe.get_doc(doctype, docname)
		
		# Get existing topics
		existing_topics = [t.topic for t in doc.topics] if doc.topics else []
		
		# Add new topics
		for topic in topics:
			if topic not in existing_topics:
				doc.append('topics', {'topic': topic})
		
		# Save document
		doc.save(ignore_permissions=True)
		
		return {"success": True, "message": f"Applied {len(topics)} topics"}
	
	except Exception as e:
		frappe.log_error(f"Apply topics failed: {str(e)}")
		return {"success": False, "error": str(e)}
