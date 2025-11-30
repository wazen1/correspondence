# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

"""
Auto Relation Finder Module
Automatically finds and links related documents based on multiple criteria:
- Topic matching
- Date proximity
- Subject similarity
- Sender/Recipient matching
"""

import frappe
from frappe.utils import get_datetime, add_days
from datetime import timedelta


def find_all_related_documents(doc, doctype):
	"""
	Find all related documents using multiple strategies
	
	Args:
		doc: The document object (Incoming Letter or Outgoing Letter)
		doctype: The doctype name
	
	Returns:
		List of related documents with scores and relation types
	"""
	related_docs = []
	
	# Strategy 1: Find by Topic
	topic_matches = find_by_topic(doc, doctype)
	related_docs.extend(topic_matches)
	
	# Strategy 2: Find by Date Proximity
	date_matches = find_by_date(doc, doctype)
	related_docs.extend(date_matches)
	
	# Strategy 3: Find by Sender/Recipient
	sender_matches = find_by_sender_recipient(doc, doctype)
	related_docs.extend(sender_matches)
	
	# Strategy 4: Find by Subject Similarity (existing AI-based method)
	subject_matches = find_by_subject_similarity(doc, doctype)
	related_docs.extend(subject_matches)
	
	# Remove duplicates (keep highest score for each document)
	unique_docs = {}
	for doc_info in related_docs:
		key = f"{doc_info['doctype']}::{doc_info['name']}"
		if key not in unique_docs or doc_info['score'] > unique_docs[key]['score']:
			unique_docs[key] = doc_info
	
	# Sort by score descending
	final_results = list(unique_docs.values())
	final_results.sort(key=lambda x: x['score'], reverse=True)
	
	return final_results[:20]  # Return top 20 matches


def find_by_topic(doc, doctype):
	"""
	Find documents with matching topics
	
	Args:
		doc: The document object
		doctype: The doctype name
	
	Returns:
		List of related documents
	"""
	results = []
	
	try:
		# Get topics from current document
		if not hasattr(doc, 'topics') or not doc.topics:
			return results
		
		current_topics = [t.topic for t in doc.topics]
		
		if not current_topics:
			return results
		
		# Search in both Incoming and Outgoing Letters
		for search_doctype in ["Incoming Letter", "Outgoing Letter"]:
			# Skip searching in the same document
			if search_doctype == doctype:
				filters = {"name": ["!=", doc.name]}
			else:
				filters = {}
			
			# Get all documents
			documents = frappe.get_all(
				search_doctype,
				filters=filters,
				fields=["name", "subject", "date_received" if search_doctype == "Incoming Letter" else "date_sent"]
			)
			
			for document in documents:
				# Get topics for this document
				doc_topics = frappe.get_all(
					"Letter Topic",
					filters={"parent": document.name, "parenttype": search_doctype},
					fields=["topic"]
				)
				
				doc_topic_names = [t.topic for t in doc_topics]
				
				# Calculate topic overlap
				common_topics = set(current_topics).intersection(set(doc_topic_names))
				
				if common_topics:
					# Score based on number of common topics
					score = min(0.9, 0.5 + (len(common_topics) * 0.1))
					
					results.append({
						"doctype": search_doctype,
						"name": document.name,
						"score": score,
						"relation_reason": f"Common Topics: {', '.join(common_topics)}"
					})
	
	except Exception as e:
		frappe.log_error(f"Find by topic failed: {str(e)}")
	
	return results


def find_by_date(doc, doctype):
	"""
	Find documents from similar time periods (within 30 days)
	
	Args:
		doc: The document object
		doctype: The doctype name
	
	Returns:
		List of related documents
	"""
	results = []
	
	try:
		# Get the date field based on doctype
		if doctype == "Incoming Letter":
			current_date = doc.date_received
		else:  # Outgoing Letter
			current_date = doc.date_sent or doc.date_created
		
		if not current_date:
			return results
		
		current_date = get_datetime(current_date)
		
		# Define date range (30 days before and after)
		date_from = add_days(current_date, -30)
		date_to = add_days(current_date, 30)
		
		# Search in both Incoming and Outgoing Letters
		for search_doctype in ["Incoming Letter", "Outgoing Letter"]:
			date_field = "date_received" if search_doctype == "Incoming Letter" else "date_sent"
			
			# Skip searching in the same document
			if search_doctype == doctype:
				filters = {
					"name": ["!=", doc.name],
					date_field: ["between", [date_from, date_to]]
				}
			else:
				filters = {
					date_field: ["between", [date_from, date_to]]
				}
			
			# For Outgoing Letter, if date_sent is null, we might want to check date_created
			# But for simplicity, let's stick to the main date field
			
			documents = frappe.get_all(
				search_doctype,
				filters=filters,
				fields=["name", "subject", date_field]
			)
			
			for document in documents:
				doc_date = get_datetime(document.get(date_field))
				
				# Calculate score based on date proximity (closer = higher score)
				days_diff = abs((current_date - doc_date).days)
				score = max(0.3, 0.7 - (days_diff / 30 * 0.4))  # Score from 0.3 to 0.7
				
				results.append({
					"doctype": search_doctype,
					"name": document.name,
					"score": score,
					"relation_reason": f"Date Proximity: {days_diff} days apart"
				})
	
	except Exception as e:
		frappe.log_error(f"Find by date failed: {str(e)}")
	
	return results


def find_by_sender_recipient(doc, doctype):
	"""
	Find documents from/to the same sender/recipient
	
	Args:
		doc: The document object
		doctype: The doctype name
	
	Returns:
		List of related documents
	"""
	results = []
	
	try:
		# Get sender/recipient from current document
		if doctype == "Incoming Letter":
			search_value = doc.sender
			search_field = "sender"
		else:  # Outgoing Letter
			search_value = doc.recipient
			search_field = "recipient"
		
		if not search_value:
			return results
		
		# Search in Incoming Letters by sender
		incoming_filters = {"sender": ["like", f"%{search_value}%"]}
		if doctype == "Incoming Letter":
			incoming_filters["name"] = ["!=", doc.name]
		
		incoming_docs = frappe.get_all(
			"Incoming Letter",
			filters=incoming_filters,
			fields=["name", "subject", "sender"],
			limit=10
		)
		
		for document in incoming_docs:
			results.append({
				"doctype": "Incoming Letter",
				"name": document.name,
				"score": 0.85,
				"relation_reason": f"Same Sender: {document.sender}"
			})
		
		# Search in Outgoing Letters by recipient
		outgoing_filters = {"recipient": ["like", f"%{search_value}%"]}
		if doctype == "Outgoing Letter":
			outgoing_filters["name"] = ["!=", doc.name]
		
		outgoing_docs = frappe.get_all(
			"Outgoing Letter",
			filters=outgoing_filters,
			fields=["name", "subject", "recipient"],
			limit=10
		)
		
		for document in outgoing_docs:
			results.append({
				"doctype": "Outgoing Letter",
				"name": document.name,
				"score": 0.85,
				"relation_reason": f"Same Recipient: {document.recipient}"
			})
	
	except Exception as e:
		frappe.log_error(f"Find by sender/recipient failed: {str(e)}")
	
	return results


def find_by_subject_similarity(doc, doctype):
	"""
	Find documents with similar subjects using AI similarity
	
	Args:
		doc: The document object
		doctype: The doctype name
	
	Returns:
		List of related documents
	"""
	results = []
	
	try:
		from correspondence.correspondence.utils.similarity_engine import find_similar_letters
		
		# Build search text from subject, summary/body, and OCR text
		if doctype == "Incoming Letter":
			search_text = f"{doc.subject or ''} {doc.summary or ''} {doc.ocr_text or ''}"
		else:  # Outgoing Letter
			search_text = f"{doc.subject or ''} {doc.body_text or ''} {doc.ocr_text or ''}"
		
		if not search_text.strip():
			return results
		
		# Find similar documents in the same doctype
		similar_docs = find_similar_letters(
			doctype=doctype,
			current_doc=doc.name,
			search_text=search_text,
			limit=10,
			threshold=0.4
		)
		
		for similar_doc in similar_docs:
			results.append({
				"doctype": similar_doc.get('doctype'),
				"name": similar_doc.get('name'),
				"score": similar_doc.get('score'),
				"relation_reason": f"Content Similarity: {int(similar_doc.get('score') * 100)}%"
			})
		
		# Also search in the opposite doctype
		opposite_doctype = "Outgoing Letter" if doctype == "Incoming Letter" else "Incoming Letter"
		
		similar_opposite = find_similar_letters(
			doctype=opposite_doctype,
			current_doc="",  # No current doc to exclude
			search_text=search_text,
			limit=5,
			threshold=0.5
		)
		
		for similar_doc in similar_opposite:
			results.append({
				"doctype": similar_doc.get('doctype'),
				"name": similar_doc.get('name'),
				"score": similar_doc.get('score'),
				"relation_reason": f"Content Similarity: {int(similar_doc.get('score') * 100)}%"
			})
	
	except Exception as e:
		frappe.log_error(f"Find by subject similarity failed: {str(e)}")
	
	return results


@frappe.whitelist()
def refresh_related_documents(doctype, docname):
	"""
	API endpoint to manually refresh related documents for a document
	
	Args:
		doctype: Document type
		docname: Document name
	
	Returns:
		Success status and updated related documents
	"""
	try:
		doc = frappe.get_doc(doctype, docname)
		
		# Find all related documents
		related_docs = find_all_related_documents(doc, doctype)
		
		# Clear existing auto-generated relations
		doc.related_documents = [
			d for d in doc.related_documents 
			if d.relation_type == "Manual"
		]
		
		# Add new related documents
		for rel_doc in related_docs:
			doc.append('related_documents', {
				'document_type': rel_doc['doctype'],
				'document_name': rel_doc['name'],
				'similarity_score': rel_doc['score'],
				'relation_type': 'Auto',
				'notes': rel_doc.get('relation_reason', '')
			})
		
		# Save the document
		doc.save(ignore_permissions=True)
		
		return {
			"success": True,
			"message": f"Found {len(related_docs)} related documents",
			"related_documents": related_docs
		}
	
	except Exception as e:
		frappe.log_error(f"Refresh related documents failed: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def preview_related_documents(doctype, doc_data):
	"""
	API endpoint to preview related documents for unsaved data
	
	Args:
		doctype: Document type
		doc_data: JSON string of document data
	
	Returns:
		List of related documents
	"""
	import json
	
	try:
		if isinstance(doc_data, str):
			data = json.loads(doc_data)
		else:
			data = doc_data
		
		# Create a temporary document object in memory
		doc = frappe.get_doc(data)
		
		# Find related documents
		related_docs = find_all_related_documents(doc, doctype)
		
		return {
			"success": True,
			"message": f"Found {len(related_docs)} related documents",
			"related_documents": related_docs
		}
	
	except Exception as e:
		frappe.log_error(f"Preview related documents failed: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}
