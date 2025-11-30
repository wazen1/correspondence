# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

"""
OCR Processor Module
Handles text extraction from PDF and image files using Tesseract OCR
"""

import frappe
import os


def extract_text_from_file(file_path):
	"""
	Extract text from PDF or image file
	
	Args:
		file_path: Absolute path to the file
	
	Returns:
		Extracted text as string
	"""
	if not os.path.exists(file_path):
		frappe.log_error(f"File not found: {file_path}")
		return ""
	
	file_ext = os.path.splitext(file_path)[1].lower()
	
	try:
		if file_ext == '.pdf':
			return extract_from_pdf(file_path)
		elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
			return extract_from_image(file_path)
		else:
			frappe.log_error(f"Unsupported file type for OCR: {file_ext}")
			return ""
	except Exception as e:
		frappe.log_error(f"OCR extraction failed for {file_path}: {str(e)}")
		return ""


def extract_from_pdf(pdf_path):
	"""
	Convert PDF to images and extract text using OCR
	
	Args:
		pdf_path: Path to PDF file
	
	Returns:
		Extracted text
	"""
	try:
		import pytesseract
		from pdf2image import convert_from_path
		
		# Convert PDF to images
		images = convert_from_path(pdf_path, dpi=300)
		
		# Extract text from each page
		text_parts = []
		for i, image in enumerate(images):
			page_text = pytesseract.image_to_string(image, lang='eng+ara')  # English and Arabic
			if page_text.strip():
				text_parts.append(f"--- Page {i+1} ---\n{page_text}")
		
		return "\n\n".join(text_parts)
	
	except ImportError:
		frappe.log_error("OCR dependencies not installed. Please install: pytesseract, pdf2image")
		return ""
	except Exception as e:
		frappe.log_error(f"PDF OCR failed: {str(e)}")
		return ""


def extract_from_image(image_path):
	"""
	Extract text from image using OCR
	
	Args:
		image_path: Path to image file
	
	Returns:
		Extracted text
	"""
	try:
		import pytesseract
		from PIL import Image
		
		# Open image
		image = Image.open(image_path)
		
		# Extract text (support English and Arabic)
		text = pytesseract.image_to_string(image, lang='eng+ara')
		
		return text
	
	except ImportError:
		frappe.log_error("OCR dependencies not installed. Please install: pytesseract, Pillow")
		return ""
	except Exception as e:
		frappe.log_error(f"Image OCR failed: {str(e)}")
		return ""


@frappe.whitelist()
def process_file_ocr(file_url):
	"""
	API endpoint to process OCR for a file
	
	Args:
		file_url: URL of the file (relative to site)
	
	Returns:
		Extracted text
	"""
	try:
		file_path = frappe.get_site_path('public', file_url.lstrip('/'))
		text = extract_text_from_file(file_path)
		return {"success": True, "text": text}
	except Exception as e:
		frappe.log_error(f"OCR API failed: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def batch_process_ocr(file_urls):
	"""
	Batch process OCR for multiple files
	
	Args:
		file_urls: List of file URLs (JSON string or list)
	
	Returns:
		Dictionary of results
	"""
	import json
	
	if isinstance(file_urls, str):
		file_urls = json.loads(file_urls)
	
	results = {}
	
	for file_url in file_urls:
		try:
			file_path = frappe.get_site_path('public', file_url.lstrip('/'))
			text = extract_text_from_file(file_path)
			results[file_url] = {"success": True, "text": text}
		except Exception as e:
			results[file_url] = {"success": False, "error": str(e)}
	
	return results
