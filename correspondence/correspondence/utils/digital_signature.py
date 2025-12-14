"""
Digital Signature Support for Correspondence App
Provides functionality for signing documents and verifying signatures
"""

import frappe
from frappe import _
import hashlib
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import os


class DigitalSignatureManager:
	"""Manages digital signatures for documents"""
	
	def __init__(self):
		self.backend = default_backend()
	
	def generate_key_pair(self, user_email):
		"""
		Generate RSA key pair for a user
		
		Args:
			user_email: Email of the user
			
		Returns:
			dict: Contains private_key and public_key in PEM format
		"""
		try:
			# Generate private key
			private_key = rsa.generate_private_key(
				public_exponent=65537,
				key_size=2048,
				backend=self.backend
			)
			
			# Generate public key
			public_key = private_key.public_key()
			
			# Serialize private key
			private_pem = private_key.private_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PrivateFormat.PKCS8,
				encryption_algorithm=serialization.NoEncryption()
			)
			
			# Serialize public key
			public_pem = public_key.public_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PublicFormat.SubjectPublicKeyInfo
			)
			
			return {
				"private_key": private_pem.decode('utf-8'),
				"public_key": public_pem.decode('utf-8')
			}
			
		except Exception as e:
			frappe.log_error(f"Error generating key pair: {str(e)}", "Digital Signature Error")
			frappe.throw(_("Failed to generate key pair: {0}").format(str(e)))
	
	def sign_document(self, doctype, docname, private_key_pem, user_email):
		"""
		Sign a document using user's private key
		
		Args:
			doctype: Document type
			docname: Document name
			private_key_pem: Private key in PEM format
			user_email: Email of the signer
			
		Returns:
			str: Base64 encoded signature
		"""
		try:
			# Get document
			doc = frappe.get_doc(doctype, docname)
			
			# Create document hash
			doc_hash = self._create_document_hash(doc)
			
			# Load private key
			private_key = serialization.load_pem_private_key(
				private_key_pem.encode('utf-8'),
				password=None,
				backend=self.backend
			)
			
			# Sign the hash
			signature = private_key.sign(
				doc_hash.encode('utf-8'),
				padding.PSS(
					mgf=padding.MGF1(hashes.SHA256()),
					salt_length=padding.PSS.MAX_LENGTH
				),
				hashes.SHA256()
			)
			
			# Encode signature
			signature_b64 = base64.b64encode(signature).decode('utf-8')
			
			# Store signature in database
			self._store_signature(doctype, docname, signature_b64, user_email, doc_hash)
			
			return signature_b64
			
		except Exception as e:
			frappe.log_error(f"Error signing document: {str(e)}", "Digital Signature Error")
			frappe.throw(_("Failed to sign document: {0}").format(str(e)))
	
	def verify_signature(self, doctype, docname, signature_b64, public_key_pem):
		"""
		Verify a document signature
		
		Args:
			doctype: Document type
			docname: Document name
			signature_b64: Base64 encoded signature
			public_key_pem: Public key in PEM format
			
		Returns:
			bool: True if signature is valid
		"""
		try:
			# Get document
			doc = frappe.get_doc(doctype, docname)
			
			# Create document hash
			doc_hash = self._create_document_hash(doc)
			
			# Load public key
			public_key = serialization.load_pem_public_key(
				public_key_pem.encode('utf-8'),
				backend=self.backend
			)
			
			# Decode signature
			signature = base64.b64decode(signature_b64)
			
			# Verify signature
			public_key.verify(
				signature,
				doc_hash.encode('utf-8'),
				padding.PSS(
					mgf=padding.MGF1(hashes.SHA256()),
					salt_length=padding.PSS.MAX_LENGTH
				),
				hashes.SHA256()
			)
			
			return True
			
		except InvalidSignature:
			return False
		except Exception as e:
			frappe.log_error(f"Error verifying signature: {str(e)}", "Digital Signature Error")
			return False
	
	def _create_document_hash(self, doc):
		"""
		Create a hash of the document content
		
		Args:
			doc: Frappe document object
			
		Returns:
			str: SHA256 hash of document
		"""
		# Create a string representation of key fields
		hash_data = {
			"doctype": doc.doctype,
			"name": doc.name,
			"subject": getattr(doc, "subject", ""),
			"body": getattr(doc, "body", ""),
			"modified": str(doc.modified)
		}
		
		# Convert to string and hash
		hash_string = str(hash_data)
		return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
	
	def _store_signature(self, doctype, docname, signature, user_email, doc_hash):
		"""
		Store signature in database
		
		Args:
			doctype: Document type
			docname: Document name
			signature: Base64 encoded signature
			user_email: Email of signer
			doc_hash: Document hash
		"""
		try:
			# Check if signature record exists
			if not frappe.db.exists("Document Signature", {"document_type": doctype, "document_name": docname, "signer": user_email}):
				sig_doc = frappe.new_doc("Document Signature")
				sig_doc.document_type = doctype
				sig_doc.document_name = docname
				sig_doc.signature = signature
				sig_doc.signer = user_email
				sig_doc.document_hash = doc_hash
				sig_doc.signature_date = datetime.now()
				sig_doc.insert(ignore_permissions=True)
				frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Error storing signature: {str(e)}", "Digital Signature Error")


@frappe.whitelist()
def generate_user_keys():
	"""
	Generate key pair for current user
	
	Returns:
		dict: Contains public_key (private key is stored securely)
	"""
	user_email = frappe.session.user
	
	manager = DigitalSignatureManager()
	keys = manager.generate_key_pair(user_email)
	
	# Store keys in User Signature Keys doctype
	# Check if keys exist for this user (using filter in case name is not email)
	existing_name = frappe.db.get_value("User Signature Keys", {"user": user_email})
	
	if existing_name:
		# Update existing keys
		key_doc = frappe.get_doc("User Signature Keys", existing_name)
		key_doc.private_key = keys["private_key"]
		key_doc.public_key = keys["public_key"]
		key_doc.save(ignore_permissions=True)
	else:
		# Create new keys
		key_doc = frappe.new_doc("User Signature Keys")
		key_doc.user = user_email
		key_doc.private_key = keys["private_key"]
		key_doc.public_key = keys["public_key"]
		key_doc.insert(ignore_permissions=True)
	
	frappe.db.commit()
	
	return {
		"success": True,
		"message": _("Keys generated successfully"),
		"public_key": keys["public_key"]
	}


@frappe.whitelist()
def sign_document_api(doctype, docname):
	"""
	Sign a document
	
	Args:
		doctype: Document type
		docname: Document name
		
	Returns:
		dict: Signature details
	"""
	user_email = frappe.session.user
	
	# Get user's private key
	# Check by user field, not just name
	key_doc_name = frappe.db.get_value("User Signature Keys", {"user": user_email})
	
	if not key_doc_name:
		# Auto-generate keys if they don't exist
		generate_user_keys()
		frappe.msgprint(_("New signature keys have been generated for you automatically."))
		# Fetch again after generation
		key_doc_name = frappe.db.get_value("User Signature Keys", {"user": user_email})
	
	if not key_doc_name:
		frappe.throw(_("Failed to generate or retrieve signature keys."))

	key_doc = frappe.get_doc("User Signature Keys", key_doc_name)
	private_key = key_doc.private_key
	
	# Sign document
	manager = DigitalSignatureManager()
	signature = manager.sign_document(doctype, docname, private_key, user_email)
	
	return {
		"success": True,
		"message": _("Document signed successfully"),
		"signature": signature,
		"signer": user_email,
		"timestamp": datetime.now().isoformat()
	}


@frappe.whitelist()
def verify_document_signature(doctype, docname, signer_email=None):
	"""
	Verify document signature
	
	Args:
		doctype: Document type
		docname: Document name
		signer_email: Email of signer (optional, uses current user if not provided)
		
	Returns:
		dict: Verification result
	"""
	if not signer_email:
		signer_email = frappe.session.user
	
	# Get signature
	signature_record = frappe.db.get_value(
		"Document Signature",
		{"document_type": doctype, "document_name": docname, "signer": signer_email},
		["signature", "signature_date"],
		as_dict=True
	)
	
	if not signature_record:
		return {
			"success": False,
			"message": _("No signature found for this document")
		}
	
	# Get public key
	key_doc_name = frappe.db.get_value("User Signature Keys", {"user": signer_email})
	
	if not key_doc_name:
		return {
			"success": False,
			"message": _("Signer's public key not found")
		}
	
	key_doc = frappe.get_doc("User Signature Keys", key_doc_name)
	public_key = key_doc.public_key
	
	# Verify signature
	manager = DigitalSignatureManager()
	is_valid = manager.verify_signature(doctype, docname, signature_record.signature, public_key)
	
	return {
		"success": True,
		"is_valid": is_valid,
		"signer": signer_email,
		"signature_date": signature_record.signature_date,
		"message": _("Signature is valid") if is_valid else _("Signature is invalid")
	}


@frappe.whitelist()
def get_document_signatures(doctype, docname):
	"""
	Get all signatures for a document
	
	Args:
		doctype: Document type
		docname: Document name
		
	Returns:
		list: List of signatures
	"""
	signatures = frappe.get_all(
		"Document Signature",
		filters={"document_type": doctype, "document_name": docname},
		fields=["signer", "signature_date", "document_hash"]
	)
	
	return signatures
