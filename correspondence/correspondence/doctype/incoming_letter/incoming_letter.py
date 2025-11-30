# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, get_datetime
from datetime import datetime, timedelta


class IncomingLetter(Document):
	def before_insert(self):
		"""Before inserting a new letter"""
		# Set default status if not set
		if not self.status:
			self.status = "New"
		
		# Set department from recipient_department if not set
		if not self.department and self.recipient_department:
			self.department = self.recipient_department
	
	def validate(self):
		"""Validate the document"""
		# Update SLA status
		self.update_sla_status()
		
		# Auto-assign based on department if not assigned
		if not self.assigned_to and self.recipient_department:
			self.auto_assign_to_department()
	
	def after_insert(self):
		"""After inserting the document"""
		# Process OCR for all attachments
		self.process_ocr_for_attachments()
		
		# Find and link related documents
		self.find_related_documents()
		
		# Auto-categorize based on topics
		self.auto_categorize()
		
		# Send notification to assigned user
		if self.assigned_to:
			self.send_assignment_notification()
	
	def on_update(self):
		"""On update of the document"""
		# If status changed, trigger workflow actions
		if self.has_value_changed('status'):
			self.on_status_change()
		
		# If assigned_to changed, send notification
		if self.has_value_changed('assigned_to'):
			self.send_assignment_notification()
		
		# Process new attachments for OCR
		self.process_ocr_for_attachments()
	
	def on_submit(self):
		"""On submit"""
		# Create version snapshot
		self.create_version_snapshot()
	
	def update_sla_status(self):
		"""Update SLA status based on due date"""
		if not self.due_date:
			return
		
		today = get_datetime()
		due_date = get_datetime(self.due_date)
		
		if self.status in ["Completed", "Archived"]:
			self.sla_status = "On Track"
		elif today > due_date:
			self.sla_status = "Overdue"
		elif (due_date - today).days <= 2:
			self.sla_status = "At Risk"
		else:
			self.sla_status = "On Track"
	
	def auto_assign_to_department(self):
		"""Auto-assign to department head or default user"""
		try:
			# Get department head
			dept = frappe.get_doc("Department", self.recipient_department)
			if hasattr(dept, 'department_head') and dept.department_head:
				self.assigned_to = dept.department_head
		except Exception as e:
			frappe.log_error(f"Auto-assignment failed: {str(e)}")
	
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
		"""Find and link related documents using multiple strategies (topic, date, sender, subject)"""
		from correspondence.correspondence.utils.auto_relation_finder import find_all_related_documents
		
		try:
			# Find all related documents using comprehensive search
			related_docs = find_all_related_documents(self, "Incoming Letter")
			
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
			text = f"{self.subject or ''} {self.summary or ''} {self.ocr_text or ''}"
			
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
	
	def send_assignment_notification(self):
		"""Send email notification to assigned user"""
		if not self.assigned_to:
			return
		
		try:
			# Create notification
			notification = frappe.new_doc("Notification Log")
			notification.subject = f"New Letter Assigned: {self.subject}"
			notification.for_user = self.assigned_to
			notification.type = "Alert"
			notification.document_type = self.doctype
			notification.document_name = self.name
			notification.email_content = f"""
				<p>A new incoming letter has been assigned to you:</p>
				<ul>
					<li><strong>Letter Number:</strong> {self.letter_number}</li>
					<li><strong>Sender:</strong> {self.sender}</li>
					<li><strong>Subject:</strong> {self.subject}</li>
					<li><strong>Priority:</strong> {self.priority}</li>
					<li><strong>Due Date:</strong> {self.due_date or 'Not set'}</li>
				</ul>
				<p>Please review and take necessary action.</p>
			"""
			notification.insert(ignore_permissions=True)
			
			# Send email
			frappe.sendmail(
				recipients=[self.assigned_to],
				subject=f"New Letter Assigned: {self.subject}",
				message=notification.email_content,
				reference_doctype=self.doctype,
				reference_name=self.name
			)
		except Exception as e:
			frappe.log_error(f"Sending notification failed: {str(e)}")
	
	def on_status_change(self):
		"""Handle status change"""
		# If archived, lock the document
		if self.status == "Archived":
			self.archive_document()
		
		# Send status update notification
		if self.assigned_to:
			try:
				frappe.sendmail(
					recipients=[self.assigned_to],
					subject=f"Letter Status Updated: {self.subject}",
					message=f"""
						<p>The status of letter <strong>{self.letter_number}</strong> has been updated to <strong>{self.status}</strong>.</p>
						<p><strong>Subject:</strong> {self.subject}</p>
					""",
					reference_doctype=self.doctype,
					reference_name=self.name
				)
			except Exception as e:
				frappe.log_error(f"Status notification failed: {str(e)}")
	
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
		
		# Update permissions to read-only (except for Administrator)
		self.set_archived_permissions()
	
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
	
	def set_archived_permissions(self):
		"""Set read-only permissions for archived documents"""
		# This is handled by permission rules in the doctype
		# Archived documents should only be editable by System Manager
		pass


@frappe.whitelist()
def get_letter_preview(letter_name):
	"""Get letter preview data including attachments and related docs"""
	letter = frappe.get_doc("Incoming Letter", letter_name)
	
	return {
		"letter": letter.as_dict(),
		"attachments": [att.as_dict() for att in letter.attachments] if letter.attachments else [],
		"related_documents": [rel.as_dict() for rel in letter.related_documents] if letter.related_documents else [],
		"topics": [t.as_dict() for t in letter.topics] if letter.topics else []
	}


@frappe.whitelist()
def bulk_archive(letter_names):
	"""Bulk archive letters"""
	import json
	
	if isinstance(letter_names, str):
		letter_names = json.loads(letter_names)
	
	results = {"success": [], "failed": []}
	
	for letter_name in letter_names:
		try:
			letter = frappe.get_doc("Incoming Letter", letter_name)
			letter.status = "Archived"
			letter.archive_document()
			letter.save(ignore_permissions=True)
			results["success"].append(letter_name)
		except Exception as e:
			results["failed"].append({"name": letter_name, "error": str(e)})
			frappe.log_error(f"Bulk archive failed for {letter_name}: {str(e)}")
	
	return results
