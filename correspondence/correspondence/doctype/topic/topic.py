# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class Topic(Document):
	def validate(self):
		"""Validate topic"""
		# Prevent circular parent reference
		if self.parent_topic == self.name:
			frappe.throw("Topic cannot be its own parent")
		
		# Check for circular hierarchy
		self.check_circular_hierarchy()
	
	def check_circular_hierarchy(self):
		"""Check for circular hierarchy in parent topics"""
		if not self.parent_topic:
			return
		
		visited = set()
		current = self.parent_topic
		
		while current:
			if current in visited or current == self.name:
				frappe.throw("Circular hierarchy detected in topic structure")
			
			visited.add(current)
			
			try:
				parent_doc = frappe.get_doc("Topic", current)
				current = parent_doc.parent_topic
			except:
				break
