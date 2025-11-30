# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class ArchiveLocation(Document):
	def validate(self):
		"""Validate archive location"""
		# Calculate available space
		self.available_space = self.capacity - self.current_count
		
		# Ensure available space is not negative
		if self.available_space < 0:
			frappe.throw("Current count cannot exceed capacity")
	
	def update_count(self):
		"""Update current count based on archived documents"""
		count = frappe.db.count("Incoming Letter", {"archive_location": self.name, "is_archived": 1})
		count += frappe.db.count("Outgoing Letter", {"archive_location": self.name, "is_archived": 1})
		
		self.current_count = count
		self.available_space = self.capacity - self.current_count
		self.save()
