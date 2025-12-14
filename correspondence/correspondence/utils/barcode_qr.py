"""
Barcode and QR Code Generation for Correspondence App
Generates barcodes and QR codes for document tracking
"""

import frappe
from frappe import _
import qrcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
import json
from datetime import datetime


class BarcodeQRGenerator:
	"""Generates barcodes and QR codes for documents"""
	
	def __init__(self):
		self.qr_version = 1
		self.qr_box_size = 10
		self.qr_border = 4
	
	def generate_qr_code(self, doctype, docname, include_metadata=True):
		"""
		Generate QR code for a document
		
		Args:
			doctype: Document type
			docname: Document name
			include_metadata: Include additional metadata in QR code
			
		Returns:
			str: Base64 encoded QR code image
		"""
		try:
			# Get document
			doc = frappe.get_doc(doctype, docname)
			
			# Prepare data for QR code
			qr_data = self._prepare_qr_data(doc, include_metadata)
			
			# Create QR code
			qr = qrcode.QRCode(
				version=self.qr_version,
				error_correction=qrcode.constants.ERROR_CORRECT_H,
				box_size=self.qr_box_size,
				border=self.qr_border,
			)
			
			qr.add_data(qr_data)
			qr.make(fit=True)
			
			# Create image
			img = qr.make_image(fill_color="black", back_color="white")
			
			# Convert to base64
			buffered = BytesIO()
			img.save(buffered, format="PNG")
			img_str = base64.b64encode(buffered.getvalue()).decode()
			
			# Store QR code reference
			self._store_qr_code(doctype, docname, img_str, qr_data)
			
			return img_str
			
		except Exception as e:
			frappe.log_error(f"Error generating QR code: {str(e)}", "QR Code Error")
			frappe.throw(_("Failed to generate QR code: {0}").format(str(e)))
	
	def generate_barcode(self, doctype, docname, barcode_type='code128'):
		"""
		Generate barcode for a document
		
		Args:
			doctype: Document type
			docname: Document name
			barcode_type: Type of barcode (code128, ean13, etc.)
			
		Returns:
			str: Base64 encoded barcode image
		"""
		try:
			# Get document
			doc = frappe.get_doc(doctype, docname)
			
			# Generate barcode data
			barcode_data = self._prepare_barcode_data(doc)
			
			# Create barcode
			barcode_class = barcode.get_barcode_class(barcode_type)
			barcode_instance = barcode_class(barcode_data, writer=ImageWriter())
			
			# Generate image
			buffered = BytesIO()
			barcode_instance.write(buffered, options={
				'module_width': 0.2,
				'module_height': 15.0,
				'quiet_zone': 6.5,
				'font_size': 10,
				'text_distance': 5.0,
				'write_text': True
			})
			
			# Convert to base64
			img_str = base64.b64encode(buffered.getvalue()).decode()
			
			# Store barcode reference
			self._store_barcode(doctype, docname, img_str, barcode_data, barcode_type)
			
			return img_str
			
		except Exception as e:
			frappe.log_error(f"Error generating barcode: {str(e)}", "Barcode Error")
			frappe.throw(_("Failed to generate barcode: {0}").format(str(e)))
	
	def _prepare_qr_data(self, doc, include_metadata):
		"""
		Prepare data to encode in QR code
		
		Args:
			doc: Frappe document
			include_metadata: Include additional metadata
			
		Returns:
			str: JSON string with document data
		"""
		data = {
			"doctype": doc.doctype,
			"name": doc.name,
			"url": frappe.utils.get_url(doc.get_url())
		}
		
		if include_metadata:
			# Add specific fields based on doctype
			if doc.doctype in ["Incoming Letter", "Outgoing Letter"]:
				data.update({
					"subject": getattr(doc, "subject", ""),
					"date": str(getattr(doc, "date_received", getattr(doc, "date_sent", ""))),
					"status": getattr(doc, "status", ""),
					"reference_number": getattr(doc, "reference_number", ""),
					"archive_number": getattr(doc, "archive_number", "")
				})
		
		return json.dumps(data)
	
	def _prepare_barcode_data(self, doc):
		"""
		Prepare data for barcode
		
		Args:
			doc: Frappe document
			
		Returns:
			str: Barcode data string
		"""
		# Use archive number if available, otherwise use document name
		if hasattr(doc, 'archive_number') and doc.archive_number:
			return doc.archive_number
		elif hasattr(doc, 'reference_number') and doc.reference_number:
			return doc.reference_number
		else:
			# Generate a numeric ID from document name
			return str(abs(hash(doc.name)) % (10 ** 12))
	
	def _store_qr_code(self, doctype, docname, qr_image, qr_data):
		"""
		Store QR code reference in database
		
		Args:
			doctype: Document type
			docname: Document name
			qr_image: Base64 encoded image
			qr_data: Data encoded in QR code
		"""
		try:
			# Check if record exists
			if frappe.db.exists("Document QR Code", {"document_type": doctype, "document_name": docname}):
				qr_doc = frappe.get_doc("Document QR Code", {"document_type": doctype, "document_name": docname})
				qr_doc.qr_image = qr_image
				qr_doc.qr_data = qr_data
				qr_doc.generated_date = datetime.now()
				qr_doc.save(ignore_permissions=True)
			else:
				qr_doc = frappe.new_doc("Document QR Code")
				qr_doc.document_type = doctype
				qr_doc.document_name = docname
				qr_doc.qr_image = qr_image
				qr_doc.qr_data = qr_data
				qr_doc.generated_date = datetime.now()
				qr_doc.insert(ignore_permissions=True)
			
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Error storing QR code: {str(e)}", "QR Code Error")
	
	def _store_barcode(self, doctype, docname, barcode_image, barcode_data, barcode_type):
		"""
		Store barcode reference in database
		
		Args:
			doctype: Document type
			docname: Document name
			barcode_image: Base64 encoded image
			barcode_data: Data encoded in barcode
			barcode_type: Type of barcode
		"""
		try:
			# Check if record exists
			if frappe.db.exists("Document Barcode", {"document_type": doctype, "document_name": docname}):
				bc_doc = frappe.get_doc("Document Barcode", {"document_type": doctype, "document_name": docname})
				bc_doc.barcode_image = barcode_image
				bc_doc.barcode_data = barcode_data
				bc_doc.barcode_type = barcode_type
				bc_doc.generated_date = datetime.now()
				bc_doc.save(ignore_permissions=True)
			else:
				bc_doc = frappe.new_doc("Document Barcode")
				bc_doc.document_type = doctype
				bc_doc.document_name = docname
				bc_doc.barcode_image = barcode_image
				bc_doc.barcode_data = barcode_data
				bc_doc.barcode_type = barcode_type
				bc_doc.generated_date = datetime.now()
				bc_doc.insert(ignore_permissions=True)
			
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Error storing barcode: {str(e)}", "Barcode Error")


@frappe.whitelist()
def generate_qr_code_api(doctype, docname, include_metadata=1):
	"""
	API to generate QR code for a document
	
	Args:
		doctype: Document type
		docname: Document name
		include_metadata: Include metadata (1 or 0)
		
	Returns:
		dict: QR code image and data
	"""
	generator = BarcodeQRGenerator()
	include_meta = bool(int(include_metadata))
	
	qr_image = generator.generate_qr_code(doctype, docname, include_meta)
	
	return {
		"success": True,
		"message": _("QR code generated successfully"),
		"qr_image": qr_image,
		"doctype": doctype,
		"docname": docname
	}


@frappe.whitelist()
def generate_barcode_api(doctype, docname, barcode_type='code128'):
	"""
	API to generate barcode for a document
	
	Args:
		doctype: Document type
		docname: Document name
		barcode_type: Type of barcode
		
	Returns:
		dict: Barcode image and data
	"""
	generator = BarcodeQRGenerator()
	
	barcode_image = generator.generate_barcode(doctype, docname, barcode_type)
	
	return {
		"success": True,
		"message": _("Barcode generated successfully"),
		"barcode_image": barcode_image,
		"doctype": doctype,
		"docname": docname
	}


@frappe.whitelist()
def get_qr_code(doctype, docname):
	"""
	Get existing QR code for a document
	
	Args:
		doctype: Document type
		docname: Document name
		
	Returns:
		dict: QR code data
	"""
	qr_record = frappe.db.get_value(
		"Document QR Code",
		{"document_type": doctype, "document_name": docname},
		["qr_image", "qr_data", "generated_date"],
		as_dict=True
	)
	
	if not qr_record:
		return {
			"success": False,
			"message": _("No QR code found. Generate one first.")
		}
	
	return {
		"success": True,
		"qr_image": qr_record.qr_image,
		"qr_data": qr_record.qr_data,
		"generated_date": qr_record.generated_date
	}


@frappe.whitelist()
def get_barcode(doctype, docname):
	"""
	Get existing barcode for a document
	
	Args:
		doctype: Document type
		docname: Document name
		
	Returns:
		dict: Barcode data
	"""
	barcode_record = frappe.db.get_value(
		"Document Barcode",
		{"document_type": doctype, "document_name": docname},
		["barcode_image", "barcode_data", "barcode_type", "generated_date"],
		as_dict=True
	)
	
	if not barcode_record:
		return {
			"success": False,
			"message": _("No barcode found. Generate one first.")
		}
	
	return {
		"success": True,
		"barcode_image": barcode_record.barcode_image,
		"barcode_data": barcode_record.barcode_data,
		"barcode_type": barcode_record.barcode_type,
		"generated_date": barcode_record.generated_date
	}


@frappe.whitelist()
def scan_qr_code(qr_data):
	"""
	Process scanned QR code data
	
	Args:
		qr_data: JSON string from QR code
		
	Returns:
		dict: Document information
	"""
	try:
		data = json.loads(qr_data)
		
		# Verify document exists
		if frappe.db.exists(data.get("doctype"), data.get("name")):
			doc = frappe.get_doc(data.get("doctype"), data.get("name"))
			
			return {
				"success": True,
				"message": _("Document found"),
				"document": {
					"doctype": doc.doctype,
					"name": doc.name,
					"url": doc.get_url()
				}
			}
		else:
			return {
				"success": False,
				"message": _("Document not found")
			}
	except Exception as e:
		frappe.log_error(f"Error scanning QR code: {str(e)}", "QR Code Error")
		return {
			"success": False,
			"message": _("Invalid QR code data")
		}
