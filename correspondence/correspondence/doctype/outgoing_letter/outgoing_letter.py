# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class OutgoingLetter(Document):
	def validate(self):
		"""Validate the document"""
		# Set date_sent when status changes to Sent
		if self.status == "Sent" and not self.date_sent:
			self.date_sent = frappe.utils.today()
	
	def after_insert(self):
		"""After inserting the document"""
		# Process OCR for all attachments
		self.process_ocr_for_attachments()
		
		# Find and link related documents
		self.find_related_documents()
		
		# Auto-categorize based on topics
		self.auto_categorize()
	
	def on_update(self):
		"""On update of the document"""
		# If status changed, trigger workflow actions
		if self.has_value_changed('status'):
			self.on_status_change()
		
		# Process new attachments for OCR
		self.process_ocr_for_attachments()
	
	def on_submit(self):
		"""On submit"""
		# Create version snapshot
		self.create_version_snapshot()
	
	def process_ocr_for_attachments(self):
		"""Process OCR for all attachments that haven't been processed"""
		if not self.attachments:
			return
		
		from correspondence.correspondence.utils.ocr_processor import extract_text_from_file
		
		ocr_texts = []
		for attachment in self.attachments:
			if not attachment.ocr_extracted and attachment.file:
				try:
					# Get file path
					file_path = frappe.get_site_path('public', attachment.file.lstrip('/'))
					
					# Extract text
					ocr_text = extract_text_from_file(file_path)
					
					# Update attachment
					attachment.ocr_text = ocr_text
					attachment.ocr_extracted = 1
					
					# Collect all OCR texts
					if ocr_text:
						ocr_texts.append(ocr_text)
				except Exception as e:
					frappe.log_error(f"OCR processing failed for {attachment.file_name}: {str(e)}")
		
		# Update main OCR text field
		if ocr_texts:
			self.ocr_text = "\n\n---\n\n".join(ocr_texts)
	
	def find_related_documents(self):
		"""Find and link related documents using multiple strategies (topic, date, recipient, subject)"""
		from correspondence.correspondence.utils.auto_relation_finder import find_all_related_documents
		
		try:
			# Find all related documents using comprehensive search
			related_docs = find_all_related_documents(self, "Outgoing Letter")
			
			# Clear existing auto-generated relations (keep manual ones)
			self.related_documents = [
				d for d in self.related_documents 
				if d.relation_type == "Manual"
			]
			
			# Add new related documents
			for doc in related_docs:
				self.append('related_documents', {
					'document_type': doc.get('doctype'),
					'document_name': doc.get('name'),
					'similarity_score': doc.get('score'),
					'relation_type': 'Auto',
					'notes': doc.get('relation_reason', '')
				})
		except Exception as e:
			frappe.log_error(f"Finding related documents failed: {str(e)}")
	
	def auto_categorize(self):
		"""Auto-categorize based on topic rules"""
		from correspondence.correspondence.utils.topic_classifier import classify_document
		
		try:
			# Build text for classification
			text = f"{self.subject or ''} {self.body_text or ''} {self.ocr_text or ''}"
			
			if not text.strip():
				return
			
			# Get suggested topics
			suggested_topics = classify_document(text)
			
			# Add topics if not already present
			existing_topics = [t.topic for t in self.topics] if self.topics else []
			
			for topic in suggested_topics:
				if topic not in existing_topics:
					self.append('topics', {'topic': topic})
		except Exception as e:
			frappe.log_error(f"Auto-categorization failed: {str(e)}")
	
	def on_status_change(self):
		"""Handle status change"""
		# If archived, lock the document
		if self.status == "Archived":
			self.archive_document()
		
		# If sent, record the date
		if self.status == "Sent" and not self.date_sent:
			self.date_sent = frappe.utils.today()
	
	def archive_document(self):
		"""Archive the document"""
		if self.is_archived:
			return
		
		# Generate archive number
		self.archive_number = self.generate_archive_number()
		self.is_archived = 1
		self.archived_on = now()
		self.archived_by = frappe.session.user
		
		# Create final version snapshot
		self.create_version_snapshot()
	
	def generate_archive_number(self):
		"""Generate unique archive number"""
		from frappe.model.naming import make_autoname
		return make_autoname("ARCH-.YYYY.-.MM.-.#####")
	
	def create_version_snapshot(self):
		"""Create a version snapshot of the document"""
		from correspondence.correspondence.utils.version_control import create_document_version
		
		try:
			create_document_version(
				doctype=self.doctype,
				docname=self.name,
				user=frappe.session.user,
				changes_summary=f"Status: {self.status}"
			)
		except Exception as e:
			frappe.log_error(f"Version snapshot creation failed: {str(e)}")


@frappe.whitelist()
def get_letter_preview(letter_name):
	"""Get letter preview data including attachments and related docs"""
	letter = frappe.get_doc("Outgoing Letter", letter_name)
	
	return {
		"letter": letter.as_dict(),
		"attachments": [att.as_dict() for att in letter.attachments] if letter.attachments else [],
		"related_documents": [rel.as_dict() for rel in letter.related_documents] if letter.related_documents else [],
		"topics": [t.as_dict() for t in letter.topics] if letter.topics else []
	}
