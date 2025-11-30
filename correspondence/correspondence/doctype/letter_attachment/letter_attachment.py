# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import os


class LetterAttachment(Document):
	def before_insert(self):
		"""Set metadata before insert"""
		if self.file:
			# Extract file name from path
			self.file_name = os.path.basename(self.file)
			
			# Get file size and type
			try:
				file_path = frappe.get_site_path('public', self.file.lstrip('/'))
				if os.path.exists(file_path):
					self.file_size = os.path.getsize(file_path)
					
					# Determine file type
					ext = os.path.splitext(self.file_name)[1].lower()
					self.file_type = ext
			except Exception as e:
				frappe.log_error(f"Error getting file metadata: {str(e)}")
		
		# Set uploaded by and on
		self.uploaded_by = frappe.session.user
		self.uploaded_on = frappe.utils.now()
