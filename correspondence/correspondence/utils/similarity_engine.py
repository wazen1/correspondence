# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

"""
Similarity Engine Module
Handles document similarity search using embeddings and vector similarity
"""

import frappe

try:
	import numpy as np
	NUMPY_AVAILABLE = True
except ImportError:
	NUMPY_AVAILABLE = False


class SimilarityEngine:
	"""Similarity search engine using sentence transformers"""
	
	def __init__(self):
		self.model = None
		self._load_model()
	
	def _load_model(self):
		"""Load the sentence transformer model"""
		try:
			from sentence_transformers import SentenceTransformer
			# Using a lightweight multilingual model
			self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
		except ImportError:
			frappe.log_error("sentence-transformers not installed. Please install it for similarity search.")
			self.model = None
		except Exception as e:
			frappe.log_error(f"Failed to load similarity model: {str(e)}")
			self.model = None
	
	def generate_embedding(self, text):
		"""
		Generate embedding vector for text
		
		Args:
			text: Input text
		
		Returns:
			Numpy array of embeddings
		"""
		if not self.model:
			return None
		
		if not text or not text.strip():
			return None
		
		try:
			embedding = self.model.encode(text, convert_to_numpy=True)
			return embedding
		except Exception as e:
			frappe.log_error(f"Embedding generation failed: {str(e)}")
			return None
	
	def calculate_similarity(self, text1, text2):
		"""
		Calculate cosine similarity between two texts
		
		Args:
			text1: First text
			text2: Second text
		
		Returns:
			Similarity score (0-1)
		"""
		if not self.model or not NUMPY_AVAILABLE:
			return 0.0
		
		try:
			from sklearn.metrics.pairwise import cosine_similarity
			
			emb1 = self.generate_embedding(text1)
			emb2 = self.generate_embedding(text2)
			
			if emb1 is None or emb2 is None:
				return 0.0
			
			similarity = cosine_similarity([emb1], [emb2])[0][0]
			return float(similarity)
		
		except ImportError:
			frappe.log_error("scikit-learn not installed. Cannot calculate similarity.")
			return 0.0
		except Exception as e:
			frappe.log_error(f"Similarity calculation failed: {str(e)}")
			return 0.0


def find_similar_letters(doctype, current_doc, search_text, limit=10, threshold=0.3):
	"""
	Find similar letters based on content similarity
	
	Args:
		doctype: DocType to search (Incoming Letter or Outgoing Letter)
		current_doc: Current document name (to exclude from results)
		search_text: Text to search for similar documents
		limit: Maximum number of results
		threshold: Minimum similarity threshold (0-1)
	
	Returns:
		List of similar documents with scores
	"""
	if not search_text or not search_text.strip():
		return []
	
	try:
		engine = SimilarityEngine()
		
		if not engine.model:
			# Fallback to simple keyword matching
			return find_similar_by_keywords(doctype, current_doc, search_text, limit)
		
		# Get current document embedding
		current_embedding = engine.generate_embedding(search_text)
		
		if current_embedding is None:
			return []
		
		# Get all documents of the same type
		if doctype == "Incoming Letter":
			documents = frappe.get_all(
				"Incoming Letter",
				filters={"name": ["!=", current_doc]},
				fields=["name", "subject", "summary", "ocr_text", "sender"]
			)
		else:
			documents = frappe.get_all(
				"Outgoing Letter",
				filters={"name": ["!=", current_doc]},
				fields=["name", "subject", "body_text", "ocr_text", "recipient"]
			)
		
		# Calculate similarity for each document
		results = []
		for doc in documents:
			# Build search text for comparison
			if doctype == "Incoming Letter":
				doc_text = f"{doc.get('subject', '')} {doc.get('summary', '')} {doc.get('ocr_text', '')}"
			else:
				doc_text = f"{doc.get('subject', '')} {doc.get('body_text', '')} {doc.get('ocr_text', '')}"
			
			if not doc_text.strip():
				continue
			
			# Calculate similarity
			similarity = engine.calculate_similarity(search_text, doc_text)
			
			if similarity >= threshold:
				results.append({
					"doctype": doctype,
					"name": doc.get("name"),
					"score": round(similarity, 3),
					"subject": doc.get("subject", ""),
					"sender_recipient": doc.get("sender") if doctype == "Incoming Letter" else doc.get("recipient")
				})
		
		# Sort by similarity score (descending) and limit results
		results.sort(key=lambda x: x["score"], reverse=True)
		return results[:limit]
	
	except Exception as e:
		frappe.log_error(f"Similarity search failed: {str(e)}")
		return []


def find_similar_by_keywords(doctype, current_doc, search_text, limit=10):
	"""
	Fallback method: Find similar documents using keyword matching
	
	Args:
		doctype: DocType to search
		current_doc: Current document name
		search_text: Search text
		limit: Maximum results
	
	Returns:
		List of similar documents
	"""
	try:
		# Extract keywords (simple approach: split by space and filter)
		keywords = [word.lower() for word in search_text.split() if len(word) > 3]
		
		if not keywords:
			return []
		
		# Build search query
		search_query = " ".join(keywords[:5])  # Use top 5 keywords
		
		if doctype == "Incoming Letter":
			documents = frappe.get_all(
				"Incoming Letter",
				filters={
					"name": ["!=", current_doc],
					"subject": ["like", f"%{search_query}%"]
				},
				fields=["name", "subject", "sender"],
				limit=limit
			)
		else:
			documents = frappe.get_all(
				"Outgoing Letter",
				filters={
					"name": ["!=", current_doc],
					"subject": ["like", f"%{search_query}%"]
				},
				fields=["name", "subject", "recipient"],
				limit=limit
			)
		
		# Format results
		results = []
		for doc in documents:
			results.append({
				"doctype": doctype,
				"name": doc.get("name"),
				"score": 0.5,  # Default score for keyword matching
				"subject": doc.get("subject", ""),
				"sender_recipient": doc.get("sender") if doctype == "Incoming Letter" else doc.get("recipient")
			})
		
		return results
	
	except Exception as e:
		frappe.log_error(f"Keyword search failed: {str(e)}")
		return []


@frappe.whitelist()
def get_similar_documents(doctype, docname):
	"""
	API endpoint to get similar documents
	
	Args:
		doctype: Document type
		docname: Document name
	
	Returns:
		List of similar documents
	"""
	try:
		doc = frappe.get_doc(doctype, docname)
		
		# Build search text
		if doctype == "Incoming Letter":
			search_text = f"{doc.subject or ''} {doc.summary or ''} {doc.ocr_text or ''}"
		elif doctype == "Outgoing Letter":
			search_text = f"{doc.subject or ''} {doc.body_text or ''} {doc.ocr_text or ''}"
		else:
			return {"success": False, "error": "Unsupported doctype"}
		
		# Find similar documents
		similar = find_similar_letters(doctype, docname, search_text)
		
		return {"success": True, "documents": similar}
	
	except Exception as e:
		frappe.log_error(f"Get similar documents API failed: {str(e)}")
		return {"success": False, "error": str(e)}
